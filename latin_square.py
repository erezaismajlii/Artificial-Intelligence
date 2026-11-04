"""
Latin Square - Iterative Deepening DFS (IDDFS) with Backtracking.
Model: n x n grid, X[r][c] in {1..n}, domain {1..n}.
Constraints: all-different per row, all-different per column.
Objective f(S) below = 0 iff grid is fully filled with no violations.
"""

def landscape(n):
    return n ** (n * n)

def objective(board, n):
    f = 0
    f += sum(v != 0 and not (1 <= v <= n) for row in board for v in row)
    for r in range(n):
        row = [v for v in board[r] if v != 0]
        f += len(row) - len(set(row))
    for c in range(n):
        col = [board[r][c] for r in range(n) if board[r][c] != 0]
        f += len(col) - len(set(col))
    f += sum(row.count(0) for row in board)
    return f

def valid_board(board, n):
    if len(board) != n or any(len(row) != n for row in board):
        return False
    if any(not isinstance(v, int) or not (0 <= v <= n) for row in board for v in row):
        return False
    return objective(board, n) == sum(row.count(0) for row in board)

def depth_limited_search(n, board, used_rows, used_cols, pos, limit):
    if pos == limit:
        return [row[:] for row in board] if pos == n * n else None

    r, c = divmod(pos, n)
    for v in range(1, n + 1):
        if v not in used_rows[r] and v not in used_cols[c]:
            board[r][c] = v
            used_rows[r].add(v)
            used_cols[c].add(v)

            result = depth_limited_search(n, board, used_rows, used_cols, pos + 1, limit)
            if result is not None:
                return result

            board[r][c] = 0
            used_rows[r].discard(v)
            used_cols[c].discard(v)
    return None

def solve_iddfs(n):
    board = [[0] * n for _ in range(n)]
    used_rows = [set() for _ in range(n)]
    used_cols = [set() for _ in range(n)]

    for limit in range(1, n * n + 1):
        result = depth_limited_search(n, board, used_rows, used_cols, 0, limit)
        if result is not None:
            return result
    return None

def print_board(board):
    for row in board:
        print(" ".join(str(v) for v in row))

if __name__ == "__main__":
    N = 5

    print(f"n = {N}")
    print(f"Landscape (n^(n^2), unconstrained): {landscape(N):,}\n")

    solution = solve_iddfs(N)

    print("Solution:" if solution else "No solution.")
    if solution:
        print_board(solution)
        print(f"\nf(S) = {objective(solution, N)}  (0 = valid solution)")
