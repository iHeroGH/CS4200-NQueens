from solver import Solver, attempt

attempt(500, Solver.hill_climb)
attempt(10, Solver.simulated_annealing)
attempt(500, Solver.genetic_algorithm)
attempt(500, Solver.min_conflicts)