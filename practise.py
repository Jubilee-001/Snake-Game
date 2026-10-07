import random

GRID_WIDTH = 20
GRID_HEIGHT = 20


def create_new_game():
    return {
        "snake": [{'x': 10, 'y': 10}, {'x': 9, 'y': 10}, {'x': 8, 'y': 10}],
        "direction": "RIGHT",
        "food": {},
        "score": 0,
        "status": "RUNNING"
    }

# print(create_new_game())

def spawn_food():
    cells = []
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            cells.append({"x": x, "y": y})
    print(len(cells))

spawn_food()