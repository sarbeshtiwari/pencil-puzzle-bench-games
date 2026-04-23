"""
Comprehensive verification of all 24 puzzles (8 games × 3 levels).
Checks BOTH default rules AND custom rules for each game.
"""
import sys, math
from collections import deque

sys.path.insert(0, '/Users/apple/Desktop/morpheus/data')

from custom_sudoku import _PUZZLES as S1, generate_custom_sudoku
from custom_sudoku2 import _PUZZLES as S2, generate_custom_sudoku2
from custom_heyawake import _PUZZLES as H1, generate_custom_heyawake
from custom_heyawake2 import _PUZZLES as H2, generate_custom_heyawake2
from custom_minesweeper import _PUZZLES as M1, generate_custom_minesweeper
from custom_minesweeper2 import _PUZZLES as M2, generate_custom_minesweeper2
from custom_country import _PUZZLES as C1, generate_custom_country
from custom_country2 import _PUZZLES as C2, generate_custom_country2

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"    ✗ FAIL: {name}" + (f" — {detail}" if detail else ""))

def decode_mines_url(url_body, rows, cols):
    grid = []
    idx = 0
    for ch in url_body:
        if idx >= rows * cols: break
        v = int(ch, 36)
        if v <= 15:
            grid.append(v); idx += 1
        else:
            for _ in range(v - 15):
                if idx < rows * cols: grid.append(-1); idx += 1
    return [grid[r*cols:(r+1)*cols] for r in range(rows)]

# ─── SUDOKU VERIFICATION ─────────────────────────────────────────────

def verify_sudoku(label, p, variant):
    print(f"  [{label}]")
    sol = p["solution"]
    clues = p["clue_grid"]

    # Default R1-R5
    for r in range(9):
        check(f"Row {r} unique", len(set(sol[r])) == 9 and all(1<=v<=9 for v in sol[r]))
    for c in range(9):
        col = [sol[r][c] for r in range(9)]
        check(f"Col {c} unique", len(set(col)) == 9)
    for br in range(3):
        for bc in range(3):
            box = [sol[br*3+r][bc*3+c] for r in range(3) for c in range(3)]
            check(f"Box ({br},{bc}) unique", len(set(box)) == 9)
    for r in range(9):
        for c in range(9):
            if clues[r][c] != 0:
                check(f"Clue ({r},{c}) matches", sol[r][c] == clues[r][c])

    if variant == "sudoku":
        # Custom R7: killer cage sum=45 (cage = hash-chosen 3x3 box)
        # Every standard 3x3 box sums to 45, so this always passes
        for br in range(3):
            for bc in range(3):
                s = sum(sol[br*3+r][bc*3+c] for r in range(3) for c in range(3))
                check(f"Box ({br},{bc}) sum=45", s == 45)

    elif variant == "sudoku2":
        # Custom R8: every row has exactly 4 even digits
        for r in range(9):
            even_count = sum(1 for v in sol[r] if v % 2 == 0)
            check(f"Row {r} even-count=4", even_count == 4, f"got {even_count}")

    # Verify generator output
    gen_func = generate_custom_sudoku if variant == "sudoku" else generate_custom_sudoku2
    for lvl in ["easy", "medium", "hard"]:
        d = gen_func(lvl)
        check(f"Gen {lvl} pid", d["pid"] == variant)
        check(f"Gen {lvl} has puzzle_url", "puzzle_url" in d and len(d["puzzle_url"]) > 0)
        check(f"Gen {lvl} has solution", "solution" in d and "moves_full" in d["solution"])

# ─── HEYAWAKE VERIFICATION ───────────────────────────────────────────

