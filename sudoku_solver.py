"""
SUDOKU SOLVER
Hybrid Breadth First Search (BFS) with Backtracking and MRV.

MODEL:
X[r][c] represents the value assigned to cell (r, c).

VARIABLES:
81 cells in a 9x9 grid.

DOMAIN:
{1, 2, ..., 9}
0 represents an empty cell.

CONSTRAINTS:
1. Every row contains numbers 1-9 exactly once.
2. Every column contains numbers 1-9 exactly once.
3. Every 3x3 box contains numbers 1-9 exactly once.

OBJECTIVE FUNCTION:
f(S) = constraint violations + empty cells.

A complete valid Sudoku has f(S) = 0.

LANDSCAPE:
L = 9^k, where k is the number of empty cells.

ALGORITHM:
BFS explores the first two search levels.
Backtracking completes the search from each BFS state.
MRV selects the empty cell with the fewest candidates.
The generator checks solution uniqueness.
"""

from collections import deque
import random
import time


SIZE = 9
BOX = 3
BFS_DEPTH = 2

LEVELS = {
    "Easy": 35,
    "Medium": 45,
    "Hard": 55
}


# --------------------------------------------------
# LANDSCAPE
# --------------------------------------------------

def landscape(empty_cells):
    """Calculates unrestricted possible assignments."""
    return 9 ** empty_cells


# --------------------------------------------------
# OBJECTIVE FUNCTION
# --------------------------------------------------

def objective(board):
    """Counts constraint violations and empty cells."""

    violations = 0

    # Check rows.
    for r in range(SIZE):
        values = [
            value for value in board[r]
            if value != 0
        ]

        violations += len(values) - len(set(values))

    # Check columns.
    for c in range(SIZE):
        values = [
            board[r][c]
            for r in range(SIZE)
            if board[r][c] != 0
        ]

        violations += len(values) - len(set(values))

    # Check 3x3 boxes.
    for br in range(0, SIZE, BOX):
        for bc in range(0, SIZE, BOX):

            values = [
                board[r][c]
                for r in range(br, br + BOX)
                for c in range(bc, bc + BOX)
                if board[r][c] != 0
            ]

            violations += len(values) - len(set(values))

    empty_cells = sum(row.count(0) for row in board)

    return violations + empty_cells


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def valid_board(board):
    """Checks dimensions, values and Sudoku constraints."""

    if not isinstance(board, (list, tuple)):
        return False

    if len(board) != SIZE:
        return False

    for row in board:

        if not isinstance(row, (list, tuple)):
            return False

        if len(row) != SIZE:
            return False

        for value in row:

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
                or value > 9
            ):
                return False

    empty_cells = sum(row.count(0) for row in board)

    return objective(board) == empty_cells


# --------------------------------------------------
# CANDIDATES
# --------------------------------------------------

def candidates(board, r, c):
    """Returns valid values for an empty cell."""

    used = set(board[r])

    # Check column.
    used.update(
        board[i][c]
        for i in range(SIZE)
    )

    # Check 3x3 box.
    br = (r // BOX) * BOX
    bc = (c // BOX) * BOX

    used.update(
        board[i][j]
        for i in range(br, br + BOX)
        for j in range(bc, bc + BOX)
    )

    return [
        value
        for value in range(1, SIZE + 1)
        if value not in used
    ]


# --------------------------------------------------
# SELECT EMPTY CELL
# --------------------------------------------------

def find_empty(board):
    """MRV: selects the empty cell with fewest candidates."""

    best_cell = None
    best_values = None

    for r in range(SIZE):
        for c in range(SIZE):

            if board[r][c] == 0:

                possible = candidates(board, r, c)

                if not possible:
                    return r, c, []

                if (
                    best_values is None
                    or len(possible) < len(best_values)
                ):
                    best_cell = (r, c)
                    best_values = possible

                    if len(possible) == 1:
                        return r, c, possible

    if best_cell is None:
        return None

    r, c = best_cell

    return r, c, best_values


# --------------------------------------------------
# COUNT SOLUTIONS
# --------------------------------------------------

def count_solutions(board, limit=2):
    """
    Counts Sudoku solutions.

    0 = no solution.
    1 = unique solution.
    2 = at least two solutions.
    """

    if not valid_board(board):
        return 0

    working = [row[:] for row in board]

    def search():

        empty = find_empty(working)

        if empty is None:
            return 1

        r, c, possible_values = empty

        if not possible_values:
            return 0

        total = 0

        for value in possible_values:

            working[r][c] = value

            total += search()

            working[r][c] = 0

            if total >= limit:
                return total

        return total

    return search()


# --------------------------------------------------
# BACKTRACKING
# --------------------------------------------------

def backtracking(board, stats):
    """Recursive Backtracking with MRV."""

    stats["backtracking_nodes"] += 1

    empty = find_empty(board)

    if empty is None:
        return True

    r, c, possible_values = empty

    if not possible_values:
        return False

    for value in possible_values:

        board[r][c] = value

        if backtracking(board, stats):
            return True

        # Undo assignment.
        board[r][c] = 0

    return False


# --------------------------------------------------
# BFS WITH BACKTRACKING
# --------------------------------------------------

def solve_bfs(board):
    """
    Hybrid BFS and Backtracking solver.

    BFS explores the first BFS_DEPTH levels.
    Backtracking completes the search from each frontier state.
    """

    stats = {
        "bfs_nodes": 0,
        "backtracking_nodes": 0
    }

    if not valid_board(board):
        return None, stats

    initial = [row[:] for row in board]

    queue = deque([(initial, 0)])

    while queue:

        current, depth = queue.popleft()
        stats["bfs_nodes"] += 1

        # Switch to Backtracking.
        if depth >= BFS_DEPTH:

            candidate_board = [
                row[:] for row in current
            ]

            if backtracking(candidate_board, stats):
                return candidate_board, stats

            continue

        empty = find_empty(current)

        if empty is None:

            if objective(current) == 0:
                return current, stats

            continue

        r, c, possible_values = empty

        if not possible_values:
            continue

        # Expand the next BFS level.
        for value in possible_values:

            child = [
                row[:] for row in current
            ]

            child[r][c] = value

            if valid_board(child):
                queue.append((child, depth + 1))

    return None, stats


# --------------------------------------------------
# GENERATE COMPLETE SUDOKU
# --------------------------------------------------

def generate_complete_sudoku():
    """Generates a randomized complete valid Sudoku."""

    def pattern(r, c):
        return (
            BOX * (r % BOX) + r // BOX + c
        ) % SIZE

    def shuffled(values):
        return random.sample(values, len(values))

    rows = [
        group * BOX + row
        for group in shuffled(range(BOX))
        for row in shuffled(range(BOX))
    ]

    cols = [
        group * BOX + col
        for group in shuffled(range(BOX))
        for col in shuffled(range(BOX))
    ]

    numbers = shuffled(range(1, SIZE + 1))

    return [
        [
            numbers[pattern(r, c)]
            for c in cols
        ]
        for r in rows
    ]


# --------------------------------------------------
# SUDOKU GENERATOR WITH UNIQUE SOLUTION
# --------------------------------------------------

def generate_sudoku(level, attempts=20):
    """
    Generates a Sudoku with a unique solution.

    Easy: target 35 empty cells.
    Medium: target 45 empty cells.
    Hard: target 55 empty cells.

    Keeps the best unique puzzle across multiple attempts.
    """

    if level not in LEVELS:
        raise ValueError("Choose Easy, Medium or Hard.")

    target = LEVELS[level]

    best_board = None
    best_empty_count = -1

    for attempt in range(attempts):

        board = generate_complete_sudoku()

        positions = random.sample(
            range(SIZE * SIZE),
            SIZE * SIZE
        )

        removed = 0

        for position in positions:

            if removed >= target:
                break

            r = position // SIZE
            c = position % SIZE

            previous_value = board[r][c]

            board[r][c] = 0

            # Keep removal only if solution stays unique.
            if count_solutions(board, limit=2) == 1:
                removed += 1

            else:
                board[r][c] = previous_value

        if removed > best_empty_count:

            best_empty_count = removed
            best_board = [row[:] for row in board]

        if removed == target:
            break

    return best_board


# --------------------------------------------------
# PRINT BOARD
# --------------------------------------------------

def print_board(board):
    """Prints Sudoku with 3x3 separators."""

    for r in range(SIZE):

        if r != 0 and r % BOX == 0:
            print("-" * 21)

        for c in range(SIZE):

            if c != 0 and c % BOX == 0:
                print("|", end=" ")

            value = board[r][c]

            print(
                value if value != 0 else ".",
                end=" "
            )

        print()


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    LEVEL = "Hard"  # Easy, Medium, Hard

    print("SUDOKU SOLVER")
    print("----------------------")

    print(f"Level: {LEVEL}")
    print("Generating Sudoku with a unique solution...")

    generation_start = time.perf_counter()

    board = generate_sudoku(LEVEL)

    generation_time = time.perf_counter() - generation_start

    empty_count = sum(
        row.count(0)
        for row in board
    )

    print(f"Target empty cells: {LEVELS[LEVEL]}")
    print(f"Actual empty cells: {empty_count}")

    print(
        f"Landscape (9^{empty_count}, unconstrained): "
        f"{landscape(empty_count):,}"
    )

    print("\nPuzzle:")
    print_board(board)

    # Check uniqueness.
    print("\nChecking solution uniqueness...")

    uniqueness_start = time.perf_counter()

    number_of_solutions = count_solutions(
        board,
        limit=2
    )

    uniqueness_time = (
        time.perf_counter() - uniqueness_start
    )

    if number_of_solutions == 0:
        print("No solution exists.")

    elif number_of_solutions == 1:
        print("Unique solution.")

    else:
        print("Multiple solutions exist (at least 2).")

    # Solve Sudoku.
    print("\nSearching using BFS with Backtracking...\n")

    start_time = time.perf_counter()

    solution, stats = solve_bfs(board)

    execution_time = time.perf_counter() - start_time

    if solution is not None:

        print("Solution:")
        print_board(solution)

        score = objective(solution)

        print(f"\nf(S) = {score}")

        if score == 0 and valid_board(solution):
            print("Valid Sudoku solution.")
        else:
            print("Invalid Sudoku solution.")

    else:
        print("No solution found.")

    # Performance statistics.
    total_nodes = (
        stats["bfs_nodes"]
        + stats["backtracking_nodes"]
    )

    print("\nSEARCH STATISTICS")
    print("----------------------")

    print(f"BFS nodes: {stats['bfs_nodes']}")

    print(
        f"Backtracking nodes: "
        f"{stats['backtracking_nodes']}"
    )

    print(f"Total nodes: {total_nodes}")

    print(
        f"Generation time: "
        f"{generation_time:.6f} seconds"
    )

    print(
        f"Uniqueness check time: "
        f"{uniqueness_time:.6f} seconds"
    )

    print(
        f"Solving time: "
        f"{execution_time:.6f} seconds"
    )
