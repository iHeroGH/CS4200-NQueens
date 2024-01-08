from math import exp
import random
from time import time
from typing import Any, Callable

from queens import Board, Queen
from ga_utils import GeneticAlgorithm

def time_solver(
            solver: Callable[..., tuple[Board, int]]
        ) -> Callable[..., tuple[Board, int]]:
    """
    Defines a decorator for timing how long it took for a solver method (which
    returns a Board) to execute.

    The time taken is printed to the console

    Parameters
    ----------
    solver : Callable[..., tuple[Board, int]]
        A callable Solver method which takes in any parameters and returns a
        Board object and the cost

    Returns
    -------
    wrapper : Callable[..., tuple[Board, int]]
        The wrapper function that took any arguments passed in, passed it to the
        Solver, timed the solve time, then returned the created Board and cost
    """

    def wrapper(*args: Any) -> tuple[Board, int]:
        start_time = time()
        board, cost = solver(*args)
        duration = time() - start_time

        print(f"({solver.__name__}) Time Taken: {duration / 60:.4f} minutes")
        return board, cost

    return wrapper

class Solver:

    @staticmethod
    # @time_solver
    def hill_climb(board: Board) -> tuple[Board, int]:

        cost = 0
        best = board
        while True:
            neighbor = min(best.possible_moves, key=lambda x: x.num_attacking)
            # Once there are no more better neighbors, exit
            if neighbor >= best:
                return best, cost
            best = neighbor
            cost += 1

    @staticmethod
    # @time_solver
    def simulated_annealing(
                board: Board,
                cooling_factor: float = 0.75,
                initial_temperature: float = 500_000
            ) -> tuple[Board, int]:

        cost = 0
        current = board
        temperature = initial_temperature
        # While we have the smallest resemblance of a temperature
        while temperature >= 1e-300:

            neighbor = random.choice(current.possible_moves)
            delta_e = current.num_attacking - neighbor.num_attacking

            # Early exit if we found the solution
            if not neighbor.num_attacking:
                return neighbor, cost

            # If this is a better solution, store it
            # If it isn't, *maybe* store it (depending on the temperature)
            if delta_e > 0 or random.random() < exp(delta_e / temperature):
                current = neighbor

            # Cool it down
            temperature *= cooling_factor
            cost += 1

        return current, cost

    @staticmethod
    # @time_solver
    def genetic_algorithm(board: Board, log: bool = False) -> tuple[Board, int]:
        ga = GeneticAlgorithm(board, log)
        return ga.best, 0

    @staticmethod
    # @time_solver
    def min_conflicts(board: Board, max_steps: int = 10_000) -> tuple[Board, int]:

        current = board
        conflict: Queen
        cost = 0
        for _ in range(max_steps):

            if not current.num_attacking:
                return current, cost

            con_ind, conflict = random.choice(list(current.conflicting_queens))
            min_conflict = min(
                current.possible_moves_part(con_ind, conflict),
                key=lambda x: x.num_attacking
            )

            current = min_conflict
            cost += 1

        return current, cost

def attempt(total_trials: int, solver: Callable[..., tuple[Board, int]], *args):
    print(f"({solver.__name__})")

    trials = total_trials
    correct = 0
    running_cost = 0
    while trials > 0:

        if trials == total_trials or not trials % 100:
            print(f"{trials} trials remaining. {correct} correct so far.")

        inp = Board.random_fill(8)
        out, cost = solver(inp, *args)
        running_cost += cost
        if out.num_attacking == 0:
            correct += 1

            if correct <= 3:
                print("INPUT\n", inp, "\nAttacks: ", inp.num_attacking)
                print("OUTPUT\n", out)
                print("||||||||||||||||||||||||||||||||||||||||||||||")

        trials -= 1

    print(
        f"{correct/(total_trials-trials) * 100}% of trials were correct. " +
        f"({correct} correct trials out of {(total_trials-trials)} trials). " +
        f"Average Cost: {running_cost / (total_trials-trials)}."
    )
    print()

