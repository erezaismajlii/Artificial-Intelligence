"""
Search Trees - 8-Puzzle, Missionaries and Cannibals, Rotating Workforce Scheduling.
"""

def print_search_tree(initial, successors, goal_test, max_depth, forbid_reverse=True):
    count = 0

    def rec(state, depth, prev_state):
        nonlocal count
        count += 1
        marker = " [GOAL]" if goal_test(state) else ""
        print("  " * depth + str(state) + marker)
        if goal_test(state) or depth >= max_depth:
            return
        for action, child in successors(state):
            if forbid_reverse and child == prev_state:
                continue
            print("  " * depth + f"  ({action})")
            rec(child, depth + 1, state)

    rec(initial, 0, None)
    return count


# ---------------- 8-Puzzle ----------------

GOAL_8PUZZLE = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def objective_8puzzle(state):
    # f(S) = number of misplaced tiles (0 excluded). f(S) = 0 <=> state == GOAL.
    return sum(1 for i, v in enumerate(state) if v != 0 and v != GOAL_8PUZZLE[i])


def successors_8puzzle(state):
    idx = state.index(0)
    r, c = divmod(idx, 3)
    moves = []
    if r > 0:
        moves.append(("UP", idx - 3))
    if r < 2:
        moves.append(("DOWN", idx + 3))
    if c > 0:
        moves.append(("LEFT", idx - 1))
    if c < 2:
        moves.append(("RIGHT", idx + 1))

    results = []
    for label, j in moves:
        new = list(state)
        new[idx], new[j] = new[j], new[idx]
        results.append((label, tuple(new)))
    return results


def goal_8puzzle(state):
    return state == GOAL_8PUZZLE


# ---------------- Missionaries and Cannibals ----------------

def successors_mc(state):
    m, c, boat = state
    moves = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]
    results = []
    for dm, dc in moves:
        if boat == "L":
            nm, nc, nb = m - dm, c - dc, "R"
        else:
            nm, nc, nb = m + dm, c + dc, "L"

        if not (0 <= nm <= 3 and 0 <= nc <= 3):
            continue
        rm, rc = 3 - nm, 3 - nc
        if nm > 0 and nm < nc:
            continue
        if rm > 0 and rm < rc:
            continue

        label = f"{boat}->{'R' if boat == 'L' else 'L'}: {dm}M{dc}C"
        results.append((label, (nm, nc, nb)))
    return results


def goal_mc(state):
    return state == (0, 0, "R")


# ---------------- Rotating Workforce Scheduling ----------------
# Simplified instance: assign one worker's shifts over DAYS days,
# shifts in {M, E, N, O(ff)}. Constraints: no M right after N (rest),
# and no 3 consecutive working shifts without an O.

WF_DAYS = 4
WF_SHIFTS = ["M", "E", "N", "O"]


def successors_wf(state):
    results = []
    last = state[-1] if state else None
    last2_working = len(state) >= 2 and state[-1] != "O" and state[-2] != "O"

    for s in WF_SHIFTS:
        if last == "N" and s == "M":
            continue
        if last2_working and s != "O":
            continue
        results.append((s, state + (s,)))
    return results


def goal_wf(state):
    return len(state) == WF_DAYS

if __name__ == "__main__":
    print("=== 8-Puzzle ===")
    initial_8 = (1, 2, 3, 4, 5, 6, 7, 0, 8)  # one move away from GOAL_8PUZZLE
    print(f"f(initial) = {objective_8puzzle(initial_8)}  (0 = goal)")
    n = print_search_tree(initial_8, successors_8puzzle, goal_8puzzle, max_depth=3)
    print(f"Nodes printed: {n}\n")

    print("=== Missionaries and Cannibals ===")
    initial_mc = (3, 3, "L")
    n = print_search_tree(initial_mc, successors_mc, goal_mc, max_depth=11)
    print(f"Nodes printed: {n}\n")

    print("=== Rotating Workforce Scheduling ===")
    initial_wf = ()
    n = print_search_tree(initial_wf, successors_wf, goal_wf, max_depth=WF_DAYS, forbid_reverse=False)
    print(f"Nodes printed: {n}")
