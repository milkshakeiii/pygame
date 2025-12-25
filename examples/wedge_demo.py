#!/usr/bin/env python3
"""
Demo of Legacy Computing wedge characters (U+1FB3C-U+1FB67).

Shows the 44 wedge characters and demonstrates using them to draw smooth shapes.

================================================================================
WEDGE CHARACTER REFERENCE FOR LLMs
================================================================================

These 44 characters (22 base + 22 inverted) allow drawing smooth diagonal lines
and rounded shapes in terminal/text UIs. Each is defined by a diagonal line
that divides the cell, with one side filled.

STRUCTURE:
- Base wedges (indices 0-21, U+1FB3C-U+1FB51): Fill BELOW the diagonal line
- Inverted wedges (indices 22-43, U+1FB52-U+1FB67): Fill ABOVE the same line
  Index N+22 is the inverse of index N (together they make a full block).

HOW WEDGES ARE DEFINED:
Each wedge has a diagonal line from point_a to point_b. The difference between
base and inverted is simply which side of that line is filled.

Edge points used in definitions:
  - Corners: TL, TR, BL, BR
  - Edge midpoints: top_mid, bot_mid
  - Vertical 1/3 points: left_1_3, left_2_3, right_1_3, right_2_3
    (1_3 = 1/3 up from bottom, 2_3 = 2/3 up from bottom)

CONNECTION RULES:
Two wedges connect smoothly when their shared edge matches. There are two ways:

1. FULL EDGE CONNECTION: A wedge with a fully-filled edge connects to any
   wedge with a fully-filled opposite edge (including full block).

2. POINT MATCHING: Wedges connect when their diagonals meet at corresponding
   points AND the fill is on the same side of that point. Specifically:
   - pa<->pa: Both diagonals START at corresponding points
   - pb<->pb: Both diagonals END at corresponding points
   - pa<->pb: One starts where the other ends at corresponding points
   The fill must be on the same side (e.g., both LEFT of the mid-point).

CONNECTIVITY MAP:
Format: [index] char  L:left R:right T:top B:bottom connections
        █ = has full edge (connects to full block and all full opposite edges)

[ 0] 🬼  L:🭇🭈🭎🭏🭑  B:🭌🭎🭐🭗🭙🭛
[ 1] 🬽  L:🭇🭈🭎🭏🭑  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[ 2] 🬾  L:🭆🭉🭊🭌🭍  B:🭌🭎🭐🭗🭙🭛
[ 3] 🬿  L:🭆🭉🭊🭌🭍  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[ 4] 🭀  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  B:🭌🭎🭐🭗🭙🭛
[ 5] 🭁  L:🭆🭉🭊🭌🭍  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:🭇🭉🭋🭒🭔🭖  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[ 6] 🭂  L:🭆🭉🭊🭌🭍  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[ 7] 🭃  L:🭇🭈🭎🭏🭑  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:🭇🭉🭋🭒🭔🭖  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[ 8] 🭄  L:🭇🭈🭎🭏🭑  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[ 9] 🭅  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:🭇🭉🭋🭒🭔🭖  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[10] 🭆  L:🭇🭈🭎🭏🭑  R:🬾🬿🭁🭂🭑  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[11] 🭇  R:🬼🬽🭃🭄🭆  B:🭁🭃🭅🭢🭤🭦
[12] 🭈  R:🬼🬽🭃🭄🭆  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[13] 🭉  R:🬾🬿🭁🭂🭑  B:🭁🭃🭅🭢🭤🭦
[14] 🭊  R:🬾🬿🭁🭂🭑  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[15] 🭋  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  B:🭁🭃🭅🭢🭤🭦
[16] 🭌  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🬾🬿🭁🭂🭑  T:🬼🬾🭀🭝🭟🭡  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[17] 🭍  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🬾🬿🭁🭂🭑  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[18] 🭎  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🬼🬽🭃🭄🭆  T:🬼🬾🭀🭝🭟🭡  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[19] 🭏  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🬼🬽🭃🭄🭆  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[20] 🭐  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  T:🬼🬾🭀🭝🭟🭡  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[21] 🭑  L:🭆🭉🭊🭌🭍  R:🬼🬽🭃🭄🭆  B:█🭒🭓🭔🭕🭖🭘🭚🭜🭝🭞🭟🭠🭡🭣🭥🭧
[22] 🭒  L:🭝🭞🭤🭥🭧  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑  B:🭁🭃🭅🭢🭤🭦
[23] 🭓  L:🭝🭞🭤🭥🭧  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[24] 🭔  L:🭜🭟🭠🭢🭣  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑  B:🭁🭃🭅🭢🭤🭦
[25] 🭕  L:🭜🭟🭠🭢🭣  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[26] 🭖  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑  B:🭁🭃🭅🭢🭤🭦
[27] 🭗  L:🭜🭟🭠🭢🭣  T:🬼🬾🭀🭝🭟🭡
[28] 🭘  L:🭜🭟🭠🭢🭣  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[29] 🭙  L:🭝🭞🭤🭥🭧  T:🬼🬾🭀🭝🭟🭡
[30] 🭚  L:🭝🭞🭤🭥🭧  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[31] 🭛  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  T:🬼🬾🭀🭝🭟🭡
[32] 🭜  L:🭝🭞🭤🭥🭧  R:🭔🭕🭗🭘🭧  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[33] 🭝  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🭒🭓🭙🭚🭜  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑  B:🭌🭎🭐🭗🭙🭛
[34] 🭞  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🭒🭓🭙🭚🭜  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[35] 🭟  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🭔🭕🭗🭘🭧  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑  B:🭌🭎🭐🭗🭙🭛
[36] 🭠  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  R:🭔🭕🭗🭘🭧  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[37] 🭡  L:█🭁🭂🭃🭄🭅🭋🭒🭓🭔🭕🭖🭦  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑  B:🭌🭎🭐🭗🭙🭛
[38] 🭢  R:🭔🭕🭗🭘🭧  T:🭇🭉🭋🭒🭔🭖
[39] 🭣  R:🭔🭕🭗🭘🭧  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[40] 🭤  R:🭒🭓🭙🭚🭜  T:🭇🭉🭋🭒🭔🭖
[41] 🭥  R:🭒🭓🭙🭚🭜  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑
[42] 🭦  R:█🭀🭌🭍🭎🭏🭐🭛🭝🭞🭟🭠🭡  T:🭇🭉🭋🭒🭔🭖
[43] 🭧  L:🭜🭟🭠🭢🭣  R:🭒🭓🭙🭚🭜  T:█🬽🬿🭁🭂🭃🭄🭅🭆🭈🭊🭌🭍🭎🭏🭐🭑

COMMON PATTERNS:

Rounded rectangle corners (these have full right+bottom or left+top edges):
  TL: 🭁 (5)   TR: 🭌 (16)   BL: 🭒 (22)   BR: 🭝 (33)

Diagonal line going DOWN-RIGHT (alternating 2-cell pattern):
  Even rows: 🭦🭐 (42, 20)
  Odd rows:  🭖🭀 (26, 4) - shifted right by 1

Full block: █ (U+2588) - connects to any wedge with a full edge on that side

================================================================================
"""

