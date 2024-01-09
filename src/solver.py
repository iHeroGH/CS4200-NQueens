from math import exp
import random
from time import time
from typing import Any, Callable

from queens import Board, Queen
from ga_utils import GeneticAlgorithm

def time_solver(
            solver: Callable[..., tuple[Board, int]]
        ) -> Callable[..., tuple[Board, int, float]]:
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
        Solver, timed the solve time, then returned the created Board, cost,
        and running time
    """

    def wrapper(*args: Any) -> tuple[Board, int, float]:
        start_time = time()
        board, cost = solver(*args)
        duration = time() - start_time

        # print(f"({solver.__name__}) Time Taken: {duration / 60:.4f} minutes")
        return board, cost, duration

    wrapper.__name__ = solver.__name__

    return wrapper

class Solver:

    @staticmethod
    @time_solver
    def hill_climb(board: Board) -> tuple[Board, int]:

        cost = 0
        best = board
        while True:
            neighbor = min(best.possible_moves, key=lambda x: x.num_attacking)

            # Once there are no more better neighbors, exit. We have reached
            # a local maxima
            if neighbor >= best:
                return best, cost

            # Prepare for the next iteration
            best = neighbor
            cost += 1

    @staticmethod
    @time_solver
    def simulated_annealing(
                board: Board,
                cooling_factor: float = 0.80,
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
    @time_solver
    def genetic_algorithm(board: Board, log: bool = False) -> tuple[Board, int]:
        ga = GeneticAlgorithm(board, log)
        return ga.best, 0

    @staticmethod
    @time_solver
    def min_conflicts(board: Board, max_steps: int = 9999) -> tuple[Board, int]:

        cost = 0
        current = board
        conflict: Queen
        for _ in range(max_steps):

            # If we find a solution, exit
            if not current.num_attacking:
                return current, cost

            # Retrieve a random queen that's under attack
            con_ind, conflict = random.choice(list(current.conflicting_queens))

            # Move it out of danger
            min_conflict = min(
                current.possible_moves_part(con_ind, conflict),
                key=lambda x: x.num_attacking
            )

            # Prepare for the next iteration
            current = min_conflict
            cost += 1

        return current, cost

def attempt(
        total_trials: int,
        solver: Callable[..., tuple[Board, int, float]],
        *args
    ):
    # Attempts a given solver(*args) for a given amount of trials

    print(f"({solver.__name__})")

    trials: int = total_trials
    correct: int = 0
    running_cost: int = 0
    running_duration: float = 0
    while trials > 0:

        # Some simple logging
        if trials == total_trials or not trials % 100:
            print(f"{trials} trials remaining. {correct} correct so far.")

        # Perform the solving
        inp = Board.random_fill(8)
        out, cost, duration = solver(inp, *args)
        running_cost += cost
        running_duration += duration
        if out.num_attacking == 0:
            correct += 1

            # Print the first 3 correct outputs
            if correct <= 3:
                print("INPUT\n", inp, "\nAttacks: ", inp.num_attacking)
                print("OUTPUT\n", out)
                print("||||||||||||||||||||||||||||||||||||||||||||||")

        trials -= 1

    # If there is an early exit of some kind
    complete_trials = total_trials - trials

    # Print some statistics
    print(
        f"{correct/(complete_trials) * 100}% of trials were correct. ",
        f"({correct} correct trials out of {(complete_trials)} trials)."
    )
    print(f"Average Cost: {running_cost / (complete_trials)}.")
    print(f"Average Time Taken: {(running_duration / (complete_trials)):.4f}s.")
    print()


