import unittest

import ddt
import numpy as np

from hpotk.model import TermId

from .csr import ImmutableCsrMatrix
from ._csr_graph import check_items_are_sorted
from ._csr_graph import BisectPoweredCsrOntologyGraph


@ddt.ddt
class TestFunctions(unittest.TestCase):
    @ddt.data(
        ([],),
        ([1],),
        ([1, 2],),
        (["a", "b", "c"],),
    )
    @ddt.unpack
    def test_check_items_are_sorted(self, items):
        self.assertIsNone(check_items_are_sorted(items))

    @ddt.data(
        ([2, 1], "Unsorted sequence. Item #1 (1) was less than #0 (2)"),
        ([2, 1, 3, 4, 5, 6], "Unsorted sequence. Item #1 (1) was less than #0 (2)"),
        ([1, 2, 30, 4, 5, 6], "Unsorted sequence. Item #3 (4) was less than #2 (30)"),
        ([1, 2, 3, 4, 6, 5], "Unsorted sequence. Item #5 (5) was less than #4 (6)"),
    )
    @ddt.unpack
    def test_check_items_are_sorted__unsorted_cases(self, items, message):
        with self.assertRaises(ValueError) as ctx:
            check_items_are_sorted(items)
        self.assertEqual(message, ctx.exception.args[0])