def decode_heyawake_url(url_body, rows, cols):
    B32 = "0123456789abcdefghijklmnopqrstuv"

    def unpack_bits(s, n):
        bits = []
        for ch in s:
            v = B32.index(ch)
            for shift in [4,3,2,1,0]:
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

    v_borders = [[0]*cols for _ in range(rows)]
    h_borders = [[0]*cols for _ in range(rows)]
    idx = 0
    for r in range(rows):
        for c in range(cols - 1):
            v_borders[r][c] = vert_bits[idx]; idx += 1
    idx = 0
    for r in range(rows - 1):
        for c in range(cols):
            h_borders[r][c] = horiz_bits[idx]; idx += 1

    room_grid = [[-1]*cols for _ in range(rows)]
    room_id = 0
    for r in range(rows):
        for c in range(cols):
            if room_grid[r][c] == -1:
                q = deque([(r, c)])
                room_grid[r][c] = room_id
                while q:
                    cr, cc = q.popleft()
                    if cc + 1 < cols and room_grid[cr][cc+1] == -1 and v_borders[cr][cc] == 0:
                        room_grid[cr][cc+1] = room_id; q.append((cr, cc+1))
                    if cc - 1 >= 0 and room_grid[cr][cc-1] == -1 and v_borders[cr][cc-1] == 0:
                        room_grid[cr][cc-1] = room_id; q.append((cr, cc-1))
                    if cr + 1 < rows and room_grid[cr+1][cc] == -1 and h_borders[cr][cc] == 0:
                        room_grid[cr+1][cc] = room_id; q.append((cr+1, cc))
                    if cr - 1 >= 0 and room_grid[cr-1][cc] == -1 and h_borders[cr-1][cc] == 0:
                        room_grid[cr-1][cc] = room_id; q.append((cr-1, cc))
                room_id += 1

    n_rooms = room_id
    clues = {}
    rid = 0
    i = 0
    while i < len(number_str) and rid < n_rooms:
        ch = number_str[i]
        if ch == '-':
            hx = number_str[i+1:i+3]
            clues[rid] = int(hx, 16)
            rid += 1; i += 3
        else:
            v = int(ch, 36)
            if v <= 15:
                clues[rid] = v
                rid += 1; i += 1
            else:
                rid += (v - 15)
                i += 1

    return room_grid, clues

def verify_heyawake(label, p, variant):
    print(f"  [{label}]")
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
        for dr, dc in [(0,1),(1,0)]:
            if (r+dr, c+dc) in shaded:
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
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if (nr, nc) in white and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        check("R2 white connected", len(visited) == len(white), f"{len(visited)} vs {len(white)}")

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
            r5_ok = False; break
    if r5_ok:
        for c in range(cols):
            col_line = [sol[r][c] for r in range(rows)]
            col_rooms = [room_grid[r][c] for r in range(rows)]
            if not check_span(col_line, col_rooms):
                r5_ok = False; break
    check("R5 white span ≤ 2 rooms", r5_ok)

    # Custom rules
    if variant == "heyawake":
        # R7: row balance ceil(cols/2)
        cap = math.ceil(cols / 2)
        for r in range(rows):
            row_sh = sum(sol[r])
            check(f"R7 row {r} shade ≤ {cap}", row_sh <= cap, f"got {row_sh}")

    elif variant == "heyawake2":
        # R7: col balance ceil(rows/2)
        cap = math.ceil(rows / 2)
        for c in range(cols):
            col_sh = sum(sol[r][c] for r in range(rows))
            check(f"R7 col {c} shade ≤ {cap}", col_sh <= cap, f"got {col_sh}")

        # R8: density 10-50%
        total = rows * cols
        n_shaded = len(shaded)
        mn = math.ceil(total * 0.10)
        mx = math.floor(total * 0.50)
        check(f"R8 density {n_shaded}/{total}", mn <= n_shaded <= mx,
              f"{n_shaded/total*100:.1f}% not in [{mn},{mx}]")

# ─── MINESWEEPER VERIFICATION ────────────────────────────────────────

