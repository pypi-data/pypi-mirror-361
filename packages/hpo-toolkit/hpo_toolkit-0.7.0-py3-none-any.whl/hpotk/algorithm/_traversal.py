import typing
from warnings import warn

from hpotk.model import TermId, CURIE_OR_TERM_ID
from hpotk.graph import OntologyGraph, GraphAware


def get_ancestors(
    g: typing.Union[GraphAware, OntologyGraph],
    source: CURIE_OR_TERM_ID,
    include_source: bool = False,
) -> typing.FrozenSet[TermId]:
    """
    Get all ancestor :class:`TermId`\\ (s). of the `source` term (parents, grandparents, great-grandparents etc.)..

    The method raises a :class:`ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: `:class:`TermId` or a term ID curie as a `str (e.g. `HP:1234567`)
    :param include_source: whether to include the `source` term in the resulting set
    :return: a `frozenset` with ancestor :class:`TermId`\\ (s).
    """
    # TODO[v1.0.0] - remove the deprecated method
    warn(
        "The method is deprecated and will be removed in v1.0.0. Use `get_ancestors` of the graph instead",
        DeprecationWarning,
        stacklevel=2,
    )
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    # Init
    builder: set[TermId] = set()
    if include_source:
        builder.add(source)

    builder.update(g.get_ancestors(source))

    return frozenset(builder)


def get_parents(
    g: typing.Union[GraphAware, OntologyGraph],
    source: CURIE_OR_TERM_ID,
    include_source: bool = False,
) -> typing.FrozenSet[TermId]:
    """
    Get :class:`TermId`\\ (s). of the direct parents of the `source` term.

    The method raises a :class:`ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: :class:`TermId` or a term ID curie as a :class:`str (e.g. `HP:1234567`)
    :param include_source:  whether to include the `source` term ID(s) in the results
    :return: a :class:`frozenset` with parent `TermId`s
    """
    # TODO[v1.0.0] - remove the deprecated method
    warn(
        "The method is deprecated and will be removed in v1.0.0. Use `get_parents` of the graph instead",
        DeprecationWarning,
        stacklevel=2,
    )
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    # Init
    builder: typing.Set[TermId] = set()
    if include_source:
        builder.add(source)

    builder.update(g.get_parents(source))

    return frozenset(builder)


def get_descendants(
    g: typing.Union[GraphAware, OntologyGraph],
    source: CURIE_OR_TERM_ID,
    include_source: bool = False,
) -> typing.FrozenSet[TermId]:
    """
    Get all descendants `TermId`s of the `source` term (children, grandchildren, great-grandchildren etc.)..

    The method raises a `ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: `TermId` or a term ID curie as a `str (e.g. `HP:1234567`)
    :param include_source:  whether to include the `source` term ID(s) in the results
    :return: a :class:`frozenset` with descendants `TermId`s
    """
    # TODO[v1.0.0] - remove the deprecated method
    warn(
        "The method is deprecated and will be removed in v1.0.0. Use `get_descendants` of the graph instead",
        DeprecationWarning,
        stacklevel=2,
    )
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    # Init
    builder: set[TermId] = set()
    if include_source:
        builder.add(source)

    builder.update(g.get_descendants(source))

    return frozenset(builder)


def get_children(
    g: typing.Union[GraphAware, OntologyGraph],
    source: CURIE_OR_TERM_ID,
    include_source: bool = False,
) -> typing.FrozenSet[TermId]:
    """
    Get `TermId`s of the direct children of the `source` term.

    The method raises a `ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: `TermId` or a CURIE `str` (e.g. `HP:1234567`)
    :param include_source: whether to include the `source` term in the results
    :return: an iterable with child `TermId`s
    """
    # TODO[v1.0.0] - remove the deprecated method
    warn(
        "The method is deprecated and will be removed in v1.0.0. Use `get_children` of the graph instead",
        DeprecationWarning,
        stacklevel=2,
    )
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    builder: set[TermId] = set()
    if include_source:
        builder.add(source)

    builder.update(g.get_children(source))

    return frozenset(builder)


def exists_path(
    g: typing.Union[GraphAware, OntologyGraph],
    source: CURIE_OR_TERM_ID,
    destination: CURIE_OR_TERM_ID,
) -> bool:
    """
    Return `True` if `destination` is an ancestor of the `source` term.

    The path does *not* exists if `source` and `destination` are the same term.

    :param g: the ontology graph or a graph-aware entity
    :param source: `TermId` or a CURIE `str` (e.g. `HP:1234567`)
    :param destination: `TermId` or a CURIE `str` (e.g. `HP:1234567`)
    :return: `True` if a path exists from `source` to `destination`
    """
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)
    destination = _check_curie_or_term_id(destination)

    if source == destination:
        return False

    for ancestor in get_ancestors(g, source):
        if ancestor == destination:
            return True

    return False


def _check_ontology_graph_is_available(g):
    if isinstance(g, OntologyGraph):
        pass
    elif isinstance(g, GraphAware):
        g = g.graph
    else:
        raise ValueError(f"`g` must implement `OntologyGraph` or `GraphAware` but got {type(g)}")
    return g


def _check_curie_or_term_id(source: CURIE_OR_TERM_ID) -> TermId:
    if isinstance(source, str):
        source = TermId.from_curie(source)
    elif isinstance(source, TermId):
        pass
    else:
        raise ValueError(f"`source` must be `TermId` or a CURIE `str` but got {type(source)}")
    return source
