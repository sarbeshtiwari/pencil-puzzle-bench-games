import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 5, "cols": 5,
        "url_body": "013n0vu03154g2",
    },
    "medium": {
        "rows": 10, "cols": 10,
        "url_body": "24gelnnvem7u6vd9bg7tbqlh3i9q8s4nda1vg43j6h1k2h5",
    },
    "hard": {
        "rows": 12, "cols": 12,
        "url_body": "5k2qplcqndbklaahahuaeja945000or1o66u08e00vvocvc7jj37p01351j34366g134k3g225g",
    },
}


def generate_puzzle_country2(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?country2/{cols}/{rows}/{p['url_body']}",
        "pid": "country2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": 0,
        "number_total_solution_moves": 0,
        "puzzlink_url": f"https://puzz.link/p?country2/{cols}/{rows}/{p['url_body']}",
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
        print("Usage: python puzzle_country2.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_country2(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    print(f"\nLevel: {level}")
    print(f"Grid: {puzzle_data['width']}×{puzzle_data['height']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