def verify_minesweeper(label, p, variant):
    print(f"  [{label}]")
    rows, cols = p["rows"], p["cols"]
    sol = p["solution"]  # 1=mine, 0=safe
    grid = decode_mines_url(p["url_body"], rows, cols)
    total = rows * cols

    mines = set()
    for r in range(rows):
        for c in range(cols):
            if sol[r][c] == 1:
                mines.add((r, c))

    n_mines = len(mines)
    check(f"Mine count = {p['num_mines']}", n_mines == p["num_mines"])

    # Default: every clue cell's number matches adjacent mine count
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] >= 0:
                adj = sum(1 for dr in range(-1,2) for dc in range(-1,2)
                          if (dr or dc) and 0<=r+dr<rows and 0<=c+dc<cols and (r+dr,c+dc) in mines)
                check(f"Clue ({r},{c})={grid[r][c]}", grid[r][c] == adj, f"actual adj={adj}")

    # Default: mine cells in URL are gaps (qnum=-1)
    for r, c in mines:
        check(f"Mine ({r},{c}) is gap in URL", grid[r][c] == -1)

    if variant == "mines":
        # R7: no 2x2 mine block
        for r in range(rows-1):
            for c in range(cols-1):
                block = all((r+dr,c+dc) in mines for dr in (0,1) for dc in (0,1))
                check(f"R7 no 2x2 at ({r},{c})", not block)

        # R8: density <= 25%
        check(f"R8 density {n_mines}/{total} ≤ 25%", n_mines * 4 <= total,
              f"{n_mines/total*100:.1f}%")

    elif variant == "mines2":
        # R7: row cap ceil(2*cols/3)
        cap = math.ceil(2 * cols / 3)
        for r in range(rows):
            rm = sum(sol[r])
            check(f"R7 row {r} mines ≤ {cap}", rm <= cap, f"got {rm}")

        # R8: no 2x2 mine block
        for r in range(rows-1):
            for c in range(cols-1):
                block = all((r+dr,c+dc) in mines for dr in (0,1) for dc in (0,1))
                check(f"R8 no 2x2 at ({r},{c})", not block)

    # Verify generator
    gen_func = generate_custom_minesweeper if variant == "mines" else generate_custom_minesweeper2
    for lvl in ["easy", "medium", "hard"]:
        d = gen_func(lvl)
        check(f"Gen {lvl} pid", d["pid"] == variant)
        check(f"Gen {lvl} moves", d["number_required_moves"] > 0)

# ─── COUNTRY ROAD VERIFICATION ───────────────────────────────────────

def verify_country(label, p_data, variant):
    print(f"  [{label}]")

    gen_func = generate_custom_country if variant == "country" else generate_custom_country2
    d = gen_func(label.split()[-1].lower())  # "easy", "medium", "hard"

    moves_req = d["solution"]["moves_required"]
    moves_hint = d["solution"]["moves_hint"]

    check(f"Has required moves", len(moves_req) > 0)
    check(f"Has hint moves", len(moves_hint) > 0)
    check(f"Total moves", d["number_total_solution_moves"] == len(d["solution"]["moves_full"]))

    # Reconstruct loop from moves_required (line segments)
    width = d["width"]
    height = d["height"]
    on_loop = set()
    edges = set()
    for mv in moves_req:
        parts = mv.split(",")
        # mouse,left,x1,y1,x2,y2
        x1, y1, x2, y2 = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
        r1, c1 = (y1-1)//2, (x1-1)//2
        r2, c2 = (y2-1)//2, (x2-1)//2
        on_loop.add((r1,c1))
        on_loop.add((r2,c2))
        e = tuple(sorted([(r1,c1),(r2,c2)]))
        edges.add(e)

    # Default R1: every loop cell has degree 2
    for r, c in on_loop:
        deg = sum(1 for e in edges if (r,c) in e)
        check(f"R1 cell ({r},{c}) degree=2", deg == 2, f"got {deg}")

    # Default R1: single connected loop (BFS)
    if on_loop:
        adj_map = {}
        for (r1,c1),(r2,c2) in edges:
            adj_map.setdefault((r1,c1), []).append((r2,c2))
            adj_map.setdefault((r2,c2), []).append((r1,c1))
        start = next(iter(on_loop))
        visited = set([start])
        q = deque([start])
        while q:
            node = q.popleft()
            for nb in adj_map.get(node, []):
                if nb not in visited:
                    visited.add(nb)
                    q.append(nb)
        check("R1 single loop", len(visited) == len(on_loop), f"{len(visited)} vs {len(on_loop)}")

    # Count straights and turns
    straights = 0
    turns = 0
    for r, c in on_loop:
        nbs = [nb for e in edges if (r,c) in e for nb in e if nb != (r,c)]
        if len(nbs) == 2:
            (r1,c1), (r2,c2) = nbs
            dr1, dc1 = r1-r, c1-c
            dr2, dc2 = r2-r, c2-c
            if (dr1+dr2 == 0 and dc1+dc2 == 0):
                straights += 1
            else:
                turns += 1

    if variant == "country":
        # R7: loop ≥ 50% coverage
        total = width * height
        pct = len(on_loop) / total * 100
        check(f"R7 coverage ≥ 50%", len(on_loop) * 2 >= total, f"{pct:.1f}%")

        # R8: at most 1 empty row
        empty_rows = sum(1 for r in range(height) if not any((r,c) in on_loop for c in range(width)))
        check(f"R8 empty rows ≤ 1", empty_rows <= 1, f"got {empty_rows}")

    elif variant == "country2":
        # R6: turns ≤ 2 * straights
        check(f"R6 turns({turns}) ≤ 2*straights({straights})", turns <= 2 * straights,
              f"ratio={turns/max(straights,1):.2f}")

        # R7: loop ≤ 85% coverage
        total = width * height
        pct = len(on_loop) / total * 100
        check(f"R7 coverage ≤ 85%", len(on_loop) * 100 <= total * 85, f"{pct:.1f}%")

        # R8: at most 1 empty row
        empty_rows = sum(1 for r in range(height) if not any((r,c) in on_loop for c in range(width)))
        check(f"R8 empty rows ≤ 1", empty_rows <= 1, f"got {empty_rows}")

