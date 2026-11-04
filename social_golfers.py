"""
Social Golfers Problem
Depth-First Search (DFS) with Backtracking.

Model:
X[w][i] = group assigned to player i in week w.

Variables:
One variable per (week, player) pair.

Domain:
{0, 1, ..., n_groups - 1}

Constraints:
1. Every group has exactly group_size players.
2. Every two players share a group at most once across all weeks.

Objective:
f(S) = 0 if the schedule is fully valid: correct number of groups,
correct group sizes, every player appears exactly once per week,
and no pair of players repeats a group.
"""

import itertools
import math


# --------------------------------------------------
# LANDSCAPE
# --------------------------------------------------

def landscape(n_players, group_size, n_groups):
    """
    Number of ways to split n_players into n_groups unlabeled
    groups of group_size, for a single week (unconstrained).
    """

    return math.factorial(n_players) // (
        math.factorial(group_size) ** n_groups * math.factorial(n_groups)
    )


# --------------------------------------------------
# OBJECTIVE FUNCTION
# --------------------------------------------------

def objective(schedule, n_players, group_size, n_groups):
    """
    Calculates constraint violations across the whole schedule.
    A fully valid schedule has f(S) = 0.
    """

    f = 0
    seen = {}

    for week in schedule:

        # Check number of groups this week.
        f += abs(len(week) - n_groups)

        # Check group sizes.
        for g in week:
            f += abs(len(g) - group_size)

        # Check every player appears exactly once this week.
        appearances = {}
        for g in week:
            for p in g:
                appearances[p] = appearances.get(p, 0) + 1
        for p in range(n_players):
            f += abs(appearances.get(p, 0) - 1)

        # Record pairs that shared a group this week.
        for g in week:
            for i, j in itertools.combinations(sorted(g), 2):
                seen[(i, j)] = seen.get((i, j), 0) + 1

    # Check repeated pairs across weeks.
    for count in seen.values():
        f += max(0, count - 1)

    return f


# --------------------------------------------------
# DFS WITH BACKTRACKING
# --------------------------------------------------

def social_golfers(n_players, group_size, n_groups, n_weeks):
    """
    Depth-First Search with Backtracking.

    Builds one week at a time (build_week), and backtracks over
    weeks (backtrack) when a week's grouping does not lead to a
    full n_weeks schedule.
    """

    assert n_groups * group_size == n_players

    players = list(range(n_players))
    played = [[False] * n_players for _ in range(n_players)]
    schedule = []

    def valid_group(group):
        """True if no two players in this group have played together before."""

        for i, j in itertools.combinations(group, 2):
            if played[i][j]:
                return False
        return True

    def build_week(remaining, week_groups):
        """
        Backtracking generator: assigns players to groups one at a
        time, trying every existing group and a new group for each
        player, undoing the assignment when it does not lead anywhere.
        """

        if not remaining:
            if len(week_groups) == n_groups:
                yield [g[:] for g in week_groups]
            return

        p = remaining[0]
        rest = remaining[1:]

        # Try adding p to each existing (not yet full) group.
        for g in week_groups:
            if len(g) < group_size:
                g.append(p)
                if valid_group(g):
                    yield from build_week(rest, week_groups)
                g.pop()

        # Try starting a new group with p.
        if len(week_groups) < n_groups:
            week_groups.append([p])
            yield from build_week(rest, week_groups)
            week_groups.pop()

    def mark(week_groups, value):
        """Marks (or unmarks, on backtrack) which pairs played together this week."""

        for g in week_groups:
            for i, j in itertools.combinations(g, 2):
                played[i][j] = played[j][i] = value

    def backtrack(week):
        """DFS over weeks: try every valid grouping, recurse, backtrack on failure."""

        if week == n_weeks:
            return True

        for week_groups in build_week(players[:], []):
            mark(week_groups, True)
            schedule.append(week_groups)

            if backtrack(week + 1):
                return True

            schedule.pop()
            mark(week_groups, False)

        return False

    success = backtrack(0)
    return schedule if success else None


# --------------------------------------------------
# PRINT SCHEDULE
# --------------------------------------------------

def print_schedule(schedule):
    """Prints the schedule, one line per week."""

    for w, week in enumerate(schedule, 1):
        groups_str = " | ".join(",".join(map(str, g)) for g in week)
        print(f"Week {w}: {groups_str}")


# --------------------------------------------------
# MAXIMUM NUMBER OF WEEKS
# --------------------------------------------------

def max_weeks(n_players, group_size, n_groups, max_try=None):
    """
    The assignment asks: for how many weeks can they play?
    Tries w = 1, 2, 3, ... until no solution is found.

    Upper bound: each week a player meets (group_size - 1) new
    players, and there are (n_players - 1) other players total,
    so w <= (n_players - 1) // (group_size - 1).
    """

    if max_try is None:
        max_try = (n_players - 1) // (group_size - 1) if group_size > 1 else n_players - 1

    best_w = 0
    best_schedule = None

    for w in range(1, max_try + 1):
        result = social_golfers(n_players, group_size, n_groups, w)

        if result:
            print(f"  w={w}: solution FOUND")
            best_w = w
            best_schedule = result
        else:
            print(f"  w={w}: NO solution (fully explored)")
            break

    return best_w, best_schedule


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    N_PLAYERS = 32
    GROUP_SIZE = 4
    N_GROUPS = 8

    print("SOCIAL GOLFERS PROBLEM")
    print("----------------------")

    print(f"Landscape (1-week search space): {landscape(N_PLAYERS, GROUP_SIZE, N_GROUPS):,}")
    print(f"Upper bound on w: {(N_PLAYERS - 1) // (GROUP_SIZE - 1)}\n")

    print("Searching for the maximum number of weeks (w) with a valid schedule...\n")
    w_max, schedule = max_weeks(N_PLAYERS, GROUP_SIZE, N_GROUPS)

    print(f"\n=== Maximum number of weeks found by this algorithm: w = {w_max} ===\n")

    if schedule:
        print_schedule(schedule)

        score = objective(schedule, N_PLAYERS, GROUP_SIZE, N_GROUPS)
        print(f"\nf(S) = {score}")
        print("Valid schedule." if score == 0 else "Invalid schedule.")
