"""
Social Golfers Problem - DFS with Backtracking.
Model: X[w][i] = group of player i in week w, domain {0..n_groups-1}.
Constraints: each group has group_size players; each pair shares a
group at most once. Objective f(S) below = 0 iff schedule is valid.
"""

import itertools
import math


def landscape(n_players, group_size, n_groups):
    return math.factorial(n_players) // (
        math.factorial(group_size) ** n_groups * math.factorial(n_groups)
    )


def objective(schedule, n_players, group_size, n_groups):
    f = 0
    seen = {}
    for week in schedule:
        f += abs(len(week) - n_groups)
        for g in week:
            f += abs(len(g) - group_size)

        appearances = {}
        for g in week:
            for p in g:
                appearances[p] = appearances.get(p, 0) + 1
        for p in range(n_players):
            f += abs(appearances.get(p, 0) - 1)

        for g in week:
            for i, j in itertools.combinations(sorted(g), 2):
                seen[(i, j)] = seen.get((i, j), 0) + 1

    for count in seen.values():
        f += max(0, count - 1)
    return f


def social_golfers(n_players, group_size, n_groups, n_weeks):
    assert n_groups * group_size == n_players

    players = list(range(n_players))
    played = [[False] * n_players for _ in range(n_players)]
    schedule = []

    def valid_group(group):
        for i, j in itertools.combinations(group, 2):
            if played[i][j]:
                return False
        return True

    def build_week(remaining, week_groups):
        if not remaining:
            if len(week_groups) == n_groups:
                yield [g[:] for g in week_groups]
            return

        p = remaining[0]
        rest = remaining[1:]

        for g in week_groups:
            if len(g) < group_size:
                g.append(p)
                if valid_group(g):
                    yield from build_week(rest, week_groups)
                g.pop()

        if len(week_groups) < n_groups:
            week_groups.append([p])
            yield from build_week(rest, week_groups)
            week_groups.pop()

    def mark(week_groups, value):
        for g in week_groups:
            for i, j in itertools.combinations(g, 2):
                played[i][j] = played[j][i] = value

    def backtrack(week):
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


def print_schedule(schedule):
    for w, week in enumerate(schedule, 1):
        groups_str = " | ".join(",".join(map(str, g)) for g in week)
        print(f"Week {w}: {groups_str}")


def max_weeks(n_players, group_size, n_groups, max_try=None):
    # Upper bound: w <= (n_players - 1) // (group_size - 1).
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


if __name__ == "__main__":
    N_PLAYERS = 32
    GROUP_SIZE = 4
    N_GROUPS = 8

    print(f"Landscape (1-week search space): {landscape(N_PLAYERS, GROUP_SIZE, N_GROUPS):,}")
    print(f"Upper bound on w: {(N_PLAYERS - 1) // (GROUP_SIZE - 1)}\n")

    print("Searching for the maximum number of weeks (w) with a valid schedule...\n")
    w_max, schedule = max_weeks(N_PLAYERS, GROUP_SIZE, N_GROUPS)

    print(f"\n=== Maximum number of weeks found by this algorithm: w = {w_max} ===\n")
    if schedule:
        print_schedule(schedule)
        print(f"\nf(S) = {objective(schedule, N_PLAYERS, GROUP_SIZE, N_GROUPS)}  (0 = valid solution)")