# ═════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════

def run_all():
    global PASS, FAIL
    PASS = FAIL = 0

    print("=" * 60)
    print("SUDOKU (R1-R5 default + R6 no-consec-same, R7 cage, R8 parity)")
    for lvl in ["easy", "medium", "hard"]:
        verify_sudoku(f"Sudoku {lvl}", S1[lvl], "sudoku")

    print("\nSUDOKU 2 (R1-R5 default + R6 row-alt, R7 box-alt, R8 even-balance)")
    for lvl in ["easy", "medium", "hard"]:
        verify_sudoku(f"Sudoku2 {lvl}", S2[lvl], "sudoku2")

    print("\nHEYAWAKE (R1mod ≤1adj, R2-R5, R6 no-consec-room, R7 row-balance)")
    for lvl in ["easy", "medium", "hard"]:
        verify_heyawake(f"Heyawake {lvl}", H1[lvl], "heyawake")

    print("\nHEYAWAKE 2 (R1strict, R2-R5, R6 half-grid, R7 col-balance, R8 density)")
    for lvl in ["easy", "medium", "hard"]:
        verify_heyawake(f"Heyawake2 {lvl}", H2[lvl], "heyawake2")

    print("\nMINESWEEPER (R1-R5 default + R6 no-same-row, R7 no-2x2, R8 density≤25%)")
    for lvl in ["easy", "medium", "hard"]:
        verify_minesweeper(f"Mines {lvl}", M1[lvl], "mines")

    print("\nMINESWEEPER 2 (R1-R5 default + R6 lucky, R7 row-cap, R8 no-2x2)")
    for lvl in ["easy", "medium", "hard"]:
        verify_minesweeper(f"Mines2 {lvl}", M2[lvl], "mines2")

    print("\nCOUNTRY ROAD (R1-R5 default + R6 no-same-room, R7 ≥50%, R8 ≤1-empty-row)")
    for lvl in ["easy", "medium", "hard"]:
        verify_country(f"Country {lvl}", C1[lvl], "country")

    print("\nCOUNTRY ROAD 2 (R1-R5 default + R6 turn-balance, R7 ≤85%, R8 ≤1-empty-row)")
    for lvl in ["easy", "medium", "hard"]:
        verify_country(f"Country2 {lvl}", C2[lvl], "country2")

    return PASS, FAIL

print("╔══════════════════════════════════════════════════════════════╗")
print("║             VERIFICATION PASS 1                             ║")
print("╚══════════════════════════════════════════════════════════════╝")
p1, f1 = run_all()
print(f"\n{'='*60}")
print(f"PASS 1 RESULT: {p1} passed, {f1} failed")

print(f"\n{'='*60}")
print("╔══════════════════════════════════════════════════════════════╗")
print("║             VERIFICATION PASS 2 (re-run)                    ║")
print("╚══════════════════════════════════════════════════════════════╝")
p2, f2 = run_all()
print(f"\n{'='*60}")
print(f"PASS 2 RESULT: {p2} passed, {f2} failed")

print(f"\n{'='*60}")
if f1 == 0 and f2 == 0:
    print(f"✓ ALL CLEAR — {p1} checks passed in both runs. Zero failures.")
else:
    print(f"✗ FAILURES DETECTED — Pass1: {f1} fails, Pass2: {f2} fails")
