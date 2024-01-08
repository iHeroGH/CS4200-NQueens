from __future__ import annotations
import random

class Queen:
    def __init__(self, row: int = 0):
        self.row = row

    def __str__(self) -> str:
        return "Q"

    def __repr__(self) -> str:
        return str(self.row)

    def __eq__(self, o: object):
        return isinstance(o, Queen) and self.row == o.row

    def __hash__(self):
        return hash(self.row)

    def __sub__(self, other: Queen):
        return self.row - other.row


    def possible_moves(self, n) -> list[Queen]:
        return [Queen(i) for i in range(0, n) if i != self.row]

class Board:

    NON_QUEEN = "-"

    def __init__(self, n: int = 8):
        self.n = n
        self.queens: list[Queen | None] = [None for _ in range(n)]
        self.available = 0

    @classmethod
    def random_fill(cls, n: int = 8) -> Board:
        return cls.from_str(
            "".join([str(random.randint(0, n - 1)) for _ in range(n)])
        )

    @classmethod
    def from_str(cls, identifier: str) -> Board:
        b = cls(len(identifier))

        i: str | int
        for i in identifier:
            assert isinstance(i, str)

            if i == cls.NON_QUEEN:
                b.add_queen(None)
                continue

            if not i.isdigit():
                raise ValueError(
                    f"ID must be composed of digits or {cls.NON_QUEEN}"
                )

            i = int(i)
            b.add_queen(Queen(i))

        return b

    def add_queen(self, queen: Queen | None) -> Board:
        if self.available >= self.n:
            raise ValueError("Exceeded Board Limit")

        if queen and queen.row >= self.n:
            raise ValueError("Exceeded Board Limit")

        self.queens[self.available] = queen
        self.available += 1

        return self

    def add_queens(self, *queens: Queen | None) -> Board:
        for queen in queens:
            self.add_queen(queen)

        return self

    def compare_queens(
                self,
                first_ind: int,
                first_queen: Queen | None,
                second_ind: int,
                second_queen: Queen | None
            ) -> int:
        attacks = 0

        if first_ind == second_ind:
            return attacks

        if not (first_queen and second_queen):
            return attacks

        if first_queen == second_queen:
            attacks += 1

        if abs(first_ind - second_ind) == abs(first_queen - second_queen):
            attacks += 1

        return attacks

    @property
    def num_attacking(self) -> int:

        attacks = 0
        for first_ind, first_queen in enumerate(self.queens):
            for second_ind, second_queen in enumerate(self.queens):
                attacks += self.compare_queens(
                    first_ind, first_queen, second_ind, second_queen
                )

        return attacks//2

    @property
    def conflicting_queens(self) -> set[tuple[int, Queen]]:

        conflicting = set()

        for first_ind, first_queen in enumerate(self.queens):
            for second_ind, second_queen in enumerate(self.queens):

                if (first_ind, first_queen) in conflicting and \
                    (second_ind, second_queen) in conflicting:
                    continue

                if self.compare_queens(
                    first_ind, first_queen, second_ind, second_queen
                ):
                    if first_queen:
                        conflicting.add((first_ind, first_queen))
                    if second_queen:
                        conflicting.add((second_ind, second_queen))

        return conflicting

    def __ge__(self, o: Board):
        return self.num_attacking >= o.num_attacking

    def __lt__(self, o: Board):
        return self.num_attacking < o.num_attacking

    @property
    def possible_moves(self) -> list[Board]:
        possible_boards: list[Board] = []

        for ind, curr_queen in enumerate(self.queens):
            if not curr_queen:
                continue

            possible_boards += self.possible_moves_part(ind, curr_queen)

        return possible_boards

    def possible_moves_part(self, index: int, curr_queen: Queen) -> list[Board]:

        possible_boards = []

        for possible_queen in curr_queen.possible_moves(self.n):
            b = Board.from_str(repr(self))
            b.queens[index] = possible_queen
            possible_boards.append(b)

        return possible_boards

    def __str__(self) -> str:
        matrix_repr = [
            [self.NON_QUEEN for _ in range(self.n)] for _ in range(self.n)
        ]

        curr_col = 0
        for queen in self.queens:
            if queen:
                matrix_repr[queen.row][curr_col] = str(queen)
            curr_col += 1

        return "\n".join(["  ".join(i) for i in matrix_repr])

    def __repr__(self) -> str:
        return "".join(
            [repr(queen) if queen else self.NON_QUEEN for queen in self.queens]
        )

if __name__ == "__main__":
    b = Board.from_str("0123")

    print(b)
    # print(repr(b))
    print(b.num_attacking)
    print("--------")