import argparse
import pygame
import pyunicodegame

FONTS = ["5x8", "6x13", "9x18", "10x20"]


def main():
    parser = argparse.ArgumentParser(description="Wedge characters demo")
    parser.add_argument("--font", choices=FONTS, default="10x20", help="Font size to use")
    args = parser.parse_args()

    root = pyunicodegame.init("Wedge Characters Demo", width=80, height=40, bg=(10, 10, 30, 255), font_name=args.font)

    def render():
        # Title
        root.put_string(2, 1, "Legacy Computing Wedge Characters (U+1FB3C-U+1FB67)", (200, 200, 255))

        # Show all 44 wedge characters in a grid
        root.put_string(2, 3, "Base wedges (22):", (150, 150, 150))
        for i in range(22):
            char = chr(0x1FB3C + i)
            x = 2 + (i % 11) * 3
            y = 4 + (i // 11) * 2
            root.put(x, y, char, (255, 255, 255))
            # Show codepoint below
            root.put_string(x, y + 1, f"{i:02d}", (80, 80, 80))

        root.put_string(2, 8, "Inverted wedges (22):", (150, 150, 150))
        for i in range(22):
            char = chr(0x1FB3C + 22 + i)
            x = 2 + (i % 11) * 3
            y = 9 + (i // 11) * 2
            root.put(x, y, char, (255, 255, 255))

        # Demo: Rounded rectangle using wedges
        root.put_string(2, 14, "Rounded rectangle example:", (150, 150, 150))

        # Small rounded rect
        rx, ry = 4, 16
        color = (100, 200, 100)
        # Corners: use large fills WITH cutouts (not small triangles)
        # TL corner: large fill with TL cutout = index 5 (left_2_3->top_mid, fills below)
        root.put(rx, ry, chr(0x1FB3C + 5), color)  # TL corner
        # TR corner: large fill with TR cutout = index 16 (top_mid->right_2_3, fills below)
        root.put(rx + 8, ry, chr(0x1FB3C + 16), color)  # TR corner
        # BL corner: large fill with BL cutout = inverted of small BL = index 22
        root.put(rx, ry + 3, chr(0x1FB3C + 22), color)  # BL corner
        # BR corner: large fill with BR cutout = inverted of small BR = index 33
        root.put(rx + 8, ry + 3, chr(0x1FB3C + 33), color)  # BR corner
        # Edges
        for x in range(rx + 1, rx + 8):
            root.put(x, ry, chr(0x2588), color)  # Top edge (full block)
            root.put(x, ry + 3, chr(0x2588), color)  # Bottom edge
        for y in range(ry + 1, ry + 3):
            root.put(rx, y, chr(0x2588), color)  # Left edge
            root.put(rx + 8, y, chr(0x2588), color)  # Right edge
        # Fill
        for y in range(ry + 1, ry + 3):
            for x in range(rx + 1, rx + 8):
                root.put(x, y, chr(0x2588), color)

        # Demo: Diagonal line (going down-right)
        root.put_string(30, 14, "Diagonal line:", (150, 150, 150))

        # Alternating wedge pairs for smooth diagonal:
        # Even rows: 🭦🭐 (indices 42, 20)
        # Odd rows: 🭖🭀 (indices 26, 4), indented by 1
        dx, dy = 32, 16
        color2 = (200, 150, 100)
        for i in range(6):
            x_off = i // 2 + (i % 2)
            if i % 2 == 0:
                root.put(dx + x_off, dy + i, chr(0x1FB3C + 42), color2)  # 🭦
                root.put(dx + x_off + 1, dy + i, chr(0x1FB3C + 20), color2)  # 🭐
            else:
                root.put(dx + x_off, dy + i, chr(0x1FB3C + 26), color2)  # 🭖
                root.put(dx + x_off + 1, dy + i, chr(0x1FB3C + 4), color2)  # 🭀

        # Demo: Show some paired wedges that combine to full block
        root.put_string(2, 22, "Wedge pairs (base + inverted = full block):", (150, 150, 150))
        # Each base wedge + its inverted counterpart = full block
        pairs = [(0, 22), (1, 23), (5, 27), (11, 33), (16, 38)]
        for idx, (a, b) in enumerate(pairs):
            x = 4 + idx * 8
            root.put(x, 24, chr(0x1FB3C + a), (255, 200, 100))
            root.put(x + 1, 24, "+", (100, 100, 100))
            root.put(x + 2, 24, chr(0x1FB3C + b), (255, 200, 100))
            root.put(x + 3, 24, "=", (100, 100, 100))
            root.put(x + 4, 24, chr(0x2588), (255, 200, 100))

        # Demo: Circle with gradual slopes
        # Structure (7 wide x 4 tall):
        #     🭊🭂█🭍🬿       <- top edge (base wedges)
        #    🭋█████🭀      <- middle + side bulge
        #    🭦█████🭛      <- middle + side bulge
        #     🭥🭓█🭞🭚       <- bottom edge (inverted wedges)
        #
        # Key principles:
        # 1. Fill levels create curves using 1/3 and 2/3 edge points
        #    Top/bottom rows: 0 -> 2/3 -> 1 -> 2/3 -> 0 (curves toward center)
        # 2. Base wedges for top edge (empty space at top of cell)
        #    Inverted wedges for bottom edge (empty space at bottom)
        # 3. Horizontal symmetry - mirror wedges across center
        # 4. Side bulges: base wedge on top, its inverse below (same diagonal)
        #    Left: 🭋(15)/🭦(42) fill RIGHT side; Right: 🭀(4)/🭛(31) fill LEFT side
        root.put_string(2, 26, "Circle:", (150, 150, 150))
        cx, cy = 4, 28
        color4 = (200, 100, 200)
        # Top row: 0→⅔→1→⅔→0 using 🭊🭂█🭍🬿 (indices 14,6,full,17,3)
        root.put(cx, cy, chr(0x1FB3C + 14), color4)      # 🭊
        root.put(cx + 1, cy, chr(0x1FB3C + 6), color4)   # 🭂
        root.put(cx + 2, cy, chr(0x2588), color4)        # █
        root.put(cx + 3, cy, chr(0x1FB3C + 17), color4)  # 🭍
        root.put(cx + 4, cy, chr(0x1FB3C + 3), color4)   # 🬿
        # Middle rows: full blocks with side wedges for roundness
        for row in range(1, 3):
            for col in range(5):
                root.put(cx + col, cy + row, chr(0x2588), color4)
        # Left side: 🭋(15) top, 🭦(42) bottom
        root.put(cx - 1, cy + 1, chr(0x1FB3C + 15), color4)  # 🭋
        root.put(cx - 1, cy + 2, chr(0x1FB3C + 42), color4)  # 🭦
        # Right side: 🭀(4) top, 🭛(31) bottom
        root.put(cx + 5, cy + 1, chr(0x1FB3C + 4), color4)   # 🭀
        root.put(cx + 5, cy + 2, chr(0x1FB3C + 31), color4)  # 🭛
        # Bottom row: 🭥🭓█🭞🭚 (indices 41,23,full,34,30)
        root.put(cx, cy + 3, chr(0x1FB3C + 41), color4)      # 🭥
        root.put(cx + 1, cy + 3, chr(0x1FB3C + 23), color4)  # 🭓
        root.put(cx + 2, cy + 3, chr(0x2588), color4)        # █
        root.put(cx + 3, cy + 3, chr(0x1FB3C + 34), color4)  # 🭞
        root.put(cx + 4, cy + 3, chr(0x1FB3C + 30), color4)  # 🭚

        # Demo: Triangle pointing right
        # Pattern uses alternating diagonal pairs:
        #   🭋(15)/🭀(4) for top of diagonal edges
        #   🭅(9)/🭐(20) for bottom of diagonal edges
        # Structure (grows wider going down):
        #     🭋🭀
        #     🭅🭐
        #    🭋██🭀
        #    🭅██🭐
        #   🭋████🭀
        root.put_string(12, 26, "Triangle:", (150, 150, 150))
        tx, ty = 14, 28
        color5 = (100, 200, 200)
        # Row 0-1: tip (2 wide)
        root.put(tx + 2, ty, chr(0x1FB3C + 15), color5)      # 🭋
        root.put(tx + 3, ty, chr(0x1FB3C + 4), color5)       # 🭀
        root.put(tx + 2, ty + 1, chr(0x1FB3C + 9), color5)   # 🭅
        root.put(tx + 3, ty + 1, chr(0x1FB3C + 20), color5)  # 🭐
        # Row 2-3: middle (4 wide)
        root.put(tx + 1, ty + 2, chr(0x1FB3C + 15), color5)  # 🭋
        root.put(tx + 2, ty + 2, chr(0x2588), color5)        # █
        root.put(tx + 3, ty + 2, chr(0x2588), color5)        # █
        root.put(tx + 4, ty + 2, chr(0x1FB3C + 4), color5)   # 🭀
        root.put(tx + 1, ty + 3, chr(0x1FB3C + 9), color5)   # 🭅
        root.put(tx + 2, ty + 3, chr(0x2588), color5)        # █
        root.put(tx + 3, ty + 3, chr(0x2588), color5)        # █
        root.put(tx + 4, ty + 3, chr(0x1FB3C + 20), color5)  # 🭐
        # Row 4: base (6 wide)
        root.put(tx, ty + 4, chr(0x1FB3C + 15), color5)      # 🭋
        for i in range(4):
            root.put(tx + 1 + i, ty + 4, chr(0x2588), color5)  # ████
        root.put(tx + 5, ty + 4, chr(0x1FB3C + 4), color5)   # 🭀

        # Demo: Arrow pointing right
        # Uses half blocks for thin shaft, wedges for arrowhead:
        #   ▄▄🭏🬼   <- lower half (U+2584) + wedges 19, 0
        #   ▀▀🭠🭗   <- upper half (U+2580) + wedges 36, 27
        root.put_string(24, 26, "Arrow:", (150, 150, 150))
        ax, ay = 26, 28
        color6 = (255, 200, 100)
        # Top row: lower half shaft + arrowhead
        root.put(ax, ay, chr(0x2584), color6)            # ▄
        root.put(ax + 1, ay, chr(0x2584), color6)        # ▄
        root.put(ax + 2, ay, chr(0x1FB3C + 19), color6)  # 🭏
        root.put(ax + 3, ay, chr(0x1FB3C + 0), color6)   # 🬼
        # Bottom row: upper half shaft + arrowhead
        root.put(ax, ay + 1, chr(0x2580), color6)        # ▀
        root.put(ax + 1, ay + 1, chr(0x2580), color6)    # ▀
        root.put(ax + 2, ay + 1, chr(0x1FB3C + 36), color6)  # 🭠
        root.put(ax + 3, ay + 1, chr(0x1FB3C + 27), color6)  # 🭗

        # Demo: Speech bubble with tail
        # Structure:
        #   🭁███████🭌   <- corners: 🭁(5), 🭌(16)
        #   █ Hello! █   <- content
        #   🭒███████🭝   <- corners: 🭒(22), 🭝(33)
        #    🭡           <- tail: 🭡(37)
        #    🭗           <- tail: 🭗(27)
        root.put_string(36, 26, "Speech bubble:", (150, 150, 150))
        sx, sy = 38, 28
        color7 = (200, 200, 200)
        # Top row
        root.put(sx, sy, chr(0x1FB3C + 5), color7)  # 🭁
        for i in range(1, 8):
            root.put(sx + i, sy, chr(0x2588), color7)
        root.put(sx + 8, sy, chr(0x1FB3C + 16), color7)  # 🭌
        # Middle row with text
        root.put(sx, sy + 1, chr(0x2588), color7)
        root.put_string(sx + 2, sy + 1, "Hello!", color7)
        root.put(sx + 8, sy + 1, chr(0x2588), color7)
        # Bottom row
        root.put(sx, sy + 2, chr(0x1FB3C + 22), color7)  # 🭒
        for i in range(1, 8):
            root.put(sx + i, sy + 2, chr(0x2588), color7)
        root.put(sx + 8, sy + 2, chr(0x1FB3C + 33), color7)  # 🭝
        # Tail
        root.put(sx + 1, sy + 3, chr(0x1FB3C + 29), color7)  # 🭙

        root.put_string(2, 38, "Press Q to quit", (80, 80, 80))

    def on_key(key):
        if key == pygame.K_q:
            pyunicodegame.quit()

    pyunicodegame.run(render=render, on_key=on_key)


if __name__ == "__main__":
    main()
