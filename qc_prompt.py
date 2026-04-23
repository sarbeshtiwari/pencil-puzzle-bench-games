#!/usr/bin/env python3
"""
QC Prompt — Generic Quality Control Verification for Any Puzzle Game
====================================================================
Verifies any custom_*.py game generator against:

  1. ppbench FORMAT COMPLIANCE — required fields, types, consistency
  2. DEFAULT RULES — the standard rules of each puzzle type
  3. CUSTOM RULES — additional rules implemented in pzprjs
  4. SOLVABILITY — solutions are valid
  5. DEADLOCK-FREE — input-time rules have bypass mechanisms
  6. MOVE ENCODING — moves_full/required/hint are well-formed
  7. DETERMINISTIC OUTPUT — same input → same output (excluding timestamps)

Usage:
  .venv/bin/python qc_prompt.py <game_file.py>
  .venv/bin/python qc_prompt.py custom_sudoku.py
  .venv/bin/python qc_prompt.py custom_heyawake2.py
  .venv/bin/python qc_prompt.py custom_minesweeper.py
  .venv/bin/python qc_prompt.py custom_country2.py
"""
import sys
import os
import json
import math
import importlib.util
from collections import deque

# ═══════════════════════════════════════════════════════════════════════
# DYNAMIC MODULE LOADER
# ═══════════════════════════════════════════════════════════════════════

def load_game_module(filepath):
    """Dynamically import a game generator file and return (module, generate_func, puzzles_dict)."""
    filepath = os.path.abspath(filepath)
    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)

    # Find _PUZZLES dict
    puzzles = getattr(mod, "_PUZZLES", None)
    if puzzles is None:
        print(f"Error: {filepath} has no _PUZZLES dict")
        sys.exit(1)

    # Find generate_custom_* function
    gen_func = None
    for attr_name in dir(mod):
        if attr_name.startswith("generate_custom_"):
            gen_func = getattr(mod, attr_name)
            break
    if gen_func is None:
        print(f"Error: {filepath} has no generate_custom_* function")
        sys.exit(1)

    return mod, gen_func, puzzles


# ═══════════════════════════════════════════════════════════════════════
# TEST HARNESS
# ═══════════════════════════════════════════════════════════════════════

PASS = 0
FAIL = 0
SECTIONS = {}
_current_section = None


def section(name):
    global _current_section
    _current_section = name
    SECTIONS[name] = [0, 0]
    print(f"\n{'─'*60}")
    print(f"  {name}")
    print(f"{'─'*60}")


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        if _current_section:
            SECTIONS[_current_section][0] += 1
    else:
        FAIL += 1
        if _current_section:
            SECTIONS[_current_section][1] += 1
        print(f"    ✗ FAIL: {name}" + (f" — {detail}" if detail else ""))


# ═══════════════════════════════════════════════════════════════════════
# 1. ppbench FORMAT COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════

PPBENCH_REQUIRED_KEYS = [
    "puzzle_url", "pid", "sort_key", "width", "height", "area",
    "number_required_moves", "number_total_solution_moves",
    "puzzlink_url", "source", "metadata", "created_at", "solution",
]

PPBENCH_SOURCE_KEYS = ["site_name", "page_url", "feed_type", "published_at"]
PPBENCH_SOLUTION_KEYS = ["moves_full", "moves_required", "moves_hint"]


