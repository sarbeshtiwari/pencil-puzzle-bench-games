import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 3 hardcoded minesweeper puzzles (generated with seed=42)
# Easy:   6×6,  6 mines  — URL body uses puzz.link 'mines' variety
# Medium: 9×9, 15 mines
# Hard:  12×12, 30 mines
# ---------------------------------------------------------------------------

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "num_mines": 6,
        "url_body": "2g21g12g433212h2g012221000000000000",
        "solution": [
            [0, 1, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 1],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ],
    },
    "medium": {
        "rows": 9, "cols": 9, "num_mines": 15,
        "url_body": "012h200001g4g21112433111g1i10011123210001111000001h210011212g3212g2012h12g20",
        "solution": [
            [0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 1, 0, 0, 1, 0, 0],
        ],
    },
    "hard": {
        "rows": 12, "cols": 12, "num_mines": 30,
        "url_body": (
            "1g212g1001g2233g2110012h3g4310000113g3h1111111g222212g33g3"
            "1100002h4h01232124g43212i12g4g212g33223g33g2g21001g212g2110"
            "0011102220000000001g1"
        ),
        "solution": [
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
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


def generate_custom_minesweeper(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    full, req, hint = _build_moves(rows, cols, p["solution"])
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?mines/{cols}/{rows}/{p['url_body']}",
        "pid": "mines",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(req),
        "number_total_solution_moves": len(full),
        "puzzlink_url": f"https://puzz.link/p?mines/{cols}/{rows}/{p['url_body']}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
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
        print(f"Usage: python custom_minesweeper.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_minesweeper(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}, Mines: {meta['num_mines']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