@ddt.ddt
class TestBisectPoweredCsrOntologyGraph(unittest.TestCase):
    NODES: np.ndarray
    GRAPH: BisectPoweredCsrOntologyGraph

    @classmethod
    def setUpClass(cls) -> None:
        root = TermId.from_curie("HP:1")
        curies = [
            "HP:01",
            "HP:010",
            "HP:011",
            "HP:0110",
            "HP:02",
            "HP:020",
            "HP:021",
            "HP:022",
            "HP:03",
            "HP:1",
        ]
        nodes = np.fromiter(map(TermId.from_curie, curies), dtype=object)
        row = [0, 3, 5, 7, 9, 13, 14, 15, 16, 17, 20]
        col = [1, 2, 9, 0, 3, 0, 3, 1, 2, 5, 6, 7, 9, 4, 4, 4, 9, 0, 4, 8]
        data = [-1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1]
        am = ImmutableCsrMatrix(row, col, data, shape=(len(nodes), len(nodes)), dtype=int)

        cls.NODES = nodes
        cls.GRAPH = BisectPoweredCsrOntologyGraph(root, nodes, am)

    def test_root(self):
        self.assertEqual(TermId.from_curie("HP:1"), self.GRAPH.root)

    @ddt.data(
        ("HP:1", ["HP:01", "HP:02", "HP:03"]),
        ("HP:02", ["HP:020", "HP:021", "HP:022"]),
        ("HP:03", []),
    )
    @ddt.unpack
    def test_get_children(self, source, expected):
        src = TermId.from_curie(source)
        exp = set(map(TermId.from_curie, expected))

        for term_id in self.GRAPH.get_children(src):
            exp.remove(term_id)
        self.assertTrue(len(exp) == 0)

        exp = set(map(TermId.from_curie, expected))
        exp.add(src)
        for term_id in self.GRAPH.get_children(src, include_source=True):
            exp.remove(term_id)

        self.assertTrue(len(exp) == 0)

    @ddt.data(
        (
            "HP:1",
            [
                "HP:01",
                "HP:010",
                "HP:011",
                "HP:0110",
                "HP:02",
                "HP:020",
                "HP:021",
                "HP:022",
                "HP:03",
            ],
        ),
        ("HP:01", ["HP:010", "HP:011", "HP:0110"]),
        ("HP:010", ["HP:0110"]),
        ("HP:011", ["HP:0110"]),
        ("HP:0110", []),
        ("HP:02", ["HP:020", "HP:021", "HP:022"]),
        ("HP:020", []),
        ("HP:021", []),
        ("HP:022", []),
        ("HP:03", []),
    )
    @ddt.unpack
    def test_get_descendants(self, source, expected):
        src = TermId.from_curie(source)
        exp = set(map(TermId.from_curie, expected))

        for term_id in self.GRAPH.get_descendants(src):
            exp.remove(term_id)
        self.assertTrue(len(exp) == 0)

        exp = set(map(TermId.from_curie, expected))
        exp.add(src)
        for term_id in self.GRAPH.get_descendants(src, include_source=True):
            exp.remove(term_id)

        self.assertTrue(len(exp) == 0)

    @ddt.data(
        ("HP:1", []),
        ("HP:01", ["HP:1"]),
        ("HP:03", ["HP:1"]),
        ("HP:0110", ["HP:010", "HP:011"]),
    )
    @ddt.unpack
    def test_get_parents(self, source, expected):
        src = TermId.from_curie(source)
        exp = set(map(TermId.from_curie, expected))

        for term_id in self.GRAPH.get_parents(src):
            exp.remove(term_id)
        self.assertTrue(len(exp) == 0)

        exp = set(map(TermId.from_curie, expected))
        exp.add(src)
        for term_id in self.GRAPH.get_parents(src, include_source=True):
            exp.remove(term_id)

        self.assertTrue(len(exp) == 0)

    @ddt.data(
        ("HP:1", []),
        ("HP:01", ["HP:1"]),
        ("HP:0110", ["HP:010", "HP:011", "HP:01", "HP:1"]),
        ("HP:022", ["HP:02", "HP:1"]),
        ("HP:03", ["HP:1"]),
    )
    @ddt.unpack
    def test_get_ancestors(self, source, expected):
        src = TermId.from_curie(source)
        exp = set(map(TermId.from_curie, expected))

        for term_id in self.GRAPH.get_ancestors(src):
            exp.remove(term_id)
        self.assertTrue(len(exp) == 0)

        exp = set(map(TermId.from_curie, expected))
        exp.add(src)
        for term_id in self.GRAPH.get_ancestors(src, include_source=True):
            exp.remove(term_id)

        self.assertTrue(len(exp) == 0)

    @ddt.data(
        ("HP:1", False),
        ("HP:01", False),
        ("HP:010", False),
        ("HP:011", False),
        ("HP:0110", True),
        ("HP:02", False),
        ("HP:020", True),
        ("HP:021", True),
        ("HP:022", True),
        ("HP:03", True),
    )
    @ddt.unpack
    def test_is_leaf(self, source, expected):
        src = TermId.from_curie(source)
        actual = self.GRAPH.is_leaf(src)
        self.assertEqual(expected, actual)

    def test_is_leaf__unknown_source(self):
        with self.assertRaises(ValueError) as ctx:
            self.GRAPH.is_leaf(TermId.from_curie("HP:999"))
        self.assertEqual("Term ID not found in the graph: HP:999", ctx.exception.args[0])

    @ddt.data(
        ("get_parents",),
        ("get_ancestors",),
        ("get_children",),
        ("get_descendants",),
    )
    @ddt.unpack
    def test_traverse_methods_with_unknown_source(self, func_name):
        unknown = TermId.from_curie("HP:999")

        func = getattr(self.GRAPH, func_name)
        with self.assertRaises(ValueError) as ctx:
            list(func(unknown))  # We must consume the iterable!
        self.assertEqual("Term ID not found in the graph: HP:999", ctx.exception.args[0])

        func = getattr(self.GRAPH, func_name)
        with self.assertRaises(ValueError) as ctx:
            list(func(unknown, include_source=True))  # We must consume the iterable!
        self.assertEqual("Term ID not found in the graph: HP:999", ctx.exception.args[0])

    def test_contains(self):
        for node in self.NODES:
            self.assertTrue(node in self.GRAPH)

    def test_iter(self):
        expected = set(self.NODES)
        actual = set(iter(self.GRAPH))
        self.assertSetEqual(expected, actual)