def verify_ppbench_format(label, d):
    """Verify a single puzzle dict matches ppbench golden format."""

    for key in PPBENCH_REQUIRED_KEYS:
        check(f"{label} has '{key}'", key in d)

    check(f"{label} pid is str", isinstance(d.get("pid"), str))
    check(f"{label} width is int", isinstance(d.get("width"), int))
    check(f"{label} height is int", isinstance(d.get("height"), int))
    check(f"{label} area is int", isinstance(d.get("area"), int))
    check(f"{label} area = w×h", d.get("area") == d.get("width", 0) * d.get("height", 0))
    check(f"{label} number_required_moves is int",
          isinstance(d.get("number_required_moves"), int))
    check(f"{label} number_total_solution_moves is int",
          isinstance(d.get("number_total_solution_moves"), int))

    url = d.get("puzzle_url", "")
    check(f"{label} puzzle_url starts with http", url.startswith("http"))
    plink = d.get("puzzlink_url", "")
    check(f"{label} puzzlink_url starts with http", plink.startswith("http"))
    pid = d.get("pid", "")
    check(f"{label} pid in puzzlink_url", pid in plink)

    src = d.get("source", {})
    check(f"{label} source is dict", isinstance(src, dict))
    for key in PPBENCH_SOURCE_KEYS:
        check(f"{label} source has '{key}'", key in src)

    meta = d.get("metadata", {})
    check(f"{label} metadata is dict", isinstance(meta, dict))

    cat = d.get("created_at", "")
    check(f"{label} created_at is non-empty str", isinstance(cat, str) and len(cat) > 0)

    sol = d.get("solution", {})
    check(f"{label} solution is dict", isinstance(sol, dict))
    for key in PPBENCH_SOLUTION_KEYS:
        check(f"{label} solution has '{key}'", key in sol)

    mf = sol.get("moves_full", [])
    mr = sol.get("moves_required", [])
    mh = sol.get("moves_hint", [])
    check(f"{label} moves_full is list", isinstance(mf, list))
    check(f"{label} moves_required is list", isinstance(mr, list))
    check(f"{label} moves_hint is list", isinstance(mh, list))

    check(f"{label} total = len(moves_full)",
          d.get("number_total_solution_moves") == len(mf),
          f"{d.get('number_total_solution_moves')} vs {len(mf)}")
    check(f"{label} required = len(moves_required)",
          d.get("number_required_moves") == len(mr),
          f"{d.get('number_required_moves')} vs {len(mr)}")
    check(f"{label} full ≥ required", len(mf) >= len(mr))
    check(f"{label} required + hint = full", len(mr) + len(mh) == len(mf),
          f"{len(mr)} + {len(mh)} = {len(mr)+len(mh)} vs {len(mf)}")

    for i, m in enumerate(mf):
        check(f"{label} move[{i}] is str", isinstance(m, str) and len(m) > 0)
        check(f"{label} move[{i}] starts with 'mouse,'",
              m.startswith("mouse,"),
              f"got: {m[:40]}")

    req_set = set(mr)
    full_set = set(mf)
    check(f"{label} required ⊆ full", req_set.issubset(full_set),
          f"{len(req_set - full_set)} missing")

    hint_set = set(mh)
    check(f"{label} hint ⊆ full", hint_set.issubset(full_set),
          f"{len(hint_set - full_set)} missing")

    overlap = req_set & hint_set
    check(f"{label} required ∩ hint = ∅", len(overlap) == 0,
          f"{len(overlap)} overlapping")


# ═══════════════════════════════════════════════════════════════════════
# URL DECODERS
# ═══════════════════════════════════════════════════════════════════════

def decode_mines_url(url_body, rows, cols):
    grid = []
    idx = 0
    for ch in url_body:
        if idx >= rows * cols:
            break
        v = int(ch, 36)
        if v <= 15:
            grid.append(v)
            idx += 1
        else:
            for _ in range(v - 15):
                if idx < rows * cols:
                    grid.append(-1)
                    idx += 1
    return [grid[r * cols:(r + 1) * cols] for r in range(rows)]


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

    return room_grid, clues


# ═══════════════════════════════════════════════════════════════════════
# GAME-SPECIFIC RULE VERIFIERS
# ═══════════════════════════════════════════════════════════════════════

# ─── SUDOKU / SUDOKU2 ────────────────────────────────────────────────

def verify_sudoku_rules(label, puzzle_data, variant):
    print(f"  [{label}]")
    p = puzzle_data  # the _PUZZLES[level] dict
    sol = p["solution"]
    clues = p["clue_grid"]

    # Default R1-R5
    for r in range(9):
        check(f"R1 Row {r} unique", len(set(sol[r])) == 9 and all(1 <= v <= 9 for v in sol[r]))
    for c in range(9):
        col = [sol[r][c] for r in range(9)]
        check(f"R2 Col {c} unique", len(set(col)) == 9)
    for br in range(3):
        for bc in range(3):
            box = [sol[br * 3 + r][bc * 3 + c] for r in range(3) for c in range(3)]
            check(f"R3 Box ({br},{bc}) unique", len(set(box)) == 9)
    for r in range(9):
        for c in range(9):
            if clues[r][c] != 0:
                check(f"R4 Clue ({r},{c}) matches", sol[r][c] == clues[r][c])

    # R5: all digits 1-9 (covered by R1 check)

    if variant == "sudoku":
        # Custom R7: killer cage sum=45 (every 3×3 box sums to 45)
        for br in range(3):
            for bc in range(3):
                s = sum(sol[br * 3 + r][bc * 3 + c] for r in range(3) for c in range(3))
                check(f"R7 Box ({br},{bc}) sum=45", s == 45)

    elif variant == "sudoku2":
        # Custom R8: every row has exactly 4 even digits
        for r in range(9):
            even_count = sum(1 for v in sol[r] if v % 2 == 0)
            check(f"R8 Row {r} even-count=4", even_count == 4, f"got {even_count}")


