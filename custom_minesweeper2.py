import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 3 hardcoded puzzles from ppbench golden dataset (mines category)
# Easy:    6×6,  6 mines — ppbench golden mines index 1
# Medium:  9×9, 15 mines — ppbench golden mines index 6
# Hard:  12×12, 30 mines — ppbench golden mines index 11
# ---------------------------------------------------------------------------

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "num_mines": 6,
        "url_body": "g1000012221001h1002342112g2g11g2211",
        "solution": [
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0],
        ],
    },
    "medium": {
        "rows": 9, "cols": 9, "num_mines": 15,
        "url_body": "001g2110000112g100000012210000001g1000001222111001g23h433323m12g324g421111",
        "solution": [
            [0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0],
        ],
    },
    "hard": {
        "rows": 12, "cols": 12, "num_mines": 30,
        "url_body": (
            "1g101121212g11101g2g3g42001232213h1112h20023311g24g4122g101234g3g3g3"
            "1001h2224g2000123212g32110001g12g32g2111233213g4g1g11h213g421111222g22g1"
        ),
        "solution": [
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
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


def generate_custom_minesweeper2(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    full, req, hint = _build_moves(rows, cols, p["solution"])
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?mines2/{cols}/{rows}/{p['url_body']}",
        "pid": "mines2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(req),
        "number_total_solution_moves": len(full),
        "puzzlink_url": f"https://puzz.link/p?mines2/{cols}/{rows}/{p['url_body']}",
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
            "num_mines": p["num_mines"],
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
        print(f"Usage: python custom_minesweeper2.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_minesweeper2(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}, Mines: {meta['num_mines']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
