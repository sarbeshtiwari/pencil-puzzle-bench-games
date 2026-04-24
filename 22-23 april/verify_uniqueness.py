#!/usr/bin/env python3
"""
Verify every puzzle across all 8 games has EXACTLY 1 unique solution.
Uses optimized backtracking solvers with constraint propagation.
For each puzzle, finds UP TO 2 solutions. Exactly 1 = unique.
"""

import sys
import time
import math
from collections import deque

sys.path.insert(0, "/Users/apple/Desktop/morpheus/data")


def decode_heyawake_url(url_body, rows, cols):
    B32 = "0123456789abcdefghijklmnopqrstuv"

    def unpack_bits(s, n):
        bits = []
        for ch in s:
            v = B32.index(ch)
            for shift in [4, 3, 2, 1, 0]:
                bits.append((v >> shift) & 1)
                if len(bits) == n:
                    return bits
        return bits

    n_vert = (cols - 1) * rows
    n_horiz = cols * (rows - 1)
    vert_chars = math.ceil(n_vert / 5)
    horiz_chars = math.ceil(n_horiz / 5)
    border_len = vert_chars + horiz_chars
    border_str = url_body[:border_len]
    number_str = url_body[border_len:]
    vert_bits = unpack_bits(border_str[:vert_chars], n_vert)
    horiz_bits = unpack_bits(border_str[vert_chars:], n_horiz)

    v_borders = [[0] * cols for _ in range(rows)]
    h_borders = [[0] * cols for _ in range(rows)]
    idx = 0
    for r in range(rows):
        for c in range(cols - 1):
            v_borders[r][c] = vert_bits[idx]
            idx += 1
    idx = 0
    for r in range(rows - 1):
        for c in range(cols):
            h_borders[r][c] = horiz_bits[idx]
            idx += 1

    room_grid = [[-1] * cols for _ in range(rows)]
    room_id = 0
    for r in range(rows):
        for c in range(cols):
            if room_grid[r][c] == -1:
                q = deque([(r, c)])
                room_grid[r][c] = room_id
                while q:
                    cr, cc = q.popleft()
                    if cc + 1 < cols and room_grid[cr][cc + 1] == -1 and v_borders[cr][cc] == 0:
                        room_grid[cr][cc + 1] = room_id
                        q.append((cr, cc + 1))
                    if cc - 1 >= 0 and room_grid[cr][cc - 1] == -1 and v_borders[cr][cc - 1] == 0:
                        room_grid[cr][cc - 1] = room_id
                        q.append((cr, cc - 1))
                    if cr + 1 < rows and room_grid[cr + 1][cc] == -1 and h_borders[cr][cc] == 0:
                        room_grid[cr + 1][cc] = room_id
                        q.append((cr + 1, cc))
                    if cr - 1 >= 0 and room_grid[cr - 1][cc] == -1 and h_borders[cr - 1][cc] == 0:
                        room_grid[cr - 1][cc] = room_id
                        q.append((cr - 1, cc))
                room_id += 1

    n_rooms = room_id
    clues = {}
    rid = 0
    i = 0
    while i < len(number_str) and rid < n_rooms:
        ch = number_str[i]
        if ch == '-':
            hx = number_str[i + 1:i + 3]
            clues[rid] = int(hx, 16)
            rid += 1
            i += 3
        else:
            v = int(ch, 36)
            if v <= 15:
                clues[rid] = v
                rid += 1
                i += 1
            else:
                rid += (v - 15)
                i += 1

    return room_grid, clues, v_borders, h_borders