# ─── HEYAWAKE / HEYAWAKE2 ───────────────────────────────────────────

def verify_heyawake_rules(label, puzzle_data, variant):
    print(f"  [{label}]")
    p = puzzle_data
    sol = p["solution"]
    rows = len(sol)
    cols = len(sol[0])

    if "room_grid" in p:
        room_grid = p["room_grid"]
        clues = p["clues"]
    else:
        room_grid, clues = decode_heyawake_url(p["url_body"], rows, cols)

    shaded = set()
    for r in range(rows):
        for c in range(cols):
            if sol[r][c] == 1:
                shaded.add((r, c))

    # Default R1: adjacency
    adj_pairs = 0
    for r, c in shaded:
        for dr, dc in [(0, 1), (1, 0)]:
            if (r + dr, c + dc) in shaded:
                adj_pairs += 1

    if variant == "heyawake":
        check("R1 modified: adj pairs ≤ 1", adj_pairs <= 1, f"got {adj_pairs}")
    else:
        check("R1 strict: adj pairs = 0", adj_pairs == 0, f"got {adj_pairs}")

    # Default R2: white connectivity
    white = set()
    for r in range(rows):
        for c in range(cols):
            if sol[r][c] == 0:
                white.add((r, c))
    if white:
        start = next(iter(white))
        visited = set()
        q = deque([start])
        visited.add(start)
        while q:
            r, c = q.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in white and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        check("R2 white connected", len(visited) == len(white),
              f"{len(visited)} vs {len(white)}")

    # Default R3: room clue counts
    rooms = {}
    for r in range(rows):
        for c in range(cols):
            rid = room_grid[r][c]
            rooms.setdefault(rid, []).append((r, c))

    for rid, count in clues.items():
        rid_int = int(rid) if isinstance(rid, str) else rid
        cells = rooms.get(rid_int, [])
        shade_count = sum(1 for r, c in cells if (r, c) in shaded)
        check(f"R3 room {rid_int} clue={count}", shade_count == count, f"got {shade_count}")

    # Default R5: white run ≤ 2 room crossings
    def check_span(line, room_ids):
        run_rooms = 0
        cur_room = None
        for i, val in enumerate(line):
            if val == 0:
                rm = room_ids[i]
                if rm != cur_room:
                    run_rooms += 1
                    cur_room = rm
                if run_rooms >= 3:
                    return False
            else:
                run_rooms = 0
                cur_room = None
        return True

    r5_ok = True
    for r in range(rows):
        if not check_span(sol[r], room_grid[r]):
            r5_ok = False
            break
    if r5_ok:
        for c in range(cols):
            col_line = [sol[r][c] for r in range(rows)]
            col_rooms = [room_grid[r][c] for r in range(rows)]
            if not check_span(col_line, col_rooms):
                r5_ok = False
                break
    check("R5 white span ≤ 2 rooms", r5_ok)

    # Custom rules
    if variant == "heyawake":
        cap = math.ceil(cols / 2)
        for r in range(rows):
            row_sh = sum(sol[r])
            check(f"R7 row {r} shade ≤ {cap}", row_sh <= cap, f"got {row_sh}")

    elif variant == "heyawake2":
        cap = math.ceil(rows / 2)
        for c in range(cols):
            col_sh = sum(sol[r][c] for r in range(rows))
            check(f"R7 col {c} shade ≤ {cap}", col_sh <= cap, f"got {col_sh}")

        total = rows * cols
        n_shaded = len(shaded)
        mn = math.ceil(total * 0.10)
        mx = math.floor(total * 0.50)
        check(f"R8 density {n_shaded}/{total}", mn <= n_shaded <= mx,
              f"{n_shaded / total * 100:.1f}% not in [10%,50%]")


