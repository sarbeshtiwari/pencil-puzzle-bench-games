import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "url_body": "j8m952l614k4i2j5i7i12i58g761i935943i826g28i14g",
        "clue_grid": [
            [0, 0, 0, 0, 8, 0, 0, 0, 0],
            [0, 0, 0, 9, 5, 2, 0, 0, 0],
            [0, 0, 0, 6, 1, 4, 0, 0, 0],
            [0, 0, 4, 0, 0, 0, 2, 0, 0],
            [0, 0, 5, 0, 0, 0, 7, 0, 0],
            [0, 1, 2, 0, 0, 0, 5, 8, 0],
            [7, 6, 1, 0, 0, 0, 9, 3, 5],
            [9, 4, 3, 0, 0, 0, 8, 2, 6],
            [0, 2, 8, 0, 0, 0, 1, 4, 0],
        ],
    },
    "medium": {
        "url_body": "1o6h84k76h9j64i7h4k8h8i53j5h71k14h6o2",
        "clue_grid": [
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 6, 0, 0, 8, 4, 0, 0, 0],
            [0, 0, 7, 6, 0, 0, 9, 0, 0],
            [0, 0, 6, 4, 0, 0, 0, 7, 0],
            [0, 4, 0, 0, 0, 0, 0, 8, 0],
            [0, 8, 0, 0, 0, 5, 3, 0, 0],
            [0, 0, 5, 0, 0, 7, 1, 0, 0],
            [0, 0, 0, 1, 4, 0, 0, 6, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 2],
        ],
    },
    "hard": {
        "url_body": "h75q23g8h1k9h2i7h3k6h2i3h4k4h3g45q78h",
        "clue_grid": [
            [0, 0, 7, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 3, 0],
            [8, 0, 0, 1, 0, 0, 0, 0, 0],
            [9, 0, 0, 2, 0, 0, 0, 7, 0],
            [0, 3, 0, 0, 0, 0, 0, 6, 0],
            [0, 2, 0, 0, 0, 3, 0, 0, 4],
            [0, 0, 0, 0, 0, 4, 0, 0, 3],
            [0, 4, 5, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 7, 8, 0, 0],
        ],
    },
}


def generate_puzzle_sudoku(level="easy"):
    p = _PUZZLES[level]
    clue_grid = p["clue_grid"]
    empty = sum(1 for r in range(9) for c in range(9) if clue_grid[r][c] == 0)
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?sudoku/9/9/{p['url_body']}",
        "pid": "sudoku",
        "sort_key": None,
        "width": 9,
        "height": 9,
        "area": 81,
        "number_required_moves": 0,
        "number_total_solution_moves": 0,
        "puzzlink_url": f"https://puzz.link/p?sudoku/9/9/{p['url_body']}",
        "source": {
            "site_name": "ppbench_golden",
            "page_url": None,
            "feed_type": "golden_dataset",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": 9,
            "db_h": 9,
            "level": level,
            "clue_count": 81 - empty,
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
        print(f"Usage: python puzzle_sudoku.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_sudoku(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Clues: {meta['clue_count']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
