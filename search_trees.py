"""
SEARCH TREES
8-Puzzle, Missionaries and Cannibals, Rotating Workforce Scheduling.

For each problem the search tree is constructed and printed in DFS
order (indentation = depth, action shown in parentheses). Full trees
grow combinatorially, so each tree is printed only up to a limited
depth; count_nodes() reports the exact number of nodes per level up
to that depth without printing them, using the same stopping rule as
print_search_tree (stop expanding a branch once its goal test succeeds
or the depth limit is reached) so the two stay consistent.
"""


def print_search_tree(initial, successors, goal_test, max_depth, forbid_reverse=True):
    """Prints the search tree in DFS order, indented by depth."""
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


def count_nodes(initial, successors, goal_test, max_depth, forbid_reverse=True):
    """
    Number of search-tree nodes per level, up to max_depth (no printing).
    Uses the same stopping rule as print_search_tree: a branch stops
    expanding once goal_test(state) is True or depth >= max_depth, so
    the counts always match what print_search_tree would print.
    """
    per_level = [0] * (max_depth + 1)

    def rec(state, depth, prev):
        per_level[depth] += 1
        if goal_test(state) or depth >= max_depth:
            return
        for _, child in successors(state):
            if forbid_reverse and child == prev:
                continue
            rec(child, depth + 1, state)

    rec(initial, 0, None)
    return per_level


# ==================================================
# 8-PUZZLE
# ==================================================
"""
MODEL:
State = tuple of 9 values, read row-major (0 = blank tile).

VARIABLES:
The state itself; no separate variables beyond the 9 tile positions.

DOMAIN:
{0, 1, ..., 8}, each value appearing exactly once in the state.

ACTIONS:
UP, DOWN, LEFT, RIGHT - move the blank tile.

OBJECTIVE FUNCTION:
f(S) = number of tiles (blank excluded) out of place.
f(S) = 0  <=>  state == GOAL.

LANDSCAPE:
9! = 362,880 distinct arrangements (unconstrained permutations of 9 tiles).
"""

GOAL_8PUZZLE = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def objective_8puzzle(state):
    """f(S) = number of misplaced tiles (0 excluded). f(S) = 0 <=> goal."""
    return sum(1 for i, v in enumerate(state) if v != 0 and v != GOAL_8PUZZLE[i])


def successors_8puzzle(state):
    """Returns the (action, child state) pairs reachable by moving the blank."""
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


# ==================================================
# MISSIONARIES AND CANNIBALS
# ==================================================
"""
MODEL:
State = (missionaries on the left bank, cannibals on the left bank,
boat position L/R). 3 missionaries and 3 cannibals in total.

VARIABLES:
The state itself: missionaries_left, cannibals_left, boat_side.

DOMAIN:
missionaries_left, cannibals_left in {0, 1, 2, 3}; boat_side in {L, R}.

CONSTRAINTS:
On neither bank may cannibals outnumber missionaries, whenever
missionaries are present on that bank.

ACTIONS:
Move 1 missionary, 2 missionaries, 1 cannibal, 2 cannibals, or
1 of each, across the river by boat.

OBJECTIVE FUNCTION (goal test):
f(S) = 0  <=>  state == (0, 0, "R")  (everyone moved to the right bank).

LANDSCAPE:
4 x 4 x 2 = 32 raw combinations of (missionaries_left, cannibals_left,
boat_side); far fewer are reachable once the constraint is applied.
"""


def successors_mc(state):
    """Returns the (action, child state) pairs reachable by one boat trip."""
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


# ==================================================
# ROTATING WORKFORCE SCHEDULING
# ==================================================
"""
MODEL:
"Rotating" workforce scheduling means the opposite of giving each
worker an independent schedule: there is ONE shared cyclic pattern
of RWS_DAYS = 7 * RWS_WEEKS days, and each of the RWS_WEEKS workers
is offset onto this same cycle by a different starting week. Worker k
experiences days S[7k], S[7k+1], ..., wrapping around the cycle.
Because all workers follow the same cyclic pattern with different
starting offsets, the same transition constraints apply throughout
the entire 21-day cycle, including the wraparound from the last day
to the first day - so a single cyclic sequence with wraparound
constraints is the correct model, not RWS_WEEKS separate independent
7-day sequences.

VARIABLES:
S[0], S[1], ..., S[RWS_DAYS - 1]: one shift per day of the cycle.

DOMAIN:
{D (day), A (afternoon), N (night), O (off)}.

CONSTRAINTS:
1. Forbidden transitions: N->D, N->A, A->D (not enough rest between
   consecutive shifts).
2. At most MAX_CONSEC_WORK working days in a row without a day off.
3. Coverage: every day of the week (0..6) must have at least one
   worker on D and one on A, across the RWS_WEEKS workers in the cycle.
4. The cyclic wrap (last day -> first day) must also not be a
   forbidden transition.

OBJECTIVE FUNCTION:
f(S) = (# forbidden transitions among consecutive days actually
        assigned, plus the cyclic wrap once the state is complete)
       + (# weekdays missing D or A coverage, evaluated only once
          the state is complete, since coverage over an incomplete
          cycle is not yet meaningful).
f(S) = 0  <=>  valid schedule. Accepts partial (even empty) states.

LANDSCAPE:
L = len(RWS_SHIFTS) ^ RWS_DAYS = 4 ^ RWS_DAYS, unconstrained.
"""