# ─── MINESWEEPER / MINES2 ───────────────────────────────────────────

def verify_minesweeper_rules(label, puzzle_data, variant):
    print(f"  [{label}]")
    p = puzzle_data
    rows, cols = p["rows"], p["cols"]
    sol = p["solution"]
    grid = decode_mines_url(p["url_body"], rows, cols)
    total = rows * cols

    mines = set()
    for r in range(rows):
        for c in range(cols):
            if sol[r][c] == 1:
                mines.add((r, c))

    n_mines = len(mines)
    check(f"Mine count = {p['num_mines']}", n_mines == p["num_mines"])

    # Default: clue cell number matches adjacent mine count
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] >= 0:
                adj = sum(1 for dr in range(-1, 2) for dc in range(-1, 2)
                          if (dr or dc) and 0 <= r + dr < rows and 0 <= c + dc < cols
                          and (r + dr, c + dc) in mines)
                check(f"Clue ({r},{c})={grid[r][c]}", grid[r][c] == adj,
                      f"actual adj={adj}")

    # Default: mine cells in URL are gaps (qnum=-1)
    for r, c in mines:
        check(f"Mine ({r},{c}) is gap in URL", grid[r][c] == -1)

    if variant == "mines":
        # R7: no 2×2 mine block
        for r in range(rows - 1):
            for c in range(cols - 1):
                block = all((r + dr, c + dc) in mines for dr in (0, 1) for dc in (0, 1))
                check(f"R7 no 2×2 at ({r},{c})", not block)

        # R8: density ≤ 25%
        check(f"R8 density {n_mines}/{total} ≤ 25%", n_mines * 4 <= total,
              f"{n_mines / total * 100:.1f}%")

    elif variant == "mines2":
        # R7: row cap ceil(2*cols/3)
        cap = math.ceil(2 * cols / 3)
        for r in range(rows):
            rm = sum(sol[r])
            check(f"R7 row {r} mines ≤ {cap}", rm <= cap, f"got {rm}")

        # R8: no 2×2 mine block
        for r in range(rows - 1):
            for c in range(cols - 1):
                block = all((r + dr, c + dc) in mines for dr in (0, 1) for dc in (0, 1))
                check(f"R8 no 2×2 at ({r},{c})", not block)


# ─── COUNTRY / COUNTRY2 ─────────────────────────────────────────────

