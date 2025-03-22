import heapq
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, cast

T = TypeVar("T")


class AStar(ABC, Generic[T]):
    @abstractmethod
    def heuristic(self, node: T) -> float:
        pass

    @abstractmethod
    def get_neighbors(self, node: T) -> list[tuple[T, float]]:
        pass

    @abstractmethod
    def is_goal(self, node: T) -> bool:
        pass

    def search(self, start: T) -> Optional[list[T]]:
        open_set: list[tuple[float, T]] = []
        heapq.heappush(open_set, (0, start))
        came_from: dict[T, Optional[T]] = {start: None}
        g_score: dict[T, float] = {start: 0}
        f_score: dict[T, float] = {start: self.heuristic(start)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if self.is_goal(current):
                return self.reconstruct_path(came_from, current)

            for neighbor, cost in self.get_neighbors(current):
                tentative_g_score = g_score[current] + cost

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def reconstruct_path(self, came_from: dict[T, Optional[T]], current: T) -> list[T]:
        total_path = [current]
        while current in came_from and came_from[current] is not None:
            current = cast(T, came_from[current])
            total_path.append(current)
        total_path.reverse()
        return total_path
