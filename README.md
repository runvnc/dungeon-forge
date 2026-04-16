# dungeon-forge ⚔️

Procedural roguelike dungeon generation for Python. Three algorithms, multiple export formats, seed-reproducible.

```
████████████████████████████████████████████████████████████████████████████████████
██···············████████·····██··············███···············██████████████████████
██···············████████·····██··············███···············██████████████████████
██···············██    ██·····██··············███···············██  ██████████████████
██···············██    ██·····██··············███···············██  ██████████████████
██······································································██████████████
██······································································██████████████
████·····██████████████████·····████████·····████████████████████··············███████
████·····██████████████████·····████████·····████████████████████··············███████
```

## Features

- **3 algorithms:** BSP (rooms & corridors), Cellular Automata (caves), Drunkard's Walk (organic caves)
- **3 export formats:** ASCII (with terminal colors), JSON, PNG
- **Seed-reproducible:** Same seed = same dungeon, every time
- **CLI + library:** Use from the command line or import in your Python projects
- **Zero dependencies:** Pure Python for core functionality (Pillow optional for PNG)

## Install

```bash
pip install dungeon-forge          # core only
pip install dungeon-forge[png]     # with PNG export
```

## CLI Usage

```bash
# Generate a BSP dungeon (rooms & corridors)
dungeon-forge bsp

# Generate a cave with cellular automata
dungeon-forge cellular -W 100 -H 50

# Drunkard's walk, reproducible seed
dungeon-forge drunkard --seed 42

# Export as JSON
dungeon-forge bsp --format json

# Export as PNG
dungeon-forge cellular --format png -o cave.png

# No color for piping
dungeon-forge bsp --no-color | less
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-W, --width` | 80 | Map width |
| `-H, --height` | 40 | Map height |
| `-s, --seed` | random | Random seed |
| `-f, --format` | ascii | Output: `ascii`, `json`, `png` |
| `-o, --output` | stdout | Output file path |
| `--no-color` | false | Disable ANSI colors |
| `--min-room` | 5 | BSP: min room size |
| `--max-room` | 15 | BSP: max room size |
| `--fill` | 0.45 | Cellular: initial wall ratio |
| `--iterations` | 5 | Cellular: smoothing passes |
| `--floor-pct` | 0.45 | Drunkard: target floor % |

## Library Usage

```python
from dungeon_forge import generate_bsp, generate_cellular, generate_drunkard, to_ascii, to_json

# Generate a dungeon
dungeon = generate_bsp(width=80, height=40, seed=42)

# Print as ASCII
print(to_ascii(dungeon))

# Export as JSON
data = to_json(dungeon)

# Access rooms
for room in dungeon.rooms:
    print(f"Room at ({room.x}, {room.y}), size {room.w}x{room.h}")

# Generate a cave
cave = generate_cellular(width=100, height=50, fill=0.45, seed=123)
print(to_ascii(cave, color=False))

# Drunkard's walk
tunnel = generate_drunkard(width=60, height=30, floor_pct=0.5, seed=99)
```

## Algorithms

### BSP (Binary Space Partition)
Recursively splits the map into halves, places rooms in each leaf, connects them with corridors. Produces structured, classic roguelike layouts with distinct rooms.

### Cellular Automata
Randomly fills the map, then smooths it over multiple iterations using neighbor-count rules. Produces organic cave systems. Disconnected regions are automatically removed.

### Drunkard's Walk
A random walker carves floor tiles until a target percentage is reached. Produces open, organic layouts with natural-feeling passages.

## License

MIT