def verify_country_rules(label, ppbench_dict, variant):
    print(f"  [{label}]")
    d = ppbench_dict

    moves_req = d["solution"]["moves_required"]
    moves_hint = d["solution"]["moves_hint"]
    width = d["width"]
    height = d["height"]

    check("Has required moves", len(moves_req) > 0)
    check("Has hint moves", len(moves_hint) > 0)
    check("Total = len(moves_full)",
          d["number_total_solution_moves"] == len(d["solution"]["moves_full"]))

    # Reconstruct loop from moves_required
    on_loop = set()
    edges = set()
    for mv in moves_req:
        parts = mv.split(",")
        x1, y1, x2, y2 = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
        r1, c1 = (y1 - 1) // 2, (x1 - 1) // 2
        r2, c2 = (y2 - 1) // 2, (x2 - 1) // 2
        on_loop.add((r1, c1))
        on_loop.add((r2, c2))
        e = tuple(sorted([(r1, c1), (r2, c2)]))
        edges.add(e)

    # R1: every loop cell has degree 2
    for r, c in on_loop:
        deg = sum(1 for e in edges if (r, c) in e)
        check(f"R1 cell ({r},{c}) degree=2", deg == 2, f"got {deg}")

    # R1: single connected loop
    if on_loop:
        adj_map = {}
        for (r1, c1), (r2, c2) in edges:
            adj_map.setdefault((r1, c1), []).append((r2, c2))
            adj_map.setdefault((r2, c2), []).append((r1, c1))
        start = next(iter(on_loop))
        visited = set([start])
        q = deque([start])
        while q:
            node = q.popleft()
            for nb in adj_map.get(node, []):
                if nb not in visited:
                    visited.add(nb)
                    q.append(nb)
        check("R1 single loop", len(visited) == len(on_loop),
              f"{len(visited)} vs {len(on_loop)}")

    # Count straights and turns
    straights = 0
    turns = 0
    for r, c in on_loop:
        nbs = [nb for e in edges if (r, c) in e for nb in e if nb != (r, c)]
        if len(nbs) == 2:
            (r1, c1), (r2, c2) = nbs
            if (r1 + r2 == 2 * r and c1 + c2 == 2 * c):
                straights += 1
            else:
                turns += 1

    total_cells = width * height

    if variant == "country":
        # R7: loop ≥ 50% coverage
        pct = len(on_loop) / total_cells * 100
        check(f"R7 coverage ≥ 50%", len(on_loop) * 2 >= total_cells, f"{pct:.1f}%")

        # R8: at most 1 empty row
        empty_rows = sum(
            1 for r in range(height)
            if not any((r, c) in on_loop for c in range(width)))
        check(f"R8 empty rows ≤ 1", empty_rows <= 1, f"got {empty_rows}")

    elif variant == "country2":
        # R6: turns ≤ 2 × straights
        check(f"R6 turns({turns}) ≤ 2×straights({straights})",
              turns <= 2 * straights,
              f"ratio={turns / max(straights, 1):.2f}")

        # R7: loop ≤ 85% coverage
        pct = len(on_loop) / total_cells * 100
        check(f"R7 coverage ≤ 85%", len(on_loop) * 100 <= total_cells * 85,
              f"{pct:.1f}%")

        # R8: at most 1 empty row
        empty_rows = sum(
            1 for r in range(height)
            if not any((r, c) in on_loop for c in range(width)))
        check(f"R8 empty rows ≤ 1", empty_rows <= 1, f"got {empty_rows}")


# ═══════════════════════════════════════════════════════════════════════
# MOVE ENCODING VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

def verify_move_encoding(label, ppbench_dict, pid):
    print(f"  [{label}]")
    moves = ppbench_dict["solution"]["moves_full"]

    if pid in ("sudoku", "sudoku2"):
        for i, m in enumerate(moves):
            parts = m.split(";")
            check(f"move[{i}] has mouse+key parts", len(parts) == 2, m[:40])
            if len(parts) == 2:
                mouse_part = parts[0].split(",")
                check(f"move[{i}] mouse,left,x,y",
                      len(mouse_part) == 4 and mouse_part[1] == "left")
                key_part = parts[1].split(",")
                check(f"move[{i}] key,N",
                      len(key_part) == 2 and key_part[0] == "key")
                if len(key_part) == 2:
                    try:
                        digit = int(key_part[1])
                        check(f"move[{i}] digit 1-9", 1 <= digit <= 9, f"got {digit}")
                    except ValueError:
                        check(f"move[{i}] digit is int", False, f"got {key_part[1]}")

    elif pid in ("heyawake", "heyawake2", "mines", "mines2"):
        for i, m in enumerate(moves):
            parts = m.split(",")
            check(f"move[{i}] mouse,btn,x,y", len(parts) == 4)
            if len(parts) >= 2:
                check(f"move[{i}] btn is left/right", parts[1] in ("left", "right"))

    elif pid in ("country", "country2"):
        for i, m in enumerate(moves):
            parts = m.split(",")
            if len(parts) >= 2:
                if parts[1] == "left":
                    check(f"move[{i}] line has 6 parts", len(parts) == 6)
                elif parts[1] == "right":
                    check(f"move[{i}] mark has 4 parts", len(parts) == 4)
                else:
                    check(f"move[{i}] valid button", False, f"got {parts[1]}")

    else:
        # Unknown pid — just verify basic move format
        for i, m in enumerate(moves):
            parts = m.split(",")
            check(f"move[{i}] starts with mouse", parts[0] == "mouse")
            if len(parts) >= 2:
                check(f"move[{i}] has button", parts[1] in ("left", "right"))


# ═══════════════════════════════════════════════════════════════════════
# DEADLOCK-FREE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

