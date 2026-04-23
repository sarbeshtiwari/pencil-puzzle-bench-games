# Puzzle Rules

All custom games have 3 difficulty levels: **easy**, **medium**, **hard**.

| Game | Easy | Medium | Hard |
|---|---|---|---|
| Sudoku | 9×9, 31 clues | 9×9, 22 clues | 9×9, 20 clues |
| Heyawake | 7×7, 10 rooms | 10×8, 11 rooms | 24×14, 40 rooms |
| Minesweeper | 6×6, 6 mines | 9×9, 15 mines | 12×12, 30 mines |
| Country Road | 5×5, 6 rooms | 10×10, 20 rooms | 15×15, 49 rooms |

Each category also has a **variant** (Sudoku 2, Heyawake 2, Minesweeper 2, Country Road 2) with different custom rules.

| Game | Easy | Medium | Hard |
|---|---|---|---|
| Sudoku 2 | 9×9, 28 clues | 9×9, 24 clues | 9×9, 20 clues |
| Heyawake 2 | 8×8, 7 shaded | 8×8, 18 shaded | 17×13, 64 shaded |
| Minesweeper 2 | 6×6, 6 mines | 9×9, 15 mines | 12×12, 30 mines |
| Country Road 2 | 5×5, 16 lines | 10×10, 72 lines | 12×12, 104 lines |

Usage: `python custom_<game>.py [easy|medium|hard]` (defaults to easy)

---

## Sudoku

1. Fill every empty cell with a digit from 1–9
2. Each **row** must contain all digits 1–9 exactly once
3. Each **column** must contain all digits 1–9 exactly once
4. Each **3×3 box** (9 thick-bordered regions) must contain all digits 1–9 exactly once
5. Pre-filled digits (clues) cannot be changed

6. **No consecutive same input** — you cannot enter the same digit twice in a row; the cell will flash red and the input will be reverted
7. **Killer cage** — a random 3×3 region (one of the nine standard boxes) is highlighted with a red dashed border and a target sum displayed in its top-left corner. The digits you place in that cage must sum to the target number. Checked when you click "Check Answer"
8. **Digit parity alternation** — if you enter an odd digit (1, 3, 5, 7, 9), your next digit must be even (2, 4, 6, 8), and vice versa. **Deadlock bypass**: if no remaining empty cell can legally accept an opposite-parity digit (via row/col/box constraints), same-parity input is allowed

### puzz.link Controls

- Click a cell, then type a digit (1–9) to place it
- Arrow keys to navigate between cells
- Entering the same digit consecutively is blocked (rule 6)
- The red dashed cage must sum to the displayed target (rule 7, checked on "Check Answer")
- Entering a digit with same odd/even parity as last digit is blocked (rule 8), unless deadlocked

## Heyawake

Shade some cells black while leaving others white in a grid divided into rooms.

1. **No adjacent shading (relaxed)** — at most **one pair** of orthogonally adjacent shaded cells is allowed in the entire grid. Two or more adjacent pairs will fail the check
2. **White connectivity** — all unshaded cells must form a single connected group (reachable from each other moving orthogonally through white cells only)
3. **Numbered rooms** — if a room contains a number N, exactly N cells in that room must be shaded
4. **Unnumbered rooms** — may contain any number of shaded cells (including zero)
5. **Three-room rule** — a straight horizontal or vertical line of consecutive white cells cannot pass through 3 or more rooms

6. **No consecutive same-room shading** — after shading a cell in a room, your next shade action must be in a different room. The cell will flash red and revert if you try to shade in the same room consecutively. Unshading/marking white does not trigger this rule
7. **Row shade balance** — no single row can have more than ⌈cols/2⌉ shaded cells (e.g., in a 6-column grid, max 3 per row). Checked when you click "Check Answer"

### puzz.link Controls

- Left-click a cell to shade it (black)
- Right-click a cell to mark it white (dot)
- Shading the same room twice in a row is blocked (rule 6)
- Row shade limit is validated on "Check Answer" (rule 7)
- Adjacent shading: 1 pair allowed, 2+ pairs fail on "Check Answer" (rule 1)

## Minesweeper

Classic Minesweeper — all cells start hidden. Reveal safe cells and flag mines.

1. **Hidden grid** — all cells start face-down; you must reveal them by clicking
2. **Left-click to reveal** — reveals a cell. If it has a number (1–8), it shows how many of its 8 neighbours are mines. If it has 0 adjacent mines, all surrounding cells auto-reveal (flood fill)
3. **Right-click to flag** — places a flag on a hidden cell to mark it as a suspected mine. Right-click again to remove the flag
4. **Mine hit = game over** — revealing a mine cell ends the game immediately; all mines are shown
5. **Win condition** — reveal every non-mine cell to win. Flagging is optional

6. **No consecutive same-row reveals** — after revealing a cell, your next reveal must be in a different row. The cell will flash red and revert if you try to reveal in the same row consecutively. **Deadlock bypass**: if all remaining hidden safe cells are in the same row, same-row reveals are allowed
7. **No 2×2 mine block** — no 2×2 square of cells can all be mines. Checked when you click "Check Answer"
8. **Mine density ≤ 25%** — the total number of mines must not exceed 25% of the grid area. Checked when you click "Check Answer"

