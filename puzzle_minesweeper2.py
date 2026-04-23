import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "num_mines": 6,
        "url_body": "g1000012221001h1002342112g2g11g2211",
    },
    "medium": {
        "rows": 9, "cols": 9, "num_mines": 15,
        "url_body": "001g2110000112g100000012210000001g1000001222111001g23h433323m12g324g421111",
    },
    "hard": {
        "rows": 12, "cols": 12, "num_mines": 30,
        "url_body": (
            "1g101121212g11101g2g3g42001232213h1112h20023311g24g4122g101234g3g3g3"
            "1001h2224g2000123212g32110001g12g32g2111233213g4g1g11h213g421111222g22g1"
        ),
    },
}


def generate_puzzle_minesweeper2(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?mines2/{cols}/{rows}/{p['url_body']}",
        "pid": "mines2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": 0,
        "number_total_solution_moves": 0,
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
            "moves_full": [],
            "moves_required": [],
            "moves_hint": [],
        },
    }


if __name__ == "__main__":
    import json

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python puzzle_minesweeper2.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_minesweeper2(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}, Mines: {meta['num_mines']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
