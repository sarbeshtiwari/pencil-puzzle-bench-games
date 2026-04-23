import sys
import time
from datetime import datetime, timezone

from puzzle_country import _PUZZLES as _PUZZLE_DATA

_SOLUTIONS = {
    "easy": {
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

_PUZZLES = {}
for _lvl in _PUZZLE_DATA:
    _PUZZLES[_lvl] = {**_PUZZLE_DATA[_lvl], **_SOLUTIONS[_lvl]}


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
        print(f"Usage: python solution_country.py [easy|medium|hard]")
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
