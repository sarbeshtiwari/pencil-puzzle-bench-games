import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 10, "cols": 10,
        "url_body": "1hufproq6nb9eil52aeehpcsru13esjj0cfg7332g3g34g51i1g251613",
    },
    "medium": {
        "rows": 18, "cols": 10,
        "url_body": "8goih3264i4gd0i1k284g905266cc8og07v808700fsfuo10201o0007vbo8304s0vsg44ga23g4g434heg113",
    },
    "hard": {
        "rows": 10, "cols": 18,
        "url_body": "40401020240g310018104g80g20440gg00vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvo3h4h5q4i5h6l",
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