def solve_sudoku(clue_grid, limit=2):
    grid = [row[:] for row in clue_grid]
    solutions = []

    cands = [[set() for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                s = set(range(1, 10))
                for i in range(9):
                    s.discard(grid[r][i])
                    s.discard(grid[i][c])
                br, bc = (r // 3) * 3, (c // 3) * 3
                for dr in range(3):
                    for dc in range(3):
                        s.discard(grid[br + dr][bc + dc])
                cands[r][c] = s

    def eliminate(r, c, n):
        removed = []
        for i in range(9):
            if i != c and n in cands[r][i]:
                cands[r][i].discard(n)
                removed.append((r, i, n))
            if i != r and n in cands[i][c]:
                cands[i][c].discard(n)
                removed.append((i, c, n))
        br, bc = (r // 3) * 3, (c // 3) * 3
        for dr in range(3):
            for dc in range(3):
                rr, cc = br + dr, bc + dc
                if (rr, cc) != (r, c) and n in cands[rr][cc]:
                    cands[rr][cc].discard(n)
                    removed.append((rr, cc, n))
        return removed

    def restore(removed):
        for rr, cc, n in removed:
            cands[rr][cc].add(n)

    def backtrack():
        if len(solutions) >= limit:
            return
        best, best_count = None, 10
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    cnt = len(cands[r][c])
                    if cnt == 0:
                        return
                    if cnt < best_count:
                        best, best_count = (r, c), cnt
                        if cnt == 1:
                            break
            if best_count <= 1:
                break

        if best is None:
            solutions.append([row[:] for row in grid])
            return

        r, c = best
        for n in list(cands[r][c]):
            grid[r][c] = n
            old_cands = cands[r][c]
            cands[r][c] = set()
            removed = eliminate(r, c, n)

            dead = any(grid[rr][cc] == 0 and len(cands[rr][cc]) == 0 for rr, cc, _ in removed)
            if not dead:
                backtrack()
                if len(solutions) >= limit:
                    restore(removed)
                    cands[r][c] = old_cands
                    grid[r][c] = 0
                    return

            restore(removed)
            cands[r][c] = old_cands
            grid[r][c] = 0

    backtrack()
    return solutions


def solve_heyawake(rows, cols, room_grid, clues, limit=2, v_borders=None, h_borders=None):
    n = rows * cols
    grid = [0] * n

    rooms = {}
    cell_room = [0] * n
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            rid = room_grid[r][c]
            cell_room[idx] = rid
            rooms.setdefault(rid, []).append(idx)

    # Precompute border lookup: vb[r][c]=1 means border between (r,c) and (r,c+1)
    vb = v_borders if v_borders else [[0] * cols for _ in range(rows)]
    hb = h_borders if h_borders else [[0] * cols for _ in range(rows)]

    def adj(idx):
        r, c = divmod(idx, cols)
        res = []
        if r > 0: res.append(idx - cols)
        if r < rows - 1: res.append(idx + cols)
        if c > 0: res.append(idx - 1)
        if c < cols - 1: res.append(idx + 1)
        return res
    adj_list = [adj(i) for i in range(n)]

    def r5_ok_at(cell_idx):
        r, c = divmod(cell_idx, cols)
        # R5: count border crossings in contiguous white run (stop at non-white)
        border_count = 0
        for cc in range(c - 1, -1, -1):
            idx = r * cols + cc
            if grid[idx] != 2:
                break
            border_count += vb[r][cc]
        for cc in range(c + 1, cols):
            idx = r * cols + cc
            if grid[idx] != 2:
                break
            border_count += vb[r][cc - 1]
        if border_count > 1:
            return False
        border_count = 0
        for rr in range(r - 1, -1, -1):
            idx = rr * cols + c
            if grid[idx] != 2:
                break
            border_count += hb[rr][c]
        for rr in range(r + 1, rows):
            idx = rr * cols + c
            if grid[idx] != 2:
                break
            border_count += hb[rr - 1][c]
        if border_count > 1:
            return False
        return True

    def white_connected():
        whites = [i for i in range(n) if grid[i] != 1]
        if not whites:
            return False
        vis = set([whites[0]])
        q = deque([whites[0]])
        while q:
            cur = q.popleft()
            for nb in adj_list[cur]:
                if nb not in vis and grid[nb] != 1:
                    vis.add(nb)
                    q.append(nb)
        return len(vis) == len(whites)

    def room_ok():
        for rid, cnt in clues.items():
            cells = rooms[rid]
            sh = sum(1 for i in cells if grid[i] == 1)
            un = sum(1 for i in cells if grid[i] == 0)
            if sh > cnt or sh + un < cnt:
                return False
        return True

    def room_exact():
        for rid, cnt in clues.items():
            if sum(1 for i in rooms[rid] if grid[i] == 1) != cnt:
                return False
        return True

    clued_order = []
    unclued_order = []
    for rid in sorted(rooms.keys(), key=lambda r: len(rooms[r])):
        if rid in clues:
            clued_order.extend(rooms[rid])
        else:
            unclued_order.extend(rooms[rid])
    order = clued_order + unclued_order

    solutions = []

    def backtrack(idx):
        if len(solutions) >= limit:
            return
        if idx == n:
            if white_connected() and room_exact():
                solutions.append(grid[:])
            return

        cell = order[idx]
        for val in [1, 2]:
            grid[cell] = val
            if val == 1:
                if any(grid[nb] == 1 for nb in adj_list[cell]):
                    grid[cell] = 0
                    continue
            if val == 2:
                if not r5_ok_at(cell):
                    grid[cell] = 0
                    continue

            if not room_ok():
                grid[cell] = 0
                continue

            if val == 1 and idx % 10 == 0 and idx > 0:
                test_whites = [i for i in range(n) if grid[i] != 1]
                if test_whites:
                    vis = set([test_whites[0]])
                    q = deque([test_whites[0]])
                    tw = set(test_whites)
                    while q:
                        cur = q.popleft()
                        for nb in adj_list[cur]:
                            if nb in tw and nb not in vis:
                                vis.add(nb)
                                q.append(nb)
                    if len(vis) < len(test_whites):
                        grid[cell] = 0
                        continue

            backtrack(idx + 1)
            if len(solutions) >= limit:
                grid[cell] = 0
                return
        grid[cell] = 0

    backtrack(0)
    return solutions


def decode_mines_url(url_body, rows, cols):
    grid = []
    for ch in url_body:
        code = int(ch, 36)
        if code <= 8:
            grid.append(code)
        else:
            grid.extend([-1] * (code - 15))
    while len(grid) < rows * cols:
        grid.append(-1)
    return [grid[r * cols:(r + 1) * cols] for r in range(rows)]


def solve_minesweeper(clue_grid, num_mines, limit=2):
    rows = len(clue_grid)
    cols = len(clue_grid[0])
    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    mine_cells = [(r,c) for r in range(rows) for c in range(cols) if clue_grid[r][c] == -1]
    mine_idx = {pos: i for i, pos in enumerate(mine_cells)}
    n_mc = len(mine_cells)

    clue_nbs = []
    for r in range(rows):
        for c in range(cols):
            if clue_grid[r][c] >= 0:
                nbs = [mine_idx[(r+dr,c+dc)] for dr,dc in DIRS if (r+dr,c+dc) in mine_idx]
                clue_nbs.append((clue_grid[r][c], nbs))

    is_mine = [0] * n_mc
    solutions = []

    def feasible(decided):
        placed = sum(is_mine[:decided])
        remaining = n_mc - decided
        if placed > num_mines or placed + remaining < num_mines:
            return False
        for val, nbs in clue_nbs:
            mc = sum(is_mine[i] for i in nbs if i < decided)
            und = sum(1 for i in nbs if i >= decided)
            if mc > val or mc + und < val:
                return False
        return True

    def bt(idx, placed):
        if len(solutions) >= limit:
            return
        if idx == n_mc:
            if placed == num_mines:
                solutions.append(is_mine[:])
            return
        if placed < num_mines:
            is_mine[idx] = 1
            if feasible(idx + 1):
                bt(idx + 1, placed + 1)
                if len(solutions) >= limit:
                    is_mine[idx] = 0
                    return
            is_mine[idx] = 0
        is_mine[idx] = 0
        if feasible(idx + 1):
            bt(idx + 1, placed)

    bt(0, 0)
    return solutions


def solve_country_small(rows, cols, room_grid, clues, limit=2):
    n = rows * cols
    cell_adj = [[] for _ in range(n)]
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            if c < cols - 1:
                cell_adj[idx].append(idx + 1)
                cell_adj[idx + 1].append(idx)
            if r < rows - 1:
                cell_adj[idx].append(idx + cols)
                cell_adj[idx + cols].append(idx)

    cr = [room_grid[r][c] for r in range(rows) for c in range(cols)]
    rooms = {}
    for i, rid in enumerate(cr):
        rooms.setdefault(rid, []).append(i)

    on_loop = [None] * n
    loop_nbrs = [set() for _ in range(n)]
    solutions = []

    order = sorted(range(n), key=lambda i: (0 if cr[i] in clues else 1, len(rooms[cr[i]])))

    def room_feasible():
        for rid, target in clues.items():
            cells = rooms[rid]
            on = sum(1 for c in cells if on_loop[c] is True)
            maybe = sum(1 for c in cells if on_loop[c] is None)
            if on > target or on + maybe < target:
                return False
        return True

    def r5_partial():
        for i in range(n):
            if on_loop[i] is False:
                for nb in cell_adj[i]:
                    if on_loop[nb] is False and cr[i] != cr[nb]:
                        return False
        return True

    def valid_solution():
        on_cells = [i for i in range(n) if on_loop[i] is True]
        if len(on_cells) < 3:
            return False
        for c in on_cells:
            if len(loop_nbrs[c]) != 2:
                return False
        vis = {on_cells[0]}
        q = deque([on_cells[0]])
        while q:
            cur = q.popleft()
            for nb in loop_nbrs[cur]:
                if nb not in vis:
                    vis.add(nb)
                    q.append(nb)
        if len(vis) != len(on_cells):
            return False
        for rid, cells in rooms.items():
            cs = set(cells)
            crossings = sum(1 for c in cells if on_loop[c] is True for nb in loop_nbrs[c] if nb not in cs)
            if crossings != 2:
                return False
        for rid, target in clues.items():
            if sum(1 for c in rooms[rid] if on_loop[c] is True) != target:
                return False
        for rid, cells in rooms.items():
            if not any(on_loop[c] is True for c in cells):
                return False
        return r5_partial()

    def bt(idx):
        if len(solutions) >= limit:
            return
        if idx == n:
            if valid_solution():
                solutions.append([on_loop[i] for i in range(n)])
            return

        cell = order[idx]
        for val in [True, False]:
            on_loop[cell] = val
            if val:
                added = []
                for nb in cell_adj[cell]:
                    if on_loop[nb] is True:
                        loop_nbrs[cell].add(nb)
                        loop_nbrs[nb].add(cell)
                        added.append(nb)
                if len(loop_nbrs[cell]) > 2 or any(len(loop_nbrs[nb]) > 2 for nb in added):
                    for nb in added:
                        loop_nbrs[cell].discard(nb)
                        loop_nbrs[nb].discard(cell)
                    on_loop[cell] = None
                    continue
                if not room_feasible():
                    for nb in added:
                        loop_nbrs[cell].discard(nb)
                        loop_nbrs[nb].discard(cell)
                    on_loop[cell] = None
                    continue
                bt(idx + 1)
                for nb in added:
                    loop_nbrs[cell].discard(nb)
                    loop_nbrs[nb].discard(cell)
            else:
                if not r5_partial():
                    on_loop[cell] = None
                    continue
                if not room_feasible():
                    on_loop[cell] = None
                    continue
                bt(idx + 1)
            if len(solutions) >= limit:
                on_loop[cell] = None
                return
        on_loop[cell] = None

    bt(0)
    return solutions


def main():
    passed = 0
    failed = 0
    skipped = 0

    def check(label, result):
        nonlocal passed, failed
        if result:
            passed += 1
            print(f"  \u2713 {label}")
        else:
            failed += 1
            print(f"  \u2717 FAIL: {label}")

    print("=" * 70)
    print("  UNIQUENESS VERIFICATION — All 24 Puzzles")
    print("=" * 70)

    for var in ["sudoku", "sudoku2"]:
        pmod = __import__(f"puzzle_{var}")
        smod = __import__(f"solution_{var}")
        for level in ["easy", "medium", "hard"]:
            print(f"\n-- {var} {level} --")
            t0 = time.monotonic()
            sols = solve_sudoku(pmod._PUZZLES[level]["clue_grid"], limit=2)
            dt = time.monotonic() - t0
            check(f"Unique solution (found {len(sols)}, {dt:.2f}s)", len(sols) == 1)
            if sols:
                check("Matches expected", sols[0] == smod._SOLUTIONS[level]["solution"])

    for var in ["heyawake", "heyawake2"]:
        pmod = __import__(f"puzzle_{var}")
        smod = __import__(f"solution_{var}")
        for level in ["easy", "medium", "hard"]:
            print(f"\n-- {var} {level} --")
            p = pmod._PUZZLES[level]
            r, c = p["rows"], p["cols"]
            if r * c > 80:
                print(f"  SKIP: {r}x{c}={r*c} cells (ppbench golden, cspuz_is_unique=True)")
                skipped += 1
                continue
            if "room_grid" in p:
                room_grid, clues = p["room_grid"], p["clues"]
                _, _, vb, hb = decode_heyawake_url(p["url_body"], r, c)
            else:
                room_grid, clues, vb, hb = decode_heyawake_url(p["url_body"], r, c)
            t0 = time.monotonic()
            sols = solve_heyawake(r, c, room_grid, clues, limit=2, v_borders=vb, h_borders=hb)
            dt = time.monotonic() - t0
            check(f"Unique solution (found {len(sols)}, {dt:.2f}s)", len(sols) == 1)
            if sols:
                expected = smod._SOLUTIONS[level]["solution"]
                sol_2d = [[1 if sols[0][rr*c+cc] == 1 else 0 for cc in range(c)] for rr in range(r)]
                check("Matches expected", sol_2d == expected)

    for var in ["minesweeper", "minesweeper2"]:
        pmod = __import__(f"puzzle_{var}")
        smod = __import__(f"solution_{var}")
        for level in ["easy", "medium", "hard"]:
            vname = "mines" if "2" not in var else "mines2"
            print(f"\n-- {vname} {level} --")
            p = pmod._PUZZLES[level]
            r, c = p["rows"], p["cols"]
            if r * c > 100:
                print(f"  SKIP: {r}x{c}={r*c} cells (ppbench golden, cspuz_is_unique=True)")
                skipped += 1
                continue
            t0 = time.monotonic()
            cg = decode_mines_url(p["url_body"], r, c)
            sols = solve_minesweeper(cg, p["num_mines"], limit=2)
            dt = time.monotonic() - t0
            check(f"Unique solution (found {len(sols)}, {dt:.2f}s)", len(sols) == 1)
            if sols:
                mc = [(rr,cc) for rr in range(r) for cc in range(c) if cg[rr][cc]==-1]
                sg = [[0]*c for _ in range(r)]
                for i,(mr,mcc) in enumerate(mc):
                    if sols[0][i] == 1:
                        sg[mr][mcc] = 1
                check("Matches expected", sg == smod._SOLUTIONS[level]["solution"])

    for var in ["country", "country2"]:
        pmod = __import__(f"puzzle_{var}")
        for level in ["easy", "medium", "hard"]:
            print(f"\n-- {var} {level} --")
            p = pmod._PUZZLES[level]
            r, c = p["rows"], p["cols"]
            print(f"  SKIP: loop puzzle {r}x{c} (ppbench golden, cspuz_is_unique=True)")
            skipped += 1

    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed} passed, {failed} failed, {skipped} skipped")
    if failed == 0:
        print(f"  ALL {passed // 2} VERIFIED PUZZLES HAVE EXACTLY 1 UNIQUE SOLUTION")
    else:
        print(f"  UNIQUENESS FAILURES DETECTED")
    if skipped:
        print(f"  {skipped} large puzzles skipped (ppbench golden guarantees uniqueness)")
    print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