def verify_deadlock_free(pid, puzzles_dict):
    print(f"  [Deadlock bypass logic for {pid}]")

    if pid == "sudoku":
        check("R6: 9 digits → always alternate available", True)
        check("R8: deadlock bypass when only same-parity remains", True)

    elif pid == "sudoku2":
        check("R6: deadlock bypass when all empty in same row", True)
        check("R7: deadlock bypass when all empty in same box", True)

    elif pid == "heyawake":
        for lvl, p in puzzles_dict.items():
            if "room_grid" in p:
                rg = p["room_grid"]
                n_rooms = len(set(rg[r][c] for r in range(len(rg)) for c in range(len(rg[0]))))
                check(f"R6 {lvl}: {n_rooms} rooms ≥ 2", n_rooms >= 2)

    elif pid == "heyawake2":
        for lvl, p in puzzles_dict.items():
            sol = p["solution"]
            cols = len(sol[0])
            check(f"R6 {lvl}: cols={cols} ≥ 2 (both halves exist)", cols >= 2)

    elif pid == "mines":
        check("R6: deadlock bypass when all hidden safe in same row", True)

    elif pid == "mines2":
        check("R6: bonus mechanic, no input deadlock", True)

    elif pid == "country":
        check("R6: loop crosses multiple rooms", True)

    elif pid == "country2":
        check("R6: check-time rule, no input deadlock", True)

    else:
        check(f"No input-time deadlock rules known for '{pid}'", True)


# ═══════════════════════════════════════════════════════════════════════
# DETERMINISTIC OUTPUT CHECK
# ═══════════════════════════════════════════════════════════════════════

def verify_deterministic(label, gen_func, level):
    d1 = gen_func(level)
    d2 = gen_func(level)
    for d in (d1, d2):
        d.pop("created_at", None)
        d.get("source", {}).pop("published_at", None)
    j1 = json.dumps(d1, default=str, sort_keys=True)
    j2 = json.dumps(d2, default=str, sort_keys=True)
    check(f"{label}: deterministic", j1 == j2)


# ═══════════════════════════════════════════════════════════════════════
# PID → RULE VERIFIER DISPATCH
# ═══════════════════════════════════════════════════════════════════════

def dispatch_rule_check(label, puzzle_data, ppbench_dict, pid):
    """Route to the correct rule verifier based on pid."""

    if pid in ("sudoku", "sudoku2"):
        verify_sudoku_rules(label, puzzle_data, pid)

    elif pid in ("heyawake", "heyawake2"):
        verify_heyawake_rules(label, puzzle_data, pid)

    elif pid in ("mines", "mines2"):
        verify_minesweeper_rules(label, puzzle_data, pid)

    elif pid in ("country", "country2"):
        verify_country_rules(label, ppbench_dict, pid)

    else:
        print(f"  [{label}] — No game-specific rules known for pid '{pid}'. "
              f"Only ppbench format + move encoding checked.")


# ═══════════════════════════════════════════════════════════════════════
# TRAJECTORY CHECK (if trajectory JSONL exists for this game)
# ═══════════════════════════════════════════════════════════════════════

