"""Tests for dungeon-forge generators."""

from dungeon_forge import generate_bsp, generate_cellular, generate_drunkard, Tile


def test_bsp_deterministic():
    d1 = generate_bsp(seed=42)
    d2 = generate_bsp(seed=42)
    assert d1.tiles == d2.tiles


def test_bsp_has_rooms():
    d = generate_bsp(width=80, height=40, seed=42)
    assert len(d.rooms) > 0


def test_bsp_dimensions():
    d = generate_bsp(width=60, height=30, seed=42)
    assert d.width == 60
    assert d.height == 30
    assert len(d.tiles) == 30
    assert len(d.tiles[0]) == 60


def test_bsp_rooms_have_floors():
    d = generate_bsp(seed=42)
    for room in d.rooms:
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                assert d.get(x, y) == Tile.FLOOR.value


def test_cellular_deterministic():
    d1 = generate_cellular(seed=42)
    d2 = generate_cellular(seed=42)
    assert d1.tiles == d2.tiles


def test_cellular_has_open_space():
    d = generate_cellular(width=80, height=40, seed=42)
    floor_count = sum(
        1 for y in range(d.height) for x in range(d.width)
        if d.get(x, y) == Tile.FLOOR.value
    )
    assert floor_count > 0


def test_drunkard_deterministic():
    d1 = generate_drunkard(seed=42)
    d2 = generate_drunkard(seed=42)
    assert d1.tiles == d2.tiles


def test_drunkard_floor_percentage():
    d = generate_drunkard(width=80, height=40, floor_pct=0.3, seed=42)
    floor_count = sum(
        1 for y in range(d.height) for x in range(d.width)
        if d.get(x, y) == Tile.FLOOR.value
    )
    target = int(80 * 40 * 0.3)
    # Should be at least close to target
    assert floor_count >= target * 0.8


def test_to_dict():
    d = generate_bsp(seed=42)
    data = d.to_dict()
    assert data["width"] == d.width
    assert data["height"] == d.height
    assert data["seed"] == 42
    assert len(data["rooms"]) == len(d.rooms)


if __name__ == "__main__":
    test_bsp_deterministic()
    test_bsp_has_rooms()
    test_bsp_dimensions()
    test_bsp_rooms_have_floors()
    test_cellular_deterministic()
    test_cellular_has_open_space()
    test_drunkard_deterministic()
    test_drunkard_floor_percentage()
    test_to_dict()
    print("All tests passed!")
