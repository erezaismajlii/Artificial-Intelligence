
"""
Latin Square Problem
Iterative Deepening Depth First Search (IDDFS)
with Backtracking.

Model:
X[r][c] = value assigned to cell (r, c).

Variables:
All cells in an n x n grid.

Domain:
{1, 2, ..., n}

Constraints:
1. Every row contains each number exactly once.
2. Every column contains each number exactly once.

Objective:
f(S) = 0 if the board is completely filled
and all row and column constraints are satisfied.
"""

# --------------------------------------------------
# GLOBAL COUNTERS
# --------------------------------------------------

visited_nodes = 0
iterations = 0


# --------------------------------------------------
# LANDSCAPE
# --------------------------------------------------

def landscape(n):
    """
    Number of possible assignments without constraints.
    Each of n*n cells has n possible values.
    """

    return n ** (n * n)


# --------------------------------------------------
# OBJECTIVE FUNCTION
# --------------------------------------------------

def objective(board, n):
    """
    Calculates constraint violations and empty cells.
    A complete valid Latin Square has f(S) = 0.
    """

    f = 0

    # Check invalid values.
    for row in board:
        for value in row:
            if value != 0 and not (1 <= value <= n):
                f += 1

    # Check duplicate values in rows.
    for r in range(n):
        values = [v for v in board[r] if v != 0]
        f += len(values) - len(set(values))

    # Check duplicate values in columns.
    for c in range(n):
        values = [
            board[r][c]
            for r in range(n)
            if board[r][c] != 0
        ]

        f += len(values) - len(set(values))

    # Count empty cells.
    f += sum(row.count(0) for row in board)

    return f


# --------------------------------------------------
# BOARD VALIDATION
# --------------------------------------------------

def valid_board(board, n):
    """
    Checks board dimensions, values and constraints.
    Partial boards are also accepted.
    """

    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        return False

    if len(board) != n:
        return False

    if any(len(row) != n for row in board):
        return False

    for row in board:
        for value in row:

            if not isinstance(value, int) or isinstance(value, bool):
                return False

            if not (0 <= value <= n):
                return False

    empty_cells = sum(row.count(0) for row in board)

    return objective(board, n) == empty_cells


# --------------------------------------------------
# DEPTH-LIMITED DFS WITH BACKTRACKING
# --------------------------------------------------

def depth_limited_search(
    n,
    board,
    used_rows,
    used_cols,
    pos,
    limit
):
    """
    Depth-Limited DFS with Backtracking.

    The first row is fixed to 1, 2, ..., n
    to eliminate equivalent solutions caused by
    symbol permutations.
    """

    global visited_nodes

    visited_nodes += 1

    # Goal test.
    if pos == n * n:

        if objective(board, n) == 0:
            return [row[:] for row in board]

        return None

    # Stop when the depth limit is reached.
    if pos >= limit:
        return None

    # Convert position into row and column.
    r, c = divmod(pos, n)

    # Try every value in the domain.
    for value in range(1, n + 1):

        # Fix the first row to 1, 2, ..., n.
        if r == 0 and value != c + 1:
            continue

        # Check row and column constraints.
        if (
            value not in used_rows[r]
            and value not in used_cols[c]
        ):

            # Assign value.
            board[r][c] = value
            used_rows[r].add(value)
            used_cols[c].add(value)

            # Recursive DFS.
            result = depth_limited_search(
                n,
                board,
                used_rows,
                used_cols,
                pos + 1,
                limit
            )

            if result is not None:
                return result

            # Backtracking.
            board[r][c] = 0
            used_rows[r].remove(value)
            used_cols[c].remove(value)

    return None


# --------------------------------------------------
# IDDFS
# --------------------------------------------------

def solve_iddfs(n):
    """
    Iterative Deepening Depth First Search.

    Increases the depth limit until a solution is found.
    """

    global visited_nodes, iterations

    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("n must be a positive integer.")

    # Reset counters.
    visited_nodes = 0
    iterations = 0

    # Initialize empty board.
    board = [[0] * n for _ in range(n)]

    # Track used values in rows and columns.
    used_rows = [set() for _ in range(n)]
    used_cols = [set() for _ in range(n)]

    # Iterative Deepening.
    for limit in range(1, n * n + 1):

        iterations += 1

        result = depth_limited_search(
            n,
            board,
            used_rows,
            used_cols,
            0,
            limit
        )

        if result is not None:
            return result

    return None


# --------------------------------------------------
# PRINT BOARD
# --------------------------------------------------

def print_board(board):
    """
    Prints the Latin Square.
    """

    for row in board:
        print(" ".join(map(str, row)))


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    N = 5

    print("LATIN SQUARE")
    print("----------------------")

    print(f"n = {N}")

    print(
        f"Landscape (n^(n^2)): "
        f"{landscape(N):,}"
    )

    print("\nSearching using IDDFS with Backtracking...\n")

    solution = solve_iddfs(N)

    if solution is not None:

        print("Solution:")
        print_board(solution)

        score = objective(solution, N)

        print(f"\nf(S) = {score}")

        if score == 0 and valid_board(solution, N):
            print("Valid Latin Square.")
        else:
            print("Invalid Latin Square.")

    else:
        print("No solution found.")

    print(f"\nVisited nodes: {visited_nodes:,}")
    print(f"Iterations: {iterations}")