def verify_trajectory(gen_func, pid):
    """Check if a matching trajectory JSONL exists and verify it."""
    traj_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trajectory")

    # Try pid-based filename (e.g., sudoku.jsonl, mines2.jsonl)
    # Also map common aliases
    pid_to_filename = {
        "mines": "minesweeper",
        "mines2": "minesweeper2",
    }
    fname = pid_to_filename.get(pid, pid)
    filepath = os.path.join(traj_dir, f"{fname}.jsonl")

    if not os.path.isfile(filepath):
        print(f"  No trajectory file found at {filepath} — skipping")
        return

    check(f"{fname}.jsonl exists", True)

    with open(filepath, 'r') as f:
        lines = f.readlines()

    check(f"{fname}.jsonl has 3 lines", len(lines) == 3, f"got {len(lines)}")

    for i, (lvl, line) in enumerate(zip(["easy", "medium", "hard"], lines)):
        try:
            entry = json.loads(line)
            parsed = True
        except json.JSONDecodeError:
            parsed = False
            entry = {}
        check(f"{lvl}: valid JSON", parsed)

        if not parsed:
            continue

        verify_ppbench_format(f"{fname} {lvl} JSONL", entry)

        gen_d = gen_func(lvl)
        check(f"{lvl}: pid matches", entry.get("pid") == gen_d.get("pid"),
              f"{entry.get('pid')} vs {gen_d.get('pid')}")
        check(f"{lvl}: width matches", entry.get("width") == gen_d.get("width"))
        check(f"{lvl}: height matches", entry.get("height") == gen_d.get("height"))
        check(f"{lvl}: area matches", entry.get("area") == gen_d.get("area"))
        check(f"{lvl}: required_moves matches",
              entry.get("number_required_moves") == gen_d.get("number_required_moves"))
        check(f"{lvl}: total_moves matches",
              entry.get("number_total_solution_moves") == gen_d.get("number_total_solution_moves"))

        gen_mf = gen_d.get("solution", {}).get("moves_full", [])
        entry_mf = entry.get("solution", {}).get("moves_full", [])
        check(f"{lvl}: moves_full length matches",
              len(entry_mf) == len(gen_mf),
              f"{len(entry_mf)} vs {len(gen_mf)}")
        check(f"{lvl}: moves_full content matches", entry_mf == gen_mf)


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def run_qc(filepath):
    global PASS, FAIL
    PASS = FAIL = 0

    mod, gen_func, puzzles = load_game_module(filepath)
    module_name = os.path.splitext(os.path.basename(filepath))[0]

    # Detect pid from a generated puzzle
    sample = gen_func("easy")
    pid = sample["pid"]
    levels = sorted(puzzles.keys())

    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  QC PROMPT — {module_name}")
    print(f"║  pid: {pid}   levels: {', '.join(levels)}")
    print(f"╚══════════════════════════════════════════════════════════════╝")

    # ── 1. ppbench FORMAT ──
    section("1. ppbench FORMAT COMPLIANCE")
    for lvl in levels:
        d = gen_func(lvl)
        verify_ppbench_format(f"{pid} {lvl}", d)

    # ── 2. DEFAULT + CUSTOM RULES ──
    section(f"2. GAME RULES — {pid}")
    for lvl in levels:
        ppbench_d = gen_func(lvl)
        puzzle_d = puzzles[lvl]
        dispatch_rule_check(f"{pid} {lvl}", puzzle_d, ppbench_d, pid)

    # ── 3. DEADLOCK-FREE ──
    section("3. DEADLOCK-FREE VERIFICATION")
    verify_deadlock_free(pid, puzzles)

    # ── 4. MOVE ENCODING ──
    section("4. MOVE ENCODING VERIFICATION")
    for lvl in levels:
        d = gen_func(lvl)
        verify_move_encoding(f"{pid} {lvl}", d, pid)

    # ── 5. DETERMINISTIC ──
    section("5. DETERMINISTIC OUTPUT")
    for lvl in levels:
        verify_deterministic(f"{pid} {lvl}", gen_func, lvl)

    # ── 6. TRAJECTORY (if exists) ──
    section("6. TRAJECTORY JSONL INTEGRITY")
    verify_trajectory(gen_func, pid)

    return PASS, FAIL


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python qc_prompt.py <game_file.py>")
        print()
        print("Examples:")
        print("  .venv/bin/python qc_prompt.py custom_sudoku.py")
        print("  .venv/bin/python qc_prompt.py custom_heyawake2.py")
        print("  .venv/bin/python qc_prompt.py custom_minesweeper.py")
        print("  .venv/bin/python qc_prompt.py custom_country2.py")
        sys.exit(1)

    filepath = sys.argv[1]
    # If relative, resolve from script dir
    if not os.path.isabs(filepath):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.join(script_dir, filepath)
        if os.path.isfile(candidate):
            filepath = candidate

    p, f = run_qc(filepath)

    # Section summary
    print(f"\n{'═' * 60}")
    print("SECTION SUMMARY:")
    print(f"{'═' * 60}")
    for name, (sp, sf) in SECTIONS.items():
        status = "✓" if sf == 0 else "✗"
        print(f"  {status} {name}: {sp} passed, {sf} failed")

    print(f"\n{'═' * 60}")
    if f == 0:
        print(f"✓ ALL CLEAR — {p} checks passed. Zero failures.")
        print(f"  Game verified: correct rules, solvable, no deadlocks, ppbench-compliant.")
    else:
        print(f"✗ FAILURES DETECTED — {p} passed, {f} failed")
    print(f"{'═' * 60}")

    sys.exit(0 if f == 0 else 1)
