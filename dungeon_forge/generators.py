import random
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Tile(Enum):
    WALL = 0
    FLOOR = 1
    CORRIDOR = 2
    DOOR = 3
    STAIRS_DOWN = 4
    STAIRS_UP = 5


@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2

    @property
    def area(self) -> int:
        return self.w * self.h

    def intersects(self, other: "Room", padding: int = 1) -> bool:
        return not (
            self.x + self.w + padding <= other.x
            or other.x + other.w + padding <= self.x
            or self.y + self.h + padding <= other.y
            or other.y + other.h + padding <= self.y
        )


@dataclass
class Dungeon:
    width: int
    height: int
    tiles: list[list[int]] = field(default_factory=list)
    rooms: list[Room] = field(default_factory=list)
    seed: Optional[int] = None

    def __post_init__(self):
        if not self.tiles:
            self.tiles = [[Tile.WALL.value] * self.width for _ in range(self.height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int) -> int:
        return self.tiles[y][x]

    def set(self, x: int, y: int, tile: int):
        self.tiles[y][x] = tile

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "rooms": [{"x": r.x, "y": r.y, "w": r.w, "h": r.h} for r in self.rooms],
            "tiles": self.tiles,
        }


def generate_bsp(
    width: int = 80,
    height: int = 40,
    min_room: int = 5,
    max_room: int = 15,
    min_leaf: int = 8,
    seed: Optional[int] = None,
) -> Dungeon:
    """Binary Space Partition dungeon generator."""
    rng = random.Random(seed)
    dungeon = Dungeon(width, height, seed=seed)

    @dataclass
    class Leaf:
        x: int
        y: int
        w: int
        h: int
        left: Optional["Leaf"] = None
        right: Optional["Leaf"] = None
        room: Optional[Room] = None

    def split(leaf: Leaf, depth: int = 0):
        if leaf.left or leaf.right:
            return
        split_h = rng.random() > 0.5
        if leaf.w > leaf.h and leaf.w / leaf.h >= 1.25:
            split_h = False
        elif leaf.h > leaf.w and leaf.h / leaf.w >= 1.25:
            split_h = True

        max_dim = leaf.h if split_h else leaf.w
        if max_dim < min_leaf * 2:
            return

        split_pos = rng.randint(min_leaf, max_dim - min_leaf)
        if split_h:
            leaf.left = Leaf(leaf.x, leaf.y, leaf.w, split_pos)
            leaf.right = Leaf(leaf.x, leaf.y + split_pos, leaf.w, leaf.h - split_pos)
        else:
            leaf.left = Leaf(leaf.x, leaf.y, split_pos, leaf.h)
            leaf.right = Leaf(leaf.x + split_pos, leaf.y, leaf.w - split_pos, leaf.h)

        split(leaf.left, depth + 1)
        split(leaf.right, depth + 1)

    def create_rooms(leaf: Leaf):
        if leaf.left or leaf.right:
            if leaf.left:
                create_rooms(leaf.left)
            if leaf.right:
                create_rooms(leaf.right)
            if leaf.left and leaf.right:
                _connect(dungeon, leaf.left.room, leaf.right.room)
        else:
            rw = rng.randint(min_room, min(leaf.w - 2, max_room))
            rh = rng.randint(min_room, min(leaf.h - 2, max_room))
            rx = leaf.x + rng.randint(1, leaf.w - rw - 1)
            ry = leaf.y + rng.randint(1, leaf.h - rh - 1)
            room = Room(rx, ry, rw, rh)
            leaf.room = room
            dungeon.rooms.append(room)
            _carve_room(dungeon, room)

    def _carve_room(dungeon: Dungeon, room: Room):
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                if dungeon.in_bounds(x, y):
                    dungeon.set(x, y, Tile.FLOOR.value)

    def _connect(dungeon: Dungeon, r1: Optional[Room], r2: Optional[Room]):
        if not r1 or not r2:
            return
        x1, y1 = r1.cx, r1.cy
        x2, y2 = r2.cx, r2.cy
        if rng.random() > 0.5:
            _carve_h(dungeon, x1, x2, y1)
            _carve_v(dungeon, y1, y2, x2)
        else:
            _carve_v(dungeon, y1, y2, x1)
            _carve_h(dungeon, x1, x2, y2)

    def _carve_h(dungeon, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if dungeon.in_bounds(x, y) and dungeon.get(x, y) == Tile.WALL.value:
                dungeon.set(x, y, Tile.CORRIDOR.value)

    def _carve_v(dungeon, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if dungeon.in_bounds(x, y) and dungeon.get(x, y) == Tile.WALL.value:
                dungeon.set(x, y, Tile.CORRIDOR.value)

    root = Leaf(0, 0, width, height)
    split(root)
    create_rooms(root)

    if not dungeon.rooms:
        rw = min(width - 4, max_room)
        rh = min(height - 4, max_room)
        room = Room(2, 2, rw, rh)
        dungeon.rooms.append(room)
        _carve_room(dungeon, room)

    return dungeon


def generate_cellular(
    width: int = 80,
    height: int = 40,
    fill: float = 0.45,
    iterations: int = 5,
    birth: int = 4,
    death: int = 4,
    seed: Optional[int] = None,
) -> Dungeon:
    """Cellular automata cave generator."""
    rng = random.Random(seed)
    dungeon = Dungeon(width, height, seed=seed)

    for y in range(height):
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                dungeon.set(x, y, Tile.WALL.value)
            elif rng.random() < fill:
                dungeon.set(x, y, Tile.WALL.value)
            else:
                dungeon.set(x, y, Tile.FLOOR.value)

    for _ in range(iterations):
        new_tiles = [row[:] for row in dungeon.tiles]
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                walls = 0
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dy == 0 and dx == 0:
                            continue
                        if dungeon.get(x + dx, y + dy) == Tile.WALL.value:
                            walls += 1
                if dungeon.get(x, y) == Tile.WALL.value:
                    new_tiles[y][x] = Tile.WALL.value if walls >= death else Tile.FLOOR.value
                else:
                    new_tiles[y][x] = Tile.WALL.value if walls > birth else Tile.FLOOR.value
        dungeon.tiles = new_tiles

    # Find connected regions, keep largest
    visited = [[False] * width for _ in range(height)]
    largest_region = set()

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if not visited[y][x] and dungeon.get(x, y) == Tile.FLOOR.value:
                region = set()
                stack = [(x, y)]
                while stack:
                    cx, cy = stack.pop()
                    if not (0 <= cx < width and 0 <= cy < height):
                        continue
                    if visited[cy][cx] or dungeon.get(cx, cy) != Tile.FLOOR.value:
                        continue
                    visited[cy][cx] = True
                    region.add((cx, cy))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        stack.append((cx + dx, cy + dy))
                if len(region) > len(largest_region):
                    largest_region = region

    for y in range(height):
        for x in range(width):
            if dungeon.get(x, y) == Tile.FLOOR.value and (x, y) not in largest_region:
                dungeon.set(x, y, Tile.WALL.value)

    return dungeon


def generate_drunkard(
    width: int = 80,
    height: int = 40,
    floor_pct: float = 0.45,
    max_steps: int = 10000,
    seed: Optional[int] = None,
) -> Dungeon:
    """Drunkard's walk cave generator."""
    rng = random.Random(seed)
    dungeon = Dungeon(width, height, seed=seed)

    target = int(width * height * floor_pct)
    floor_count = 0
    x, y = width // 2, height // 2

    for _ in range(max_steps):
        if floor_count >= target:
            break
        if dungeon.get(x, y) == Tile.WALL.value:
            dungeon.set(x, y, Tile.FLOOR.value)
            floor_count += 1
        direction = rng.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        x = max(1, min(width - 2, x + direction[0]))
        y = max(1, min(height - 2, y + direction[1]))

    return dungeon


GENERATORS = {
    "bsp": generate_bsp,
    "cellular": generate_cellular,
    "drunkard": generate_drunkard,
}
