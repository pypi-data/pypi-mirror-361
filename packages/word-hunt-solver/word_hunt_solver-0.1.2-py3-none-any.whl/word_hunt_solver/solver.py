from typing import Dict, List, Tuple
from english_words import get_english_words_set
from pprint import pprint


class Solver:
    def __init__(self, n=4):
        self.n = n
        self.adj_list: Dict[Tuple[int, int], List] = {}
        self.directions = [(-1, -1), (-1, 0),
                           (-1, 1), (0, -1),
                           (0, 1), (1, -1),
                           (1, 0), (1, 1)]
        self.words = set(get_english_words_set(['web2'], lower=True))
        self.answers = set()

    def _is_valid_coord(self, i, j):
        return 0 <= i < self.n and 0 <= j < self.n

    def load_board(self):
        letters = input("Enter letters separated by spaces:\n").split()
        if len(letters) != self.n * self.n:
            raise ValueError(f"You must enter exactly {self.n * self.n} letters.")

        self.board = [
            [letters[i * self.n + j].lower() for j in range(self.n)]
            for i in range(self.n)
        ]

    def dfs(self, word, i, j, visited):
        word += self.board[i][j]
        visited.add((i, j))

        if len(word) >= 3 and word in self.words:
            self.answers.add(word)
            self.words.remove(word)

        for di, dj in self.directions:
            ni, nj = i + di, j + dj
            if self._is_valid_coord(ni, nj) and (ni, nj) not in visited:
                self.dfs(word, ni, nj, visited)

        visited.remove((i, j))

    def solve(self) -> List[str]:
        for i in range(self.n):
            for j in range(self.n):
                self.dfs("", i, j, set())

        return sorted(list(self.answers), key=lambda w: -len(w))


def main():
    solver = Solver()
    solver.load_board()
    print("solving...")
    pprint(solver.solve())
