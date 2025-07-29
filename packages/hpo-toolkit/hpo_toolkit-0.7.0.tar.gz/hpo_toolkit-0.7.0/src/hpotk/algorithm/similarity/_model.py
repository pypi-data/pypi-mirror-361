import abc
import csv
import typing
from collections import defaultdict
from datetime import datetime

from hpotk.model import TermId, MetadataAware
from hpotk.util import open_text_io_handle_for_writing, open_text_io_handle_for_reading


class AnnotationIcContainer(typing.Mapping[TermId, float], MetadataAware, metaclass=abc.ABCMeta):
    """
    A container for storing information content of item annotations.
    """

    @staticmethod
    def from_mapping(
        data: typing.Mapping[TermId, float],
        metadata: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> "AnnotationIcContainer":
        """
        Create a container from given `data` and `metadata`.
        """
        return SimpleAnnotationIcContainer(
            data,
            metadata,
        )

    def to_csv(self, fh: typing.Union[str, typing.IO]):
        """
        Store the term ID to IC mapping with metadata into a CSV file.
        :param fh: where to write the
        :return:
        """
        now = datetime.now()
        self.metadata["created"] = now.strftime("%Y-%m-%d-%H:%M:%S")
        with open_text_io_handle_for_writing(fh) as handle:
            # (0) Comments
            handle.write("#Information content of the term ID calculated from HPO annotations\n")
            handle.write("#" + self.metadata_to_str() + "\n")

            # (1) Header
            fieldnames = ["term_id", "ic"]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()

            # (2) Entries
            for term_id, ic in self.items():
                writer.writerow({"term_id": term_id, "ic": ic})


class SimpleAnnotationIcContainer(AnnotationIcContainer):
    """
    An implementation of a :class:`AnnotationIcContainer` that is backed by a :class:`dict`.
    """

    def __init__(
        self,
        data: typing.Mapping[TermId, float],
        metadata: typing.Optional[typing.Mapping[str, str]] = None,
    ):
        if not isinstance(data, typing.Mapping):
            raise ValueError(f"data must be an instance of Mapping but it was: {type(data)}")
        self._data = data

        self._meta = dict()
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError(f"meta must be a dict but was {type(metadata)}")
            else:
                self._meta.update(metadata)

    def __getitem__(self, key: TermId) -> float:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> typing.Iterator[TermId]:
        return iter(self._data)

    @property
    def metadata(self) -> typing.MutableMapping[str, str]:
        return self._meta


class SimilarityContainer(MetadataAware, typing.Sized):
    """
    A container for pre-calculated semantic similarity results.
    """

    def __init__(self, metadata: typing.Optional[typing.Mapping[str, str]] = None):
        self._meta = dict()
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError(f"meta must be a dict but was {type(metadata)}")
            else:
                self._meta.update(metadata)
        self._data = self._prepare_datadict()

    def get_similarity(self, a: str, b: str) -> float:
        """
        Get similarity of two entries `a` and `b`.

        :param a: an item, e.g. `HP:1234567`
        :param b: another item, e.g. `HP:9876543`
        :return: a non-negative semantic similarity
        """
        o, i = (a, b) if a <= b else (b, a)
        outer = self._data.get(o, None)
        if outer:
            return outer.get(i, 0.0)
        else:
            return 0.0

    def set_similarity(self, a: str, b: str, sim: float):
        """
        Set semantic similarity for items `a` and `b`.
        :param a: an item, e.g. `HP:1234567`
        :param b: another item, e.g. `HP:9876543`
        :param sim: a non-negative semantic similarity
        """
        if sim < 0.0:
            raise ValueError(f"Similarity must be non-negative: {sim}")
        if a <= b:
            self._data[a][b] = sim
        else:
            self._data[b][a] = sim

    def items(self):
        """
        Get a generator of semantic similarities.

        Each item is a tuple with three items:
        *  left item (`str`)
        * right item (`str`)
        * similarity (`float`)
        """
        for a, vals in self._data.items():
            for b, sim in vals.items():
                yield a, b, sim

    @property
    def metadata(self) -> typing.MutableMapping[str, str]:
        return self._meta

    @staticmethod
    def _prepare_datadict() -> typing.MutableMapping[str, typing.MutableMapping[str, float]]:
        def inner() -> float:
            return 0.0

        def outer() -> defaultdict:
            return defaultdict(inner)

        return defaultdict(outer)

    def to_csv(self, fh: typing.Union[str, typing.IO]):
        now = datetime.now()
        self._meta["created"] = now.strftime("%Y-%m-%d-%H:%M:%S")
        with open_text_io_handle_for_writing(fh) as handle:
            # (0) Comments
            handle.write("#Information content of the most informative common ancestor for term pairs\n")
            handle.write("#" + self.metadata_to_str() + "\n")

            # (1) Header
            fieldnames = ["term_a", "term_b", "ic_mica"]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()

            # (2) Entries
            for left, right, sim in self.items():
                writer.writerow({"term_a": left, "term_b": right, "ic_mica": sim})

    @staticmethod
    def from_csv(fh: typing.Union[str, typing.IO]):
        header = []
        records = []

        def store_header(row: str) -> bool:
            if row[0] == "#":
                header.append(row)
                return False
            return True

        with open_text_io_handle_for_reading(fh) as handle:
            reader = csv.DictReader(filter(store_header, handle))
            for record in reader:
                records.append((record["term_a"], record["term_b"], float(record["ic_mica"])))

        meta = SimilarityContainer._parse_meta(header)
        data = SimilarityContainer(meta)
        for record in records:
            data.set_similarity(record[0], record[1], record[2])

        return data

    @staticmethod
    def _parse_meta(header: typing.Sequence[str]) -> typing.Mapping[str, str]:
        # Poor man's parsing.
        if len(header) < 2 or len(header[1]) < 2:
            return {}
        else:
            # The 2nd line is the metadata line, and we strip off the first and the last char (# and \n)
            return MetadataAware.metadata_from_str(header[1][1:-1])

    def __len__(self) -> int:
        return sum([len(inner) for inner in self._data.values()])
