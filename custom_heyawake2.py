import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 3 hardcoded puzzles from ppbench golden dataset, sorted by difficulty
# Easy:    8×8,  7 shaded — ppbench golden heyawake index 12
# Medium:  8×8, 18 shaded — ppbench golden heyawake index 4
# Hard:  17×13, 64 shaded — ppbench golden heyawake index 0
# ---------------------------------------------------------------------------

_PUZZLES = {
    "easy": {
        "rows": 8, "cols": 8,
        "url_body": "022gkf3gc2007o00o01s01v07",
        "solution": [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
    },
    "medium": {
        "rows": 8, "cols": 8,
        "url_body": "fismnltf9aag603j1pg0v00gh0g0h221g2h21g",
        "solution": [
            [0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0, 1, 0],
            [1, 0, 0, 1, 0, 0, 0, 1],
            [0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0],
        ],
    },
    "hard": {
        "rows": 13, "cols": 17,
        "url_body": (
            "2401200h0082841420i1090g4g82841401000g00800000001vvvg"
            "0000000000000003g003vvv00000004309-1575g87"
        ),
        "solution": [
            [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1],
        ],
    },
}


def _build_moves(rows, cols, solution):
    full, req, hint = [], [], []
    for r in range(rows):
        for c in range(cols):
            x, y = 1 + c * 2, 1 + r * 2
            if solution[r][c] == 1:
                m = f"mouse,left,{x},{y}"
                full.append(m)
                req.append(m)
            else:
                m = f"mouse,right,{x},{y}"
                full.append(m)
                hint.append(m)
    return full, req, hint


def generate_custom_heyawake2(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    full, req, hint = _build_moves(rows, cols, p["solution"])
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?heyawake2/{cols}/{rows}/{p['url_body']}",
        "pid": "heyawake2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(req),
        "number_total_solution_moves": len(full),
        "puzzlink_url": f"https://puzz.link/p?heyawake2/{cols}/{rows}/{p['url_body']}",
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
            "num_shaded": len(req),
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
        print(f"Usage: python custom_heyawake2.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_heyawake2(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}")
    print(f"Shaded cells: {puzzle_data['number_required_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
