import random

GRID_WIDTH = 20
GRID_HEIGHT = 20


def create_new_game(high_score = 0):
    snake = [{'x': 10, 'y': 10}, {'x': 9, 'y': 10}, {'x': 8, 'y': 10}]

    return {
        "snake": snake,
        "direction": "RIGHT",
        "food": spawn_food(snake),
        "score": 0,
        "status": "RUNNING",
        "next_direction": "RIGHT",
        "high_score": high_score
    }

def spawn_food(snake):
    cells = []
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            cells.append({"x": x, "y": y})

    free_cells = []
    for cell in cells:
        if cell not in snake:
            free_cells.append(cell)


    chosen = random.choice(free_cells)
    return chosen


# Calculates where the head WOULD be after one step.
# It does not change the game, it only returns the new cell.
def get_new_head(game):
    head = game['snake'][0]

    x = head["x"]
    y = head["y"]

    direction = game["direction"]

    if direction == "RIGHT":
        x = x + 1
    elif direction == "LEFT":
        x = x - 1
    elif direction == "UP":
        y = y - 1
    elif direction == "DOWN":
        y = y + 1
        
    return {"x": x, "y": y}

def hits_wall(cell):
    x = cell["x"]
    y = cell["y"]

    if x < 0 or x >= GRID_WIDTH:
        return True
    elif y < 0 or y >= GRID_HEIGHT:
        return True
    else:
        return False


def hits_self(snake, new_head, grow):
    if grow:
        body = snake
    else:
        body = snake[:-1]

    if new_head in body:
        return True
    else:
        return False

def is_eating_food(game, new_head):
    if new_head == game["food"]:
        return True
    else:
        return False

def move_snake(game, grow):
    snake = game["snake"]
    new_head = get_new_head(game)
    snake.insert(0, new_head)
    
    if not grow:
        snake.pop()

def step_game(game):
    if game["status"] != "RUNNING":
        return

    game["direction"] = game["next_direction"]

    new_head = get_new_head(game)

    if hits_wall(new_head):
        game["status"] = "GAME_OVER"
        return

    eating = is_eating_food(game, new_head)

    if hits_self(game["snake"], new_head, eating):
        game["status"] = "GAME_OVER"
        return

    move_snake(game, eating)

    if eating:
        game["score"] += 10

        if game["score"] > game["high_score"]:
            game["high_score"] = game["score"]

        game["food"] = spawn_food(game["snake"])


def change_direction(game, new_direction):
    opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
    
    forbidden = opposites[game["direction"]]

    if new_direction != forbidden:
        game["next_direction"] = new_direction

def toggle_pause(game):
    if game["status"] == "RUNNING":
        game["status"] = "PAUSED"
    elif game["status"] == "PAUSED":
        game["status"] = "RUNNING"