RWS_WEEKS = 3
RWS_DAYS = 7 * RWS_WEEKS
RWS_SHIFTS = ["D", "A", "N", "O"]
FORBIDDEN = {("N", "D"), ("N", "A"), ("A", "D")}
MAX_CONSEC_WORK = 5


def successors_rws(state):
    """Returns the (action, child state) pairs reachable by assigning the next day's shift."""
    out = []
    for s in RWS_SHIFTS:
        if state and (state[-1], s) in FORBIDDEN:
            continue
        run = 0
        for x in reversed(state):
            if x == "O":
                break
            run += 1
        if s != "O" and run + 1 > MAX_CONSEC_WORK:
            continue
        out.append((s, state + (s,)))
    return out


def cyclic_consec_work_excess(state):
    """
    Counts, for a FULL (length RWS_DAYS) state treated as a cycle, how many
    working days exceed MAX_CONSEC_WORK in any run - including a run that
    wraps from the end of the array back to the start (e.g. 3 working days
    at the end + 4 at the start, with no 'O' in between, is one 7-day run).
    Returns 0 iff every cyclic run of working days has length <= MAX_CONSEC_WORK.
    """
    n = len(state)
    if "O" not in state:
        # No day off anywhere in the cycle: the whole cycle is one run.
        return max(0, n - MAX_CONSEC_WORK)

    # Rotate so the array starts right after an 'O' - this turns the
    # cyclic run-length problem into a simple linear scan.
    o_idx = state.index("O")
    rotated = state[o_idx + 1:] + state[:o_idx + 1]

    excess = 0
    run = 0
    for s in rotated:
        if s == "O":
            run = 0
        else:
            run += 1
            if run > MAX_CONSEC_WORK:
                excess += 1
    return excess


def goal_rws(state):
    """Goal test: full cycle length, cyclic wrap valid, cyclic work-run limit, D/A coverage."""
    if len(state) != RWS_DAYS:
        return False
    if (state[-1], state[0]) in FORBIDDEN:      # cyclic constraint
        return False
    if cyclic_consec_work_excess(state) > 0:
        return False
    for d in range(7):
        col = [state[7 * w + d] for w in range(RWS_WEEKS)]
        if "D" not in col or "A" not in col:
            return False
    return True


def objective_rws(state):
    """
    f(S) = # forbidden transitions among consecutive assigned days
    (+ the cyclic wrap once the state is complete)
    + # weekdays missing D/A coverage (checked only once complete)
    + # days exceeding the cyclic max-consecutive-work-days limit
      (checked only once complete, since the run can wrap around).
    Safe to call on a partial or even empty state.
    """
    n = len(state)
    if n == 0:
        return 0

    f = sum((state[i], state[i + 1]) in FORBIDDEN for i in range(n - 1))

    if n == RWS_DAYS:
        f += (state[-1], state[0]) in FORBIDDEN  # cyclic wrap
        f += cyclic_consec_work_excess(state)
        for d in range(7):
            col = [state[7 * w + d] for w in range(RWS_WEEKS)]
            f += ("D" not in col) + ("A" not in col)

    return f


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("=== 8-PUZZLE ===")
    init8 = (1, 2, 3, 0, 5, 6, 4, 7, 8)      # 3 moves away from the goal
    print(f"f(initial) = {objective_8puzzle(init8)}  (0 = goal)")
    n = print_search_tree(init8, successors_8puzzle, goal_8puzzle, max_depth=3)
    print(f"Nodes printed: {n}")
    print("Nodes per level (no reverse moves), depth 0..10:",
          count_nodes(init8, successors_8puzzle, goal_8puzzle, 10), "\n")

    print("=== MISSIONARIES AND CANNIBALS ===")
    n = print_search_tree((3, 3, "L"), successors_mc, goal_mc, max_depth=11)
    print(f"Nodes printed: {n}")
    print("Nodes per level, depth 0..11:",
          count_nodes((3, 3, "L"), successors_mc, goal_mc, 11), "\n")

    print("=== ROTATING WORKFORCE SCHEDULING (3 workers, 21-day cycle) ===")
    print_search_tree((), successors_rws, goal_rws, max_depth=3, forbid_reverse=False)
    print("Nodes per level, depth 0..8:",
          count_nodes((), successors_rws, goal_rws, 8, forbid_reverse=False))
    print(f"Unconstrained landscape: 4^{RWS_DAYS} = {4 ** RWS_DAYS:,}")
