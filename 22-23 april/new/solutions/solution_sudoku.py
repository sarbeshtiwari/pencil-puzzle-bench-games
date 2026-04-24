import sys
import time
from datetime import datetime, timezone

from puzzle_sudoku import _PUZZLES as _PUZZLE_DATA

_SOLUTIONS = {
    "easy": {
        "solution": [
            [4, 5, 9, 7, 8, 3, 6, 1, 2],
            [1, 3, 6, 9, 5, 2, 4, 7, 8],
            [2, 8, 7, 6, 1, 4, 3, 5, 9],
            [8, 7, 4, 5, 3, 6, 2, 9, 1],
            [3, 9, 5, 8, 2, 1, 7, 6, 4],
            [6, 1, 2, 4, 9, 7, 5, 8, 3],
            [7, 6, 1, 2, 4, 8, 9, 3, 5],
            [9, 4, 3, 1, 7, 5, 8, 2, 6],
            [5, 2, 8, 3, 6, 9, 1, 4, 7],
        ],
    },
    "medium": {
        "solution": [
            [1, 5, 8, 7, 9, 2, 4, 3, 6],
            [9, 6, 3, 5, 8, 4, 2, 1, 7],
            [4, 2, 7, 6, 3, 1, 9, 5, 8],
            [2, 3, 6, 4, 1, 8, 5, 7, 9],
            [5, 4, 9, 2, 7, 3, 6, 8, 1],
            [7, 8, 1, 9, 6, 5, 3, 2, 4],
            [6, 9, 5, 8, 2, 7, 1, 4, 3],
            [3, 7, 2, 1, 4, 9, 8, 6, 5],
            [8, 1, 4, 3, 5, 6, 7, 9, 2],
        ],
    },
    "hard": {
        "solution": [
            [2, 6, 7, 5, 3, 9, 4, 1, 8],
            [4, 1, 9, 8, 7, 6, 2, 3, 5],
            [8, 5, 3, 1, 4, 2, 6, 9, 7],
            [9, 8, 4, 2, 6, 5, 3, 7, 1],
            [7, 3, 1, 4, 9, 8, 5, 6, 2],
            [5, 2, 6, 7, 1, 3, 9, 8, 4],
            [6, 7, 8, 9, 2, 4, 1, 5, 3],
            [3, 4, 5, 6, 8, 1, 7, 2, 9],
            [1, 9, 2, 3, 5, 7, 8, 4, 6],
        ],
    },
}

_PUZZLES = {}
for _lvl in _PUZZLE_DATA:
    _PUZZLES[_lvl] = {**_PUZZLE_DATA[_lvl], **_SOLUTIONS[_lvl]}


def _build_moves(clue_grid, solution):
    moves = []
    for r in range(9):
        for c in range(9):
            if clue_grid[r][c] == 0:
                x = 1 + c * 2
                y = 1 + r * 2
                moves.append(f"mouse,left,{x},{y};key,{solution[r][c]}")
    return moves


def generate_custom_sudoku(level="easy"):
    p = _PUZZLES[level]
    moves = _build_moves(p["clue_grid"], p["solution"])
    now = datetime.now(timezone.utc).isoformat()
    empty = len(moves)

    return {
        "puzzle_url": f"http://pzv.jp/p.html?sudoku/9/9/{p['url_body']}",
        "pid": "sudoku",
        "sort_key": None,
        "width": 9,
        "height": 9,
        "area": 81,
        "number_required_moves": empty,
        "number_total_solution_moves": empty,
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
            "moves_full": moves,
            "moves_required": moves,
            "moves_hint": [],
        },
    }


if __name__ == "__main__":
    import json

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python solution_sudoku.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_sudoku(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Clues: {meta['clue_count']}, Empty: {puzzle_data['number_required_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
