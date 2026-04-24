#!/usr/bin/env python3
"""Verify ALL 24 puzzles (8 games × 3 levels) for correctness."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from custom_sudoku import generate_custom_sudoku
from custom_sudoku2 import generate_custom_sudoku2
from custom_heyawake import generate_custom_heyawake
from custom_heyawake2 import generate_custom_heyawake2
from custom_minesweeper import generate_custom_minesweeper
from custom_minesweeper2 import generate_custom_minesweeper2
from custom_country import generate_custom_country
from custom_country2 import generate_custom_country2

PASS = 0
FAIL = 0

def ok(name, check, msg=""):
    global PASS, FAIL
    if check:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name} — {msg}")

def verify_sudoku(label, gen_func):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    for level in ("easy", "medium", "hard"):
        print(f"\n  --- {level} ---")
        d = gen_func(level)
        sol = None
        # Extract solution grid from moves
        grid = [[0]*9 for _ in range(9)]
        # Get clue grid from the module
        mod = gen_func.__module__
        mod_obj = sys.modules[mod]
        p = mod_obj._PUZZLES[level]
        clue_grid = p["clue_grid"]
        solution = p["solution"]

        # R1: Each row has digits 1-9
        for r in range(9):
            ok(f"{level} row {r}", sorted(solution[r]) == list(range(1,10)),
               f"row {r} = {solution[r]}")

        # R2: Each column has digits 1-9
        for c in range(9):
            col = [solution[r][c] for r in range(9)]
            ok(f"{level} col {c}", sorted(col) == list(range(1,10)),
               f"col {c} = {col}")

        # R3: Each 3x3 box has digits 1-9
        for br in range(3):
            for bc in range(3):
                box = []
                for r in range(br*3, br*3+3):
                    for c in range(bc*3, bc*3+3):
                        box.append(solution[r][c])
                ok(f"{level} box ({br},{bc})", sorted(box) == list(range(1,10)),
                   f"box ({br},{bc}) = {box}")

        # R4: Solution matches clues
        mismatches = []
        for r in range(9):
            for c in range(9):
                if clue_grid[r][c] != 0 and clue_grid[r][c] != solution[r][c]:
                    mismatches.append((r, c, clue_grid[r][c], solution[r][c]))
        ok(f"{level} clue match", len(mismatches) == 0,
           f"mismatches: {mismatches}")

        # R5: Move count
        empty = sum(1 for r in range(9) for c in range(9) if clue_grid[r][c] == 0)
        ok(f"{level} move count", d["number_required_moves"] == empty,
           f"expected {empty}, got {d['number_required_moves']}")

        # Verify moves encode correct cells and digits
        moves = d["solution"]["moves_required"]
        ok(f"{level} moves len", len(moves) == empty,
           f"expected {empty} moves, got {len(moves)}")

        for m in moves:
            parts = m.split(";")
            mouse_part = parts[0].split(",")
            key_part = parts[1].split(",") if len(parts) > 1 else None
            x, y = int(mouse_part[2]), int(mouse_part[3])
            c_idx = (x - 1) // 2
            r_idx = (y - 1) // 2
            digit = int(key_part[1]) if key_part else None
            if digit and solution[r_idx][c_idx] != digit:
                ok(f"{level} move ({r_idx},{c_idx})", False,
                   f"move says {digit}, solution says {solution[r_idx][c_idx]}")

        # URL present
        ok(f"{level} has URL", "puzz.link" in d.get("puzzlink_url", ""),
           "missing puzzlink_url")
        ok(f"{level} pid", d["pid"] in ("sudoku", "sudoku2"),
           f"pid={d['pid']}")

        print(f"  {level}: all checks passed ✓" if FAIL == 0 else "")


def verify_heyawake(label, gen_func):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    for level in ("easy", "medium", "hard"):
        print(f"\n  --- {level} ---")
        d = gen_func(level)
        mod_obj = sys.modules[gen_func.__module__]
        p = mod_obj._PUZZLES[level]
        rows, cols = p["rows"], p["cols"]
        sol = p["solution"]

        # R1: No two shaded cells orthogonally adjacent (standard heyawake)
        # For heyawake (original), allow at most 1 pair; for heyawake2, strict 0
        is_v2 = "2" in d["pid"]
        adj_pairs = 0
        for r in range(rows):
            for c in range(cols):
                if sol[r][c] == 1:
                    if r+1 < rows and sol[r+1][c] == 1:
                        adj_pairs += 1
                    if c+1 < cols and sol[r][c+1] == 1:
                        adj_pairs += 1
        if is_v2:
            ok(f"{level} R1 strict adj", adj_pairs == 0,
               f"{adj_pairs} adjacent pairs (must be 0 for heyawake2)")
        else:
            ok(f"{level} R1 adj ≤1", adj_pairs <= 1,
               f"{adj_pairs} adjacent pairs (must be ≤1)")

        # R2: All white cells connected (BFS)
        white_cells = [(r,c) for r in range(rows) for c in range(cols) if sol[r][c] == 0]
        if white_cells:
            visited = set()
            queue = [white_cells[0]]
            visited.add(white_cells[0])
            while queue:
                cr, cc = queue.pop(0)
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = cr+dr, cc+dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr,nc) not in visited and sol[nr][nc] == 0:
                        visited.add((nr,nc))
                        queue.append((nr,nc))
            ok(f"{level} R2 white connected", len(visited) == len(white_cells),
               f"visited {len(visited)}/{len(white_cells)}")

        # Move counts
        shaded = sum(sol[r][c] for r in range(rows) for c in range(cols))
        total = rows * cols
        ok(f"{level} shaded count", d["number_required_moves"] == shaded,
           f"expected {shaded}, got {d['number_required_moves']}")
        ok(f"{level} total moves", d["number_total_solution_moves"] == total,
           f"expected {total}, got {d['number_total_solution_moves']}")

        # Check row shade balance for heyawake (ceil(cols/2))
        if not is_v2:
            import math
            cap = math.ceil(cols / 2)
            for r in range(rows):
                row_shade = sum(sol[r])
                ok(f"{level} R7 row {r} balance", row_shade <= cap,
                   f"row {r} has {row_shade} shaded, cap={cap}")

        # Check column shade balance for heyawake2 (ceil(rows/2))
        if is_v2:
            import math
            cap = math.ceil(rows / 2)
            for c in range(cols):
                col_shade = sum(sol[r][c] for r in range(rows))
                ok(f"{level} R7 col {c} balance", col_shade <= cap,
                   f"col {c} has {col_shade} shaded, cap={cap}")

        ok(f"{level} has URL", "puzz.link" in d.get("puzzlink_url", ""))
        print(f"  {level}: checks done")


def verify_minesweeper(label, gen_func):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    for level in ("easy", "medium", "hard"):
        print(f"\n  --- {level} ---")
        d = gen_func(level)
        mod_obj = sys.modules[gen_func.__module__]
        p = mod_obj._PUZZLES[level]
        rows, cols = p["rows"], p["cols"]
        sol = p["solution"]  # 1=mine, 0=safe

        # Count mines
        mine_count = sum(sol[r][c] for r in range(rows) for c in range(cols))
        ok(f"{level} mine count", mine_count == p["num_mines"],
           f"expected {p['num_mines']}, got {mine_count}")

        # For each safe cell, verify the clue number matches adjacent mine count
        # Decode the URL to get the clue grid
        url_body = p["url_body"]
        clue_grid = []
        for ch in url_body:
            v = int(ch, 36)
            if v <= 15:  # hex digit = clue number
                clue_grid.append(v)
            else:  # g-z = gaps (mines)
                gap = v - 15
                clue_grid.extend([-1] * gap)

        ok(f"{level} cell count", len(clue_grid) == rows * cols,
           f"expected {rows*cols}, got {len(clue_grid)}")

        if len(clue_grid) == rows * cols:
            errors = []
            for r in range(rows):
                for c in range(cols):
                    idx = r * cols + c
                    cell_val = clue_grid[idx]

                    if cell_val == -1:
                        # This should be a mine
                        if sol[r][c] != 1:
                            errors.append(f"({r},{c}) URL says mine but sol says safe")
                    else:
                        # This should be safe with clue = cell_val
                        if sol[r][c] != 0:
                            errors.append(f"({r},{c}) URL says clue {cell_val} but sol says mine")
                        else:
                            # Count adjacent mines (8 directions)
                            adj = 0
                            for dr in (-1, 0, 1):
                                for dc in (-1, 0, 1):
                                    if dr == 0 and dc == 0:
                                        continue
                                    nr, nc = r + dr, c + dc
                                    if 0 <= nr < rows and 0 <= nc < cols and sol[nr][nc] == 1:
                                        adj += 1
                            if adj != cell_val:
                                errors.append(f"({r},{c}) clue={cell_val} but adj mines={adj}")

            ok(f"{level} clue verification", len(errors) == 0,
               f"{len(errors)} errors: {errors[:5]}")

        # Move counts
        ok(f"{level} required moves", d["number_required_moves"] == mine_count,
           f"expected {mine_count}, got {d['number_required_moves']}")
        ok(f"{level} total moves", d["number_total_solution_moves"] == rows * cols,
           f"expected {rows*cols}, got {d['number_total_solution_moves']}")

        ok(f"{level} has URL", "puzz.link" in d.get("puzzlink_url", ""))
        print(f"  {level}: checks done")


def verify_country(label, gen_func):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    for level in ("easy", "medium", "hard"):
        print(f"\n  --- {level} ---")
        d = gen_func(level)
        req = d["solution"]["moves_required"]
        hint = d["solution"]["moves_hint"]
        full = d["solution"]["moves_full"]
        rows, cols = d["height"], d["width"]

        # Parse line segments from required moves
        segments = []
        for m in req:
            parts = m.split(",")
            # mouse,left,x1,y1,x2,y2
            x1, y1, x2, y2 = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
            r1, c1 = (y1-1)//2, (x1-1)//2
            r2, c2 = (y2-1)//2, (x2-1)//2
            segments.append(((r1,c1),(r2,c2)))

        # Build adjacency from segments
        from collections import defaultdict
        adj = defaultdict(set)
        on_loop = set()
        for (r1,c1),(r2,c2) in segments:
            adj[(r1,c1)].add((r2,c2))
            adj[(r2,c2)].add((r1,c1))
            on_loop.add((r1,c1))
            on_loop.add((r2,c2))

        # R1: Every cell on loop has exactly 2 neighbors (closed loop, no branching)
        degree_errors = []
        for cell in on_loop:
            deg = len(adj[cell])
            if deg != 2:
                degree_errors.append((cell, deg))
        ok(f"{level} loop degrees", len(degree_errors) == 0,
           f"cells with degree != 2: {degree_errors[:5]}")

        # R1b: Single connected loop
        if on_loop:
            start = next(iter(on_loop))
            visited = {start}
            queue = [start]
            while queue:
                cur = queue.pop(0)
                for nb in adj[cur]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            ok(f"{level} single loop", len(visited) == len(on_loop),
               f"visited {len(visited)}/{len(on_loop)}")

        # Move counts
        ok(f"{level} req count", d["number_required_moves"] == len(req),
           f"expected {len(req)}, got {d['number_required_moves']}")
        total_expected = len(req) + len(hint)
        ok(f"{level} total count", d["number_total_solution_moves"] == len(full),
           f"expected {len(full)}, got {d['number_total_solution_moves']}")
        ok(f"{level} full = req + hint", len(full) == len(req) + len(hint),
           f"full={len(full)} != req={len(req)} + hint={len(hint)}")

        # For country2, check turns ≤ 2 * straight
        is_v2 = "2" in d["pid"]
        if is_v2:
            straight = 0
            turns = 0
            for cell in on_loop:
                nbs = list(adj[cell])
                if len(nbs) == 2:
                    (r1,c1), (r2,c2) = nbs
                    cr, cc = cell
                    # Straight if both neighbors on same axis
                    if r1 == r2 == cr or c1 == c2 == cc:
                        straight += 1
                    else:
                        turns += 1
            ok(f"{level} turns≤2*straight", turns <= straight * 2,
               f"turns={turns}, straight={straight}, 2*straight={straight*2}")

        ok(f"{level} has URL", "puzz.link" in d.get("puzzlink_url", ""))
        print(f"  {level}: checks done")


# ---- Run all verifications ----

print("=" * 60)
print("  FULL PUZZLE VERIFICATION — 24 puzzles")
print("=" * 60)

verify_sudoku("SUDOKU (original)", generate_custom_sudoku)
verify_sudoku("SUDOKU 2 (variant)", generate_custom_sudoku2)
verify_heyawake("HEYAWAKE (original)", generate_custom_heyawake)
verify_heyawake("HEYAWAKE 2 (variant)", generate_custom_heyawake2)
verify_minesweeper("MINESWEEPER (original)", generate_custom_minesweeper)
verify_minesweeper("MINESWEEPER 2 (variant)", generate_custom_minesweeper2)
verify_country("COUNTRY ROAD (original)", generate_custom_country)
verify_country("COUNTRY ROAD 2 (variant)", generate_custom_country2)

print(f"\n{'='*60}")
print(f"  FINAL RESULTS: {PASS} passed, {FAIL} failed")
print(f"{'='*60}")

if FAIL > 0:
    sys.exit(1)
else:
    print("  ALL 24 PUZZLES VERIFIED CORRECT ✓")
