import json
import sys
from .generators import Dungeon, Tile


# Terminal color codes
COLORS = {
    Tile.WALL.value: "\033[90m",      # dark gray
    Tile.FLOOR.value: "\033[97m",     # white
    Tile.CORRIDOR.value: "\033[33m",  # yellow
    Tile.DOOR.value: "\033[93m",      # bright yellow
    Tile.STAIRS_DOWN.value: "\033[91m",  # red
    Tile.STAIRS_UP.value: "\033[92m",    # green
}
RESET = "\033[0m"

GLYPHS = {
    Tile.WALL.value: "█",
    Tile.FLOOR.value: "·",
    Tile.CORRIDOR.value: "·",
    Tile.DOOR.value: "+",
    Tile.STAIRS_DOWN.value: ">",
    Tile.STAIRS_UP.value: "<",
}


def to_ascii(dungeon: Dungeon, color: bool = True) -> str:
    """Render dungeon as ASCII art."""
    lines = []
    for row in dungeon.tiles:
        line = ""
        for tile in row:
            glyph = GLYPHS.get(tile, "?")
            if color and tile in COLORS:
                line += COLORS[tile] + glyph + RESET
            else:
                line += glyph
        lines.append(line)
    return "\n".join(lines)


def to_json(dungeon: Dungeon, pretty: bool = True) -> str:
    """Export dungeon as JSON."""
    data = dungeon.to_dict()
    if pretty:
        return json.dumps(data, indent=2)
    return json.dumps(data)


def to_png(dungeon: Dungeon, cell_size: int = 8, path: str = "dungeon.png"):
    """Export dungeon as PNG image. Requires Pillow."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Pillow required for PNG export: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    tile_colors = {
        Tile.WALL.value: (30, 30, 30),
        Tile.FLOOR.value: (200, 190, 170),
        Tile.CORRIDOR.value: (180, 170, 140),
        Tile.DOOR.value: (160, 120, 60),
        Tile.STAIRS_DOWN.value: (200, 50, 50),
        Tile.STAIRS_UP.value: (50, 200, 50),
    }

    img = Image.new("RGB", (dungeon.width * cell_size, dungeon.height * cell_size), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    for y in range(dungeon.height):
        for x in range(dungeon.width):
            tile = dungeon.get(x, y)
            color = tile_colors.get(tile, (0, 0, 0))
            x0, y0 = x * cell_size, y * cell_size
            draw.rectangle(
                [x0, y0, x0 + cell_size - 1, y0 + cell_size - 1],
                fill=color,
            )

    img.save(path)
    return path
