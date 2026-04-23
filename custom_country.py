import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 3 hardcoded puzzles from ppbench golden dataset, sorted by difficulty
# Easy:    5×5,  6 rooms, 16 required — URL body: 013n0vu03154g2
# Medium: 10×10, 20 rooms, 72 required — URL body: 24gelnnvem7u6vd9bg7tbqlh3i9q8s4nda1vg43j6h1k2h5
# Hard:  15×15, 49 rooms, 170 required — URL body: al4la9alilb59m9bcimgi91d96qidikql9laial4la...
# ---------------------------------------------------------------------------

_PUZZLES = {
    "easy": {
        "rows": 5, "cols": 5,
        "url_body": "013n0vu03154g2",
        "room_grid": [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [1, 1, 2, 2, 2],
            [3, 3, 4, 5, 2],
            [3, 3, 4, 5, 2],
        ],
        "clues": {0: 3, 1: 1, 2: 5, 3: 4, 5: 2},
        "v_lines": [
            [False, False, False, False, False],
            [True,  False, True,  False, False],
            [True,  False, False, False, True],
            [True,  True,  False, True,  True],
        ],
        "h_lines": [
            [False, False, False, False],
            [True,  True,  False, False],
            [False, False, True,  True],
            [False, True,  True,  False],
            [True,  False, False, True],
        ],
    },
    "medium": {
        "rows": 10, "cols": 10,
        "url_body": "24gelnnvem7u6vd9bg7tbqlh3i9q8s4nda1vg43j6h1k2h5",
        "room_grid": [
            [0, 0, 0, 0, 1, 1, 1, 1, 2, 2],
            [0, 0, 3, 3, 3, 3, 3, 3, 2, 4],
            [0, 3, 3, 5, 5, 6, 6, 3, 4, 4],
            [7, 3, 8, 5, 9, 9, 6, 3, 4, 10],
            [7, 3, 8, 11, 12, 12, 6, 3, 10, 10],
            [7, 8, 8, 11, 3, 3, 3, 3, 13, 10],
            [7, 14, 8, 11, 3, 13, 13, 13, 13, 10],
            [7, 14, 14, 11, 3, 15, 13, 15, 15, 16],
            [7, 17, 17, 11, 11, 15, 15, 15, 16, 16],
            [7, 17, 17, 11, 18, 19, 19, 19, 19, 19],
        ],
        "clues": {1: 4, 2: 3, 7: 6, 10: 1, 16: 2, 19: 5},
        "v_lines": [
            [0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 1, 0, 1, 0],
            [1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 0, 0, 1, 0],
            [1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
            [1, 1, 0, 1, 0, 1, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        ],
        "h_lines": [
            [0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 1, 0, 0, 1],
            [0, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 1],
            [1, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 1, 1, 1, 1, 1],
        ],
    },
    "hard": {
        "rows": 15, "cols": 15,
        "url_body": (
            "al4la9alilb59m9bcimgi91d96qidikql9laial4la000pvv6000frvu0007vuo3fvs"
            "000fvru000cvvj00032234413g2g2g44i2g4g44362g33g144i42h13g3i4"
        ),
        "room_grid": [
            [0,0,1,1,2,2,3,3,4,4,5,5,5,6,6],
            [0,0,1,1,2,2,3,3,4,4,5,5,5,6,6],
            [7,7,1,1,8,8,9,9,10,10,11,11,12,13,13],
            [7,7,14,14,8,8,9,9,10,10,11,11,12,13,13],
            [7,7,14,14,8,8,15,15,15,16,17,17,12,18,18],
            [19,19,20,20,20,21,21,22,22,16,17,17,12,18,18],
            [19,19,20,20,20,21,21,22,22,16,17,17,23,23,23],
            [24,24,24,25,25,25,26,26,26,16,16,16,23,23,23],
            [24,24,24,27,27,25,28,28,29,29,30,30,30,31,31],
            [32,32,33,27,27,25,28,28,29,29,30,30,30,31,31],
            [32,32,33,27,27,25,34,34,34,35,35,36,36,37,37],
            [38,38,33,39,39,40,40,41,41,35,35,36,36,37,37],
            [38,38,33,39,39,40,40,41,41,35,35,42,42,37,37],
            [43,43,44,44,44,45,45,46,46,47,47,42,42,48,48],
            [43,43,44,44,44,45,45,46,46,47,47,42,42,48,48],
        ],
        "clues": {
            0: 3, 1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 1, 7: 3, 9: 2,
            11: 2, 13: 4, 14: 4, 18: 2, 20: 4, 22: 4, 23: 4, 24: 3,
            25: 6, 26: 2, 28: 3, 29: 3, 31: 1, 32: 4, 33: 4, 37: 4,
            38: 2, 41: 1, 42: 3, 44: 3, 48: 4,
        },
        "v_lines": [
            [0,1,0,0,1,0,1,0,1,1,0,0,1,0,0],
            [1,0,0,0,1,0,1,0,0,0,0,0,0,1,0],
            [0,1,0,0,0,1,0,0,1,1,0,0,1,0,1],
            [0,0,0,1,1,0,0,0,0,0,0,0,1,1,0],
            [0,0,1,0,0,1,1,0,1,0,1,1,1,1,0],
            [1,1,0,1,0,1,1,1,0,0,1,0,0,1,0],
            [1,0,0,0,0,0,0,0,1,0,0,1,0,0,1],
            [0,0,0,0,0,1,0,1,0,1,0,0,0,1,0],
            [0,0,0,1,1,1,1,0,0,1,0,0,1,0,0],
            [1,0,1,1,1,1,1,0,1,0,0,1,0,0,0],
            [0,1,1,1,0,0,0,0,0,1,1,1,1,0,1],
            [0,1,1,0,1,1,1,0,0,1,1,0,0,0,1],
            [0,1,0,0,0,1,0,1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,1,0,1,0,1,0,0,1,1],
        ],
        "h_lines": [
            [0,1,1,1,0,0,1,1,0,1,1,1,0,0],
            [1,0,0,0,0,0,0,0,1,0,0,0,1,0],
            [1,0,0,0,1,0,1,1,0,1,1,1,0,1],
            [0,1,1,0,1,0,0,0,1,0,0,0,0,1],
            [0,0,1,0,1,0,1,1,0,0,1,0,0,0],
            [1,0,1,0,0,0,0,1,0,0,0,1,0,0],
            [0,1,1,0,0,1,0,1,0,0,1,0,0,1],
            [1,1,1,1,1,0,0,1,0,1,1,0,0,1],
            [0,0,0,1,0,0,1,0,0,0,0,0,1,0],
            [1,1,0,0,0,0,0,0,1,0,0,1,0,0],
            [1,0,0,0,1,0,1,1,0,1,0,0,1,1],
            [0,0,0,1,0,1,0,0,0,0,0,1,0,0],
            [0,0,1,1,0,0,1,0,0,0,1,1,0,0],
            [1,0,0,0,0,1,0,1,0,1,0,0,1,0],
            [1,1,1,1,1,1,0,0,1,1,0,0,0,1],
        ],
    },
}


def _build_moves(rows, cols, v_lines, h_lines):
    full, req, hint = [], [], []

    for r in range(rows - 1):
        for c in range(cols):
            bx = 2 * c + 1
            by = 2 * (r + 1)
            if v_lines[r][c]:
                y1 = 2 * r + 1
                y2 = 2 * (r + 1) + 1
                m = f"mouse,left,{bx},{y1},{bx},{y2}"
                full.append(m)
                req.append(m)
            else:
                m = f"mouse,right,{bx},{by}"
                full.append(m)
                hint.append(m)

    for r in range(rows):
        for c in range(cols - 1):
            bx = 2 * (c + 1)
            by = 2 * r + 1
            if h_lines[r][c]:
                x1 = 2 * c + 1
                x2 = 2 * (c + 1) + 1
                m = f"mouse,left,{x1},{by},{x2},{by}"
                full.append(m)
                req.append(m)
            else:
                m = f"mouse,right,{bx},{by}"
                full.append(m)
                hint.append(m)

    return full, req, hint


def generate_custom_country(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    full, req, hint = _build_moves(rows, cols, p["v_lines"], p["h_lines"])
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?country/{cols}/{rows}/{p['url_body']}",
        "pid": "country",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(req),
        "number_total_solution_moves": len(full),
        "puzzlink_url": f"https://puzz.link/p?country/{cols}/{rows}/{p['url_body']}",
        "source": {
            "site_name": "ppbench_golden",
            "page_url": None,
            "feed_type": "golden_dataset",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "level": level,
            "num_rooms": len(set(c for row in p["room_grid"] for c in row)),
            "num_clued_rooms": len(p["clues"]),
        },
        "created_at": now,
        "solution": {
            "moves_full": full,
            "moves_required": req,
            "moves_hint": hint,
        },
    }


if __name__ == "__main__":
    import json

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python custom_country.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_country(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}")
    print(f"Rooms: {meta['num_rooms']} ({meta['num_clued_rooms']} clued)")
    print(f"Lines (required moves): {puzzle_data['number_required_moves']}")
    print(f"Total moves: {puzzle_data['number_total_solution_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
