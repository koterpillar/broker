import unittest
from collections.abc import Iterator

from broker.astar import AStar, NoPathError


class NumbersAStar(AStar[int]):
    def __init__(self, *, goal: int, steps: list[int]):
        self.goal = goal
        self.steps = steps

    def is_goal(self, node: int) -> bool:
        return node == self.goal

    def heuristic(self, node: int) -> float:
        return abs(node - self.goal)

    def get_neighbors(self, node: int) -> Iterator[tuple[int, float]]:
        for step in self.steps:
            if abs(node + step) <= 100:
                yield node + step, abs(step)


class TestAStar(unittest.TestCase):
    def test_simple_path(self):
        astar = NumbersAStar(goal=5, steps=[1, -1])

        path = astar.search(start=0)

        self.assertEqual(path, [0, 1, 2, 3, 4, 5])

    def test_no_path(self):
        astar = NumbersAStar(goal=5, steps=[2])

        with self.assertRaises(NoPathError) as context:
            astar.search(start=0)

        exception = context.exception
        self.assertEqual(exception.best_node, 4)
        self.assertEqual(exception.path, [0, 2, 4])
