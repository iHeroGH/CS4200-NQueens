import random
from queens import Board

class SelectionMethods:
    """
    The SelectionMethods class holds staticmethods for any selection methods
    written.

    Each function should be decorated with the "@staticmethod" decorator (meaning,
    you will not be passing 'self' as an argument)

    The first argument passed must be a list of Boards (the population).

    Any arguments can be passed after that, but they must all be typehinted with
    what type of argument they are (in the case of tournament selection, the
    proportion passed is a "float", so it is marked accordingly)

    After the function declaration is written, the return type of the function
    must be an Board object

    In short: any selection method must be given a Population (list of Boards),
    any other necessary arguments, and must return an Board

    Generic Example:
    @staticmethod
    def function_name(
                        parameter: param_type,
                        param_2: param_2_type
                    ) -> return_type:
        ...

    Specific Example:
    @staticmethod
    def selection_method_name(
                                population: list[Board],
                                ...
                        ) -> Board:
        ...
    """

    @staticmethod
    def tournament_selection(
                population: list[Board],
                proportion: float
            ) -> Board:
        """
        Chooses the best individual out of a subset of the population

        The subset's size is determined by the given proportion (such that
        subset size is = size of population * proportion)

        Parameters
        ----------
        population: list[Board]
            The population to select from
        proportion: float
            The proportion of the population to use for the tournament

        Returns
        -------
        Board
            The selected individual
        """

        # Calculate the tournament's size based on the proportion
        size = int(len(population) * proportion)

        if not 1 < size < len(population):
            raise ValueError(f"The tournament proportion {proportion} is " +
                            f"invalid for population size {len(population)}.")

        # Select first random Board
        parent = random.choice(population)

        # Choose n random Boards and choose the best out of them
        for _ in range(size):
            opponent = random.choice(population)
            if opponent.num_attacking < parent.num_attacking:
                parent = opponent

        return parent

    @staticmethod
    def random_selection(population: list[Board]) -> Board:
        return random.choice(population)

class GeneticAlgorithm:

    # Some configuration values
    # We want a relatively low number of generations (since we converge quickly
    # anyways, and end up not changing the board too much after that) and a
    # relatively high population size (since we want to throw as many darts as
    # we can in hopes that some of the darts hit the bullseye)
    # Since the board size is relatively small as well (usually 8), we want
    # a pretty high mutation probability. This is to promote genetic diversity
    # in later generations
    NUM_INDIVIDUALS = 750
    NUM_GENERATIONS = 10
    MUTATION_PROBABILITY = 0.5
    TOURNAMENT_PROPORTION = 0.05

    def __init__(self, board: Board, log: bool = True) -> None:
        self.input_board = board
        self.log = log

        # Does the generation loop of the algorithm
        found_population, self.cost = self.gen_loop()
        self.best = GeneticAlgorithm.get_best_individual(found_population)
        if self.log:
            print(f"Best found has {self.best.num_attacking} attacks.")

    def initialize_population(self) -> list[Board]:

        # Initialize population based on slight variations of the input board
        population = [self.input_board]
        while len(population) < GeneticAlgorithm.NUM_INDIVIDUALS:
            curr = random.choice(
                    [Board.from_str(repr(self.input_board))] +
                    self.input_board.possible_moves
                )

            if random.random() < GeneticAlgorithm.MUTATION_PROBABILITY:
                GeneticAlgorithm.mutate(curr)

            population.append(curr)

        # Find out what the best individual that we're starting off of is
        best = GeneticAlgorithm.get_best_individual(population)
        if self.log:
            print(f"Initialized {len(population)} individuals.")
            print(
                f"Best at initialization has {best.num_attacking} attacks."
            )

        return population

    def gen_loop(self) -> tuple[list[Board], int]:

        # Initialization
        current_population = self.initialize_population()

        if self.log:
            print(f"Beginning {GeneticAlgorithm.NUM_GENERATIONS} generations.")

        # Generation loop
        for i in range(GeneticAlgorithm.NUM_GENERATIONS):

            # sorted_population = sorted(
            #     current_population,
            #     key=lambda p: p.num_attacking
            # )

            # Implement elitism. The best individual of each generation will
            # always get passed along to the next generation.
            best = GeneticAlgorithm.get_best_individual(current_population)
            next_population = [best]

            # If we already found a solution, early exit
            if not best.num_attacking:
                current_population = next_population
                return current_population, i - 1

            # # Filtering
            # percentile_fitness = sorted_population[
            #     (7*len(current_population))//10
            # ].num_attacking

            # acceptable_subset = [
            #     p for p in sorted_population
            #     if p.num_attacking >= percentile_fitness
            # ]

            # for index, individual in enumerate(current_population):
            #     if individual.num_attacking >= percentile_fitness:
            #         current_population[index] = random.choice(acceptable_subset)

            if not i % 5 and self.log:
                print(
                    f"Best at generation {i} has {best.num_attacking} attacks."
                )

            # Fill the next population
            while len(next_population) < GeneticAlgorithm.NUM_INDIVIDUALS:

                # Selection
                parent_one = SelectionMethods.tournament_selection(
                    current_population, GeneticAlgorithm.TOURNAMENT_PROPORTION
                )
                parent_two = SelectionMethods.tournament_selection(
                    current_population, GeneticAlgorithm.TOURNAMENT_PROPORTION
                )

                # Crossover
                child_one = GeneticAlgorithm.crossover(parent_one, parent_two)
                child_two = GeneticAlgorithm.crossover(parent_one, parent_two)

                # Mutation
                if random.random() <= GeneticAlgorithm.MUTATION_PROBABILITY:
                    GeneticAlgorithm.mutate(child_one)
                    GeneticAlgorithm.mutate(child_two)

                # Add the children to the next generation's population
                next_population.append(child_one)
                if len(next_population) < GeneticAlgorithm.NUM_INDIVIDUALS:
                    next_population.append(child_two)

            # Prepare for next iteration
            current_population = next_population

        return current_population, GeneticAlgorithm.NUM_GENERATIONS

    @staticmethod
    def crossover(parent_one: Board, parent_two: Board):
        crossover_point = random.randint(1, parent_one.n - 1)

        # Create a new child out of the first portion of the first parent
        # and second portion of the second parent
        child_chromosome = (
            repr(parent_one)[:crossover_point] +
            repr(parent_two)[crossover_point:]
        )

        return Board.from_str(child_chromosome)

    @staticmethod
    def mutate(child: Board) -> None:

        # Choose two random, different, indices and swap them
        id1 = random.randint(0, len(repr(child)) - 1)
        id2 = random.randint(0, len(repr(child)) - 1)

        while id2 == id1:
            id2 = random.randint(0, len(repr(child)) - 1)

        child.queens[id1], child.queens[id2] = child.queens[id2], child.queens[id1]

    @staticmethod
    def get_best_individual(population: list[Board]):
        # Retrieve the best individual based on the number of queens under attack
        return min(population, key=lambda x: x.num_attacking)
