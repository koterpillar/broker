import unittest

from broker.astar import AStar


class NumbersAStar(AStar[int]):
    def __init__(self, *, goal: int, steps: list[int]):
        self.goal = goal
        self.steps = steps

    def heuristic(self, node: int) -> float:
        return abs(node - self.goal)

    def get_neighbors(self, node: int) -> list[tuple[int, float]]:
        return [
            (node + step, abs(step)) for step in self.steps if abs(node + step) <= 100
        ]

    def is_goal(self, node: int) -> bool:
        return node == self.goal


class TestAStar(unittest.TestCase):
    def test_simple_path(self):
        astar = NumbersAStar(goal=5, steps=[1, -1])
        path = astar.search(start=0)
        self.assertEqual(path, [0, 1, 2, 3, 4, 5])

    def test_no_path(self):
        astar = NumbersAStar(goal=5, steps=[2])
        path = astar.search(start=0)
        self.assertIsNone(path)
