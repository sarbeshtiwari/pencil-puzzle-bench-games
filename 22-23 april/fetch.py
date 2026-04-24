# source /Users/apple/Desktop/morpheus/data/ .venv/bin/activate

from ppbench import load_dataset
from collections import defaultdict

puzzles = load_dataset("golden")  # 300 puzzles, 20 types × 15 each

by_type = defaultdict(list)
for p in puzzles:
    by_type[p["pid"]].append(p)

print(f"Total puzzles: {len(puzzles)}")
print(f"Puzzle types: {len(by_type)}")
print("=" * 70)

for pid in sorted(by_type):
    group = by_type[pid]
    print(f"\n{pid.upper()} ({len(group)} puzzles)")
    print("-" * 50)
    for i, p in enumerate(group, 1):
        print(f"  {i:2d}. {p['width']}x{p['height']} | "
              f"moves: {p['number_required_moves']}/{p['number_total_solution_moves']} | "
              f"{p['puzzle_url']}")