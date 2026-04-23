import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "num_mines": 6,
        "url_body": "2g21g12g433212h2g012221000000000000",
    },
    "medium": {
        "rows": 9, "cols": 9, "num_mines": 15,
        "url_body": "012h200001g4g21112433111g1i10011123210001111000001h210011212g3212g2012h12g20",
    },
    "hard": {
        "rows": 12, "cols": 12, "num_mines": 30,
        "url_body": (
            "1g212g1001g2233g2110012h3g4310000113g3h1111111g222212g33g3"
            "1100002h4h01232124g43212i12g4g212g33223g33g2g21001g212g2110"
            "0011102220000000001g1"
        ),
    },
}


def generate_puzzle_minesweeper(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?mines/{cols}/{rows}/{p['url_body']}",
        "pid": "mines",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": 0,
        "number_total_solution_moves": 0,
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
            "moves_full": [],
            "moves_required": [],
            "moves_hint": [],
        },
    }


if __name__ == "__main__":
    import json

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python puzzle_minesweeper.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_minesweeper(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}, Mines: {meta['num_mines']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