### puzz.link Controls

- Left-click a hidden cell to reveal it
- Right-click a hidden cell to toggle a flag (🚩)
- Flagged cells cannot be revealed (unflag first)
- Revealing in the same row as last reveal is blocked (rule 6), unless deadlocked
- 2×2 mine block and mine density are validated on "Check Answer" (rules 7–8)

## Country Road

Draw a single closed loop through cell centers on a grid divided into rooms.

1. **Single closed loop** — the path must form one continuous loop with no branching, no crossing, and no dead ends
2. **One visit per room** — the loop enters and exits each room exactly once (through 2 room-boundary crossings)
3. **Number clues** — if a room contains a number N, exactly N cells in that room must be on the loop
4. **Every room visited** — the loop must pass through every room (at least one cell on the loop per room)
5. **No adjacent grass across borders** — two cells on opposite sides of a room boundary cannot both be off the loop

6. **No consecutive same-room lines** — after drawing a line in a room, your next line-drawing action must start in a different room. The cell will flash red and revert if you try to start drawing in the same room consecutively
7. **Minimum loop coverage** — at least 50% of all grid cells must be on the loop. Checked when you click "Check Answer"
8. **At most 1 empty row** — at most one row in the grid may have zero cells on the loop. Checked when you click "Check Answer"

### puzz.link Controls

- Left-click and drag between adjacent cells to draw a line segment
- Right-click a cell or border to mark it as "not on the loop" (green ×)
- Starting a line in the same room as the last draw action is blocked (rule 6)
- Loop coverage and empty-row limits are validated on "Check Answer" (rules 7–8)

---

## Sudoku 2

All standard Sudoku rules (1–5) apply.

6. **Row alternation** — consecutive entries must be placed in different rows. Cell will flash red and revert if you try to enter in the same row as the last entry. **Deadlock bypass**: if every remaining empty cell is in the same row, same-row input is allowed
7. **Box alternation** — consecutive entries must be placed in different 3×3 boxes. Cell will flash red and revert if you try to enter in the same box as the last entry. **Deadlock bypass**: if every remaining empty cell is in the same box, same-box input is allowed
8. **Even-digit balance** — every row must contain exactly 4 even digits (2, 4, 6, 8). Checked when you click "Check Answer"

### puzz.link Controls

- Click a cell, then type a digit (1–9) to place it
- Arrow keys to navigate between cells
- Entering in the same row as last entry is blocked (rule 6), unless deadlocked
- Entering in the same 3×3 box as last entry is blocked (rule 7), unless deadlocked
- Even-digit balance is validated on "Check Answer" (rule 8)

## Heyawake 2

All standard Heyawake rules (1–5) apply with strict R1 (zero adjacent pairs allowed).

6. **Half-grid alternation** — you must alternate between shading cells in the left half (cols 0 to cols/2−1) and right half (cols/2 to cols−1) of the grid. After shading in one half, your next shade must be in the other half. Cell flashes red and reverts otherwise
7. **Column shade balance** — no single column can have more than ⌈rows/2⌉ shaded cells. Checked when you click "Check Answer"
8. **Shading density 10–50%** — the total number of shaded cells must be at least 10% and at most 50% of the grid area. Checked when you click "Check Answer"

### puzz.link Controls

- Left-click a cell to shade it (black)
- Right-click a cell to mark it white (dot)
- Shading in the same grid half consecutively is blocked (rule 6)
- Column shade limit and shading density are validated on "Check Answer" (rules 7–8)
- Adjacent shading: 0 pairs allowed (strict R1)

## Minesweeper 2

All standard Minesweeper rules (1–5) apply.

6. **Lucky streak** — every 3rd consecutive safe cell you reveal triggers a bonus: one additional random hidden safe cell is automatically revealed for free. The streak counter is displayed in orange at the top. Streak resets on game-over
7. **Row mine cap** — no single row can have more than ⌈2·cols/3⌉ mines (e.g., in a 9-column grid, max 6 per row). Checked when you click "Check Answer"
8. **No 2×2 mine block** — no 2×2 square of cells can all be mines. Checked when you click "Check Answer"

### puzz.link Controls

- Same as standard Minesweeper
- Watch the "Streak: N (bonus in M)" counter for your next auto-reveal
- Row mine cap and 2×2 block are validated on "Check Answer" (rules 7–8)

## Country Road 2

All standard Country Road rules (1–5) apply.

6. **Turn balance** — the total number of turns (corners) in the loop must not exceed twice the number of straight segments. Checked when you click "Check Answer"
7. **Maximum loop coverage** — at most 85% of all grid cells may be on the loop. Checked when you click "Check Answer"
8. **At most 1 empty row** — at most one row in the grid may have zero cells on the loop. Checked when you click "Check Answer"

### puzz.link Controls

- Same as standard Country Road
- Turn/straight ratio is validated on "Check Answer" (rule 6)
- Loop coverage cap and empty-row limit are validated on "Check Answer" (rules 7–8)
