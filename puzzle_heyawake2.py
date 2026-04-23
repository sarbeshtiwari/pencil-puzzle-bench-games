import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 8, "cols": 8,
        "url_body": "022gkf3gc2007o00o01s01v07",
    },
    "medium": {
        "rows": 8, "cols": 8,
        "url_body": "fismnltf9aag603j1pg0v00gh0g0h221g2h21g",
    },
    "hard": {
        "rows": 13, "cols": 17,
        "url_body": (
            "2401200h0082841420i1090g4g82841401000g00800000001vvvg"
            "0000000000000003g003vvv00000004309-1575g87"
        ),
    },
}


def generate_puzzle_heyawake2(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?heyawake2/{cols}/{rows}/{p['url_body']}",
        "pid": "heyawake2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": 0,
        "number_total_solution_moves": 0,
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
            "num_shaded": 0,
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
        print(f"Usage: python puzzle_heyawake2.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_heyawake2(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
