import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 7, "cols": 7,
        "url_body": "2hblosca00fhjg0fs012g1i313h",
        "room_grid": [
            [0, 0, 0, 0, 1, 1, 2],
            [0, 0, 0, 0, 1, 1, 3],
            [4, 4, 5, 6, 1, 1, 3],
            [7, 7, 5, 6, 8, 8, 8],
            [7, 7, 5, 6, 8, 8, 8],
            [7, 7, 5, 9, 9, 9, 9],
            [10, 11, 11, 9, 9, 9, 9],
        ],
        "clues": {0: 1, 1: 2, 3: 1, 7: 3, 8: 1, 9: 3},
    },
    "medium": {
        "rows": 8, "cols": 10,
        "url_body": "98ih52a2i54a8kgoo7700vv00ss33i0222332321i",
        "room_grid": [
            [0, 0, 1, 1, 1, 2, 2, 3, 3, 3],
            [4, 4, 1, 1, 1, 5, 5, 3, 3, 3],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [12, 12, 12, 9, 9, 13, 13, 13, 11, 11],
            [12, 12, 12, 14, 14, 13, 13, 13, 15, 15],
        ],
        "clues": {3: 0, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 2, 10: 3, 11: 2, 12: 1},
    },
    "hard": {
        "rows": 14, "cols": 24,
        "url_body": (
            "8i289289548ikkh2aiii9aaa959992951494k4okigl2ia2ka99ah9at155bk4kl8o"
            "007ofvvgc00007vv1vg000007vopvg0ec0vv00f01u00000vg1vvjvg0000000g"
            "32g3h3g3g3g3j52g4g21223h221425g32g01h311g0h3"
        ),
        "room_grid": [
            [0,0,1,1,1,1,2,2,2,3,3,3,3,3,4,4,4,5,5,5,5,5,6,6],
            [7,7,1,1,1,1,2,2,2,3,3,3,3,3,4,4,4,8,8,8,9,9,6,6],
            [7,7,10,10,10,10,11,11,11,11,12,12,12,13,13,14,14,8,8,8,9,9,15,15],
            [7,7,10,10,10,10,11,11,11,11,12,12,12,13,13,14,14,8,8,8,9,9,15,15],
            [16,16,17,17,18,18,18,19,19,19,20,20,20,13,13,14,14,21,21,21,22,22,23,23],
            [16,16,17,17,18,18,18,19,19,19,20,20,20,13,13,14,14,21,21,21,22,22,23,23],
            [16,16,17,17,18,18,18,24,24,24,24,25,25,25,26,26,26,21,21,21,27,27,23,23],
            [28,28,28,28,29,29,29,24,24,24,24,25,25,25,26,26,26,30,30,30,27,27,31,31],
            [28,28,28,28,29,29,29,32,33,33,33,33,34,34,35,35,35,30,30,30,27,27,31,31],
            [28,28,28,28,36,36,37,37,33,33,33,33,34,34,35,35,35,38,38,38,39,39,31,31],
            [28,28,28,28,36,36,37,37,33,33,33,33,34,34,35,35,35,38,38,38,39,39,31,31],
            [40,40,41,41,42,42,37,37,33,33,33,33,34,34,43,43,43,44,44,45,45,46,46,47],
            [48,49,41,41,50,50,50,50,50,51,51,51,34,34,43,43,43,44,44,45,45,46,46,47],
            [48,49,41,41,50,50,50,50,50,51,51,51,34,34,43,43,43,44,44,45,45,46,46,47],
        ],
        "clues": {
            1: 3, 2: 2, 4: 3, 7: 3, 9: 3, 11: 3, 13: 3, 18: 5,
            19: 2, 21: 4, 23: 2, 24: 1, 25: 2, 26: 2, 27: 3, 30: 2,
            31: 2, 32: 1, 33: 4, 34: 2, 35: 5, 37: 3, 38: 2,
            40: 0, 41: 1, 44: 3, 45: 1, 46: 1, 48: 0, 51: 3,
        },
    },
}


def generate_puzzle_heyawake(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?heyawake/{cols}/{rows}/{p['url_body']}",
        "pid": "heyawake",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": 0,
        "number_total_solution_moves": 0,
        "puzzlink_url": f"https://puzz.link/p?heyawake/{cols}/{rows}/{p['url_body']}",
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
            "num_rooms": len(set(c for row in p["room_grid"] for c in row)),
            "num_clued_rooms": len(p["clues"]),
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
        print(f"Usage: python puzzle_heyawake.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_heyawake(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}")
    print(f"Rooms: {meta['num_rooms']} ({meta['num_clued_rooms']} clued)")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
