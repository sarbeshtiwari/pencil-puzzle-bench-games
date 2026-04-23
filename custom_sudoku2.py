import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 3 hardcoded puzzles from ppbench golden dataset, sorted by difficulty
# Easy:   28 clues, 53 empty — ppbench golden sudoku index 3
# Medium: 24 clues, 57 empty — ppbench golden sudoku index 11
# Hard:   20 clues, 61 empty — ppbench golden sudoku index 5
# ---------------------------------------------------------------------------

_PUZZLES = {
    "easy": {
        "url_body": "t289h283g9g6j1g7g3h346g827h1i5g4h678g4g2l638p",
        "clue_grid": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 8, 9, 0],
            [0, 2, 8, 3, 0, 9, 0, 6, 0],
            [0, 0, 0, 1, 0, 7, 0, 3, 0],
            [0, 3, 4, 6, 0, 8, 2, 7, 0],
            [0, 1, 0, 0, 0, 5, 0, 4, 0],
            [0, 6, 7, 8, 0, 4, 0, 2, 0],
            [0, 0, 0, 0, 0, 6, 3, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        "solution": [
            [6, 9, 3, 7, 8, 1, 4, 5, 2],
            [1, 7, 5, 4, 6, 2, 8, 9, 3],
            [4, 2, 8, 3, 5, 9, 1, 6, 7],
            [9, 8, 2, 1, 4, 7, 6, 3, 5],
            [5, 3, 4, 6, 9, 8, 2, 7, 1],
            [7, 1, 6, 2, 3, 5, 9, 4, 8],
            [3, 6, 7, 8, 1, 4, 5, 2, 9],
            [2, 5, 1, 9, 7, 6, 3, 8, 4],
            [8, 4, 9, 5, 2, 3, 7, 1, 6],
        ],
    },
    "medium": {
        "url_body": "g69j3g5i48h98g2i6k2h4s7h9k8i5g12h58i4g1j82g",
        "clue_grid": [
            [0, 6, 9, 0, 0, 0, 0, 3, 0],
            [5, 0, 0, 0, 4, 8, 0, 0, 9],
            [8, 0, 2, 0, 0, 0, 6, 0, 0],
            [0, 0, 0, 2, 0, 0, 4, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 7, 0, 0, 9, 0, 0, 0],
            [0, 0, 8, 0, 0, 0, 5, 0, 1],
            [2, 0, 0, 5, 8, 0, 0, 0, 4],
            [0, 1, 0, 0, 0, 0, 8, 2, 0],
        ],
        "solution": [
            [4, 6, 9, 7, 5, 2, 1, 3, 8],
            [5, 3, 1, 6, 4, 8, 2, 7, 9],
            [8, 7, 2, 1, 9, 3, 6, 4, 5],
            [9, 8, 6, 2, 3, 5, 4, 1, 7],
            [3, 2, 4, 8, 1, 7, 9, 5, 6],
            [1, 5, 7, 4, 6, 9, 3, 8, 2],
            [7, 4, 8, 3, 2, 6, 5, 9, 1],
            [2, 9, 3, 5, 8, 1, 7, 6, 4],
            [6, 1, 5, 9, 7, 4, 8, 2, 3],
        ],
    },
    "hard": {
        "url_body": "h836m8m9j4m35h4g5g1g2h63m2j7m7m546h",
        "clue_grid": [
            [0, 0, 8, 3, 6, 0, 0, 0, 0],
            [0, 0, 0, 8, 0, 0, 0, 0, 0],
            [0, 0, 9, 0, 0, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0, 3, 5, 0],
            [0, 4, 0, 5, 0, 1, 0, 2, 0],
            [0, 6, 3, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 7, 0, 0],
            [0, 0, 0, 0, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 5, 4, 6, 0, 0],
        ],
        "solution": [
            [4, 1, 8, 3, 6, 2, 5, 9, 7],
            [2, 7, 5, 8, 4, 9, 1, 6, 3],
            [6, 3, 9, 7, 1, 5, 8, 4, 2],
            [1, 9, 2, 4, 7, 6, 3, 5, 8],
            [8, 4, 7, 5, 3, 1, 9, 2, 6],
            [5, 6, 3, 9, 2, 8, 4, 7, 1],
            [9, 2, 4, 6, 8, 3, 7, 1, 5],
            [3, 5, 6, 1, 9, 7, 2, 8, 4],
            [7, 8, 1, 2, 5, 4, 6, 3, 9],
        ],
    },
}


def _build_moves(clue_grid, solution):
    moves = []
    for r in range(9):
        for c in range(9):
            if clue_grid[r][c] == 0:
                x = 1 + c * 2
                y = 1 + r * 2
                moves.append(f"mouse,left,{x},{y};key,{solution[r][c]}")
    return moves


def generate_custom_sudoku2(level="easy"):
    p = _PUZZLES[level]
    moves = _build_moves(p["clue_grid"], p["solution"])
    now = datetime.now(timezone.utc).isoformat()
    empty = len(moves)

    return {
        "puzzle_url": f"http://pzv.jp/p.html?sudoku2/9/9/{p['url_body']}",
        "pid": "sudoku2",
        "sort_key": None,
        "width": 9,
        "height": 9,
        "area": 81,
        "number_required_moves": empty,
        "number_total_solution_moves": empty,
        "puzzlink_url": f"https://puzz.link/p?sudoku2/9/9/{p['url_body']}",
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
        print(f"Usage: python custom_sudoku2.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_sudoku2(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Clues: {meta['clue_count']}, Empty: {puzzle_data['number_required_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
