"""
Sudoku Solver - BFS with Backtracking.
Model: 81 variables (r,c), domain {1..9} (fixed for givens).
Constraints: all-different per row, column, and 3x3 box.
Objective f(S) below = 0 iff grid is fully filled with no violations.
"""

from collections import deque

SIZE = 9
BOX = 3

VALID_COMPLETE_GRIDS = 6670903752021072936960  # Felgenhauer-Jarvis count


def landscape(empty_cells):
    return 9 ** empty_cells


def objective(board):
    f = 0
    for r in range(SIZE):
        for v in board[r]:
            if v != 0 and not (1 <= v <= 9):
                f += 1  # value outside the valid domain
        row = [v for v in board[r] if v != 0]
        f += len(row) - len(set(row))
    for c in range(SIZE):
        col = [board[r][c] for r in range(SIZE) if board[r][c] != 0]
        f += len(col) - len(set(col))
    for br in range(0, SIZE, BOX):
        for bc in range(0, SIZE, BOX):
            box = [board[r][c] for r in range(br, br + BOX)
                   for c in range(bc, bc + BOX) if board[r][c] != 0]
            f += len(box) - len(set(box))
    f += sum(row.count(0) for row in board)
    return f


def valid_board(board):
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False
    if any(not isinstance(v, int) or not (0 <= v <= 9) for row in board for v in row):
        return False
    return objective(board) == sum(row.count(0) for row in board)  # no conflicts among givens


def find_empty(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return r, c
    return None


def candidates(board, r, c):
    used = set(board[r]) | {board[i][c] for i in range(SIZE)}
    br, bc = BOX * (r // BOX), BOX * (c // BOX)
    used |= {board[i][j] for i in range(br, br + BOX) for j in range(bc, bc + BOX)}
    return [v for v in range(1, 10) if v not in used]


def solve_bfs(board):
    if not valid_board(board):
        return None
    queue = deque([board])
    while queue:
        current = queue.popleft()
        empty = find_empty(current)
        if empty is None:
            if objective(current) == 0:
                return current
            continue  # fully filled but invalid (unreachable for a valid_board() input)
        r, c = empty
        for v in candidates(current, r, c):
            child = [row[:] for row in current]
            child[r][c] = v
            queue.append(child)
    return None


def print_board(board):
    for r in range(SIZE):
        if r % BOX == 0 and r != 0:
            print("-" * 21)
        row = []
        for c in range(SIZE):
            if c % BOX == 0 and c != 0:
                row.append("|")
            row.append(str(board[r][c]) if board[r][c] != 0 else ".")
        print(" ".join(row))


PUZZLES = {
    "Easy": [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    "Medium": [
        [0, 2, 0, 6, 0, 8, 0, 0, 0],
        [5, 8, 0, 0, 0, 9, 7, 0, 0],
        [0, 0, 0, 0, 4, 0, 0, 0, 0],
        [3, 7, 0, 0, 0, 0, 5, 0, 0],
        [6, 0, 0, 0, 0, 0, 0, 0, 4],
        [0, 0, 8, 0, 0, 0, 0, 1, 3],
        [0, 0, 0, 0, 2, 0, 0, 0, 0],
        [0, 0, 9, 8, 0, 0, 0, 3, 6],
        [0, 0, 0, 3, 0, 6, 0, 9, 0],
    ],
    "Hard": [
        [0, 0, 0, 6, 0, 0, 4, 0, 0],
        [7, 0, 0, 0, 0, 3, 6, 0, 0],
        [0, 0, 0, 0, 9, 1, 0, 8, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 5, 0, 1, 8, 0, 0, 0, 3],
        [0, 0, 0, 3, 0, 6, 0, 4, 5],
        [0, 4, 0, 2, 0, 0, 0, 6, 0],
        [9, 0, 3, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 1, 0, 0],
    ],
}


if __name__ == "__main__":
    LEVEL = "Easy"  # change to "Medium" or "Hard"

    board = PUZZLES[LEVEL]
    empty_count = sum(row.count(0) for row in board)

    print(f"Level: {LEVEL}  (empty cells: {empty_count})")
    print(f"Landscape (9^{empty_count}, unconstrained): {landscape(empty_count):,}")
    print(f"Known number of valid 9x9 grids: {VALID_COMPLETE_GRIDS:,}\n")

    print("Puzzle:")
    print_board(board)

    solution = solve_bfs(board)

    print("\nSolution:" if solution else "\nNo solution.")
    if solution:
        print_board(solution)
        print(f"\nf(S) = {objective(solution)}  (0 = valid solution)")
