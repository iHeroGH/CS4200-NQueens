from solver import Solver, attempt

attempt(25, Solver.hill_climb)
attempt(5, Solver.simulated_annealing)
attempt(15, Solver.genetic_algorithm)
attempt(5, Solver.min_conflicts)