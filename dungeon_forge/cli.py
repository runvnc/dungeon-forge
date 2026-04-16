#!/usr/bin/env python3
"""dungeon-forge CLI — Generate roguelike dungeon maps from the terminal."""

import argparse
import json
import random
import sys

from .generators import GENERATORS, Tile
from .exporters import to_ascii, to_json, to_png


def main():
    parser = argparse.ArgumentParser(
        prog="dungeon-forge",
        description="Generate roguelike dungeon maps. Three algorithms: bsp (rooms & corridors), cellular (caves), drunkard (organic caves).",
    )
    parser.add_argument(
        "algorithm",
        choices=["bsp", "cellular", "drunkard"],
        help="Generation algorithm",
    )
    parser.add_argument("-W", "--width", type=int, default=80, help="Map width (default: 80)")
    parser.add_argument("-H", "--height", type=int, default=40, help="Map height (default: 40)")
    parser.add_argument("-s", "--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument(
        "-f", "--format",
        choices=["ascii", "json", "png"],
        default="ascii",
        help="Output format (default: ascii)",
    )
    parser.add_argument("-o", "--output", type=str, default=None, help="Output file (default: stdout)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors in ASCII output")
    parser.add_argument("--cell-size", type=int, default=8, help="Pixel size per cell for PNG (default: 8)")

    # Algorithm-specific options
    parser.add_argument("--min-room", type=int, default=5, help="BSP: minimum room size")
    parser.add_argument("--max-room", type=int, default=15, help="BSP: maximum room size")
    parser.add_argument("--fill", type=float, default=0.45, help="Cellular: initial wall fill ratio")
    parser.add_argument("--iterations", type=int, default=5, help="Cellular: smoothing iterations")
    parser.add_argument("--floor-pct", type=float, default=0.45, help="Drunkard: target floor percentage")

    args = parser.parse_args()

    if args.seed is None:
        args.seed = random.randint(0, 2**31 - 1)

    # Generate
    gen_fn = GENERATORS[args.algorithm]
    kwargs = {"width": args.width, "height": args.height, "seed": args.seed}

    if args.algorithm == "bsp":
        kwargs.update({"min_room": args.min_room, "max_room": args.max_room})
    elif args.algorithm == "cellular":
        kwargs.update({"fill": args.fill, "iterations": args.iterations})
    elif args.algorithm == "drunkard":
        kwargs.update({"floor_pct": args.floor_pct})

    dungeon = gen_fn(**kwargs)

    # Stats
    floor_tiles = sum(
        1 for y in range(dungeon.height) for x in range(dungeon.width)
        if dungeon.get(x, y) in (Tile.FLOOR.value, Tile.CORRIDOR.value)
    )
    total = dungeon.width * dungeon.height

    print(f"# seed: {dungeon.seed} | {args.algorithm} | {dungeon.width}x{dungeon.height}", file=sys.stderr)
    print(f"# rooms: {len(dungeon.rooms)} | floor: {floor_tiles}/{total} ({100*floor_tiles/total:.1f}%)", file=sys.stderr)

    # Export
    if args.format == "ascii":
        output = to_ascii(dungeon, color=not args.no_color)
    elif args.format == "json":
        output = to_json(dungeon)
    elif args.format == "png":
        out_path = args.output or "dungeon.png"
        path = to_png(dungeon, cell_size=args.cell_size, path=out_path)
        print(f"# saved: {path}", file=sys.stderr)
        return

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"# saved: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
