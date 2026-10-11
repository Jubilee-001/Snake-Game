# versus.py - two-player timed mode: best of 3 rounds, golden bonus apple, optional AI.
# Rules: snakes pass through each other, walls wrap around, hitting yourself loses the round,
# otherwise the higher score when the round's time runs out wins it.
import random

from practise import spawn_food, get_new_head, hits_self, GRID_WIDTH, GRID_HEIGHT, POINTS_PER_APPLE

VERSUS_DELAY = 200                         # ms per move (constant, no speed-up in versus)
TICKS_PER_SECOND = 1000 // VERSUS_DELAY    # moves per second, used to turn ticks into seconds
ROUND_SECONDS = 60
COUNTDOWN_SECONDS = 3
MAX_ROUNDS = 3
WINS_NEEDED = 2                            # first to 2 round wins takes the match

BONUS_EVERY_SECONDS = 12                   # quiet time before a golden apple appears
BONUS_LIFETIME_SECONDS = 6                 # how long it stays
BONUS_POINTS = 30

# which way the body trails behind the head for each starting direction
BEHIND = {"RIGHT": (-1, 0), "LEFT": (1, 0), "UP": (0, 1), "DOWN": (0, -1)}


def create_player(start_x, start_y, direction):
    dx, dy = BEHIND[direction]
    snake = []
    for i in range(3):
        snake.append({"x": (start_x + dx * i) % GRID_WIDTH, "y": (start_y + dy * i) % GRID_HEIGHT})
    return {"snake": snake, "direction": direction, "next_direction": direction, "score": 0}


# sets up a fresh round. Series information (round number, wins) is left alone.
def reset_round(game):
    p1 = create_player(5, 5, "RIGHT")
    p2 = create_player(14, 14, "LEFT")
    game["players"] = [p1, p2]
    game["food"] = spawn_food(p1["snake"] + p2["snake"])
    game["bonus"] = None                   # the golden apple: None or {"x", "y", "ticks_left"}
    game["bonus_timer"] = 0
    game["status"] = "COUNTDOWN"
    game["countdown_ticks"] = COUNTDOWN_SECONDS * TICKS_PER_SECOND
    game["ticks_left"] = ROUND_SECONDS * TICKS_PER_SECOND
    game["winner"] = None                  # this round: "P1", "P2" or "TIE"
    game["reason"] = None                  # "TIME", "SELF_COLLISION" or "BOARD_FULL"
    game["crashed"] = []                   # indexes of players who hit themselves
    refresh_clock(game)


def create_versus_game(ai_level=None):
    game = {
        "mode": "versus",
        "delay": VERSUS_DELAY,
        "ai_level": ai_level,              # None = two humans, or "easy" / "medium" / "hard"
        "round": 1,
        "max_rounds": MAX_ROUNDS,
        "wins_needed": WINS_NEEDED,
        "round_wins": [0, 0],
        "total_scores": [0, 0],
        "match_winner": None,
    }
    reset_round(game)
    return game


def start_next_round(game):
    if game["status"] == "ROUND_OVER":
        game["round"] += 1
        reset_round(game)


# turns a cell that left the board into the cell on the opposite side
def wrap_cell(cell):
    return {"x": cell["x"] % GRID_WIDTH, "y": cell["y"] % GRID_HEIGHT}


def move_player(player, new_head, grow):
    player["snake"].insert(0, new_head)
    if not grow:
        player["snake"].pop()


# is this cell (compared by x and y only) in the list?
def is_on(cell, cells):
    for other in cells:
        if other["x"] == cell["x"] and other["y"] == cell["y"]:
            return True
    return False


# the golden apple as a plain cell, so spawn_food and the AI can treat it like any other cell
def bonus_cells(game):
    if game["bonus"] is None:
        return []
    return [{"x": game["bonus"]["x"], "y": game["bonus"]["y"]}]


# seconds shown on screen, rounded up so "0" only shows when time is really over
def refresh_clock(game):
    game["countdown"] = (game["countdown_ticks"] + TICKS_PER_SECOND - 1) // TICKS_PER_SECOND
    game["seconds_left"] = (game["ticks_left"] + TICKS_PER_SECOND - 1) // TICKS_PER_SECOND


def decide_match(game):
    wins = game["round_wins"]
    if wins[0] != wins[1]:
        return "P1" if wins[0] > wins[1] else "P2"
    totals = game["total_scores"]              # equal rounds won: most points overall wins
    if totals[0] != totals[1]:
        return "P1" if totals[0] > totals[1] else "P2"
    return "TIE"


# called once a round has a winner. Records it and decides if the match is over.
def end_round(game):
    for i in range(2):
        game["total_scores"][i] += game["players"][i]["score"]
    if game["winner"] == "P1":
        game["round_wins"][0] += 1
    elif game["winner"] == "P2":
        game["round_wins"][1] += 1

    wins = game["round_wins"]
    if wins[0] >= WINS_NEEDED or wins[1] >= WINS_NEEDED or game["round"] >= MAX_ROUNDS:
        game["match_winner"] = decide_match(game)
        game["status"] = "MATCH_OVER"
    else:
        game["status"] = "ROUND_OVER"


def finish_by_score(game, reason):
    s1 = game["players"][0]["score"]
    s2 = game["players"][1]["score"]
    if s1 > s2:
        game["winner"] = "P1"
    elif s2 > s1:
        game["winner"] = "P2"
    else:
        game["winner"] = "TIE"
    game["reason"] = reason
    end_round(game)


def finish_after_crash(game, crashed):
    if len(crashed) == 2:
        game["winner"] = "TIE"
    elif crashed[0] == 0:
        game["winner"] = "P2"
    else:
        game["winner"] = "P1"
    game["crashed"] = crashed
    game["reason"] = "SELF_COLLISION"
    end_round(game)


# counts the golden apple down, or spawns one after a quiet spell
def update_bonus(game):
    bonus = game["bonus"]
    if bonus is not None:
        bonus["ticks_left"] -= 1
        if bonus["ticks_left"] <= 0:
            game["bonus"] = None
            game["bonus_timer"] = 0
        return

    game["bonus_timer"] += 1
    if game["bonus_timer"] >= BONUS_EVERY_SECONDS * TICKS_PER_SECOND:
        blocked = game["players"][0]["snake"] + game["players"][1]["snake"] + [game["food"]]
        cell = spawn_food(blocked)
        if cell is not None:
            cell["ticks_left"] = BONUS_LIFETIME_SECONDS * TICKS_PER_SECOND
            game["bonus"] = cell
            game["bonus_timer"] = 0


def advance_versus(game):
    if game["status"] == "COUNTDOWN":
        game["countdown_ticks"] -= 1
        if game["countdown_ticks"] <= 0:
            game["status"] = "RUNNING"
        return

    if game["status"] != "RUNNING":
        return

    players = game["players"]
    new_heads = []
    on_food = []
    on_bonus = []
    crashed = []

    # work out every move first, so both players are judged on the same tick
    for i in range(2):
        player = players[i]
        player["direction"] = player["next_direction"]
        new_head = wrap_cell(get_new_head(player))
        eating_food = new_head == game["food"]
        eating_bonus = is_on(new_head, bonus_cells(game))
        new_heads.append(new_head)
        on_food.append(eating_food)
        on_bonus.append(eating_bonus)
        if hits_self(player["snake"], new_head, eating_food or eating_bonus):
            crashed.append(i)

    if len(crashed) > 0:
        finish_after_crash(game, crashed)
        return

    for i in range(2):
        move_player(players[i], new_heads[i], on_food[i] or on_bonus[i])
        if on_food[i]:
            players[i]["score"] += POINTS_PER_APPLE   # if both reach it together, both score
        if on_bonus[i]:
            players[i]["score"] += BONUS_POINTS

    if on_bonus[0] or on_bonus[1]:
        game["bonus"] = None
        game["bonus_timer"] = 0

    if on_food[0] or on_food[1]:
        snakes = players[0]["snake"] + players[1]["snake"] + bonus_cells(game)
        new_food = spawn_food(snakes)
        if new_food is None:
            finish_by_score(game, "BOARD_FULL")
            return
        game["food"] = new_food

    update_bonus(game)

    game["ticks_left"] -= 1
    if game["ticks_left"] <= 0:
        finish_by_score(game, "TIME")


# ---------------------------------------------------------------
# AI player (player 2 in "vs AI" mode)
# ---------------------------------------------------------------
AI_MISTAKE_CHANCE = {"easy": 0.35, "medium": 0.12, "hard": 0.0}   # chance of a random move
OPPOSITES = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}


# distance between two positions on one axis, going the short way around the wrap
def wrapped_distance(a, b, size):
    d = abs(a - b)
    return min(d, size - d)


def cell_distance(a, b):
    return wrapped_distance(a["x"], b["x"], GRID_WIDTH) + wrapped_distance(a["y"], b["y"], GRID_HEIGHT)


# every direction that doesn't reverse and doesn't hit the snake's own body.
# eat_cells are the cells that make the snake grow (so its tail stays).
def get_safe_moves(player, eat_cells):
    safe = []
    for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
        if direction == OPPOSITES[player["direction"]]:
            continue
        test = {"snake": player["snake"], "direction": direction}
        new_head = wrap_cell(get_new_head(test))
        if not hits_self(player["snake"], new_head, is_on(new_head, eat_cells)):
            safe.append((direction, new_head))
    return safe


# flood fill: counts the cells you can walk to from "start" without touching the body
def count_reachable(snake, start):
    blocked = set()
    for cell in snake[:-1]:                         # the tail moves away, so it isn't a wall
        blocked.add((cell["x"], cell["y"]))
    first = (start["x"], start["y"])
    seen = {first}
    queue = [first]
    while len(queue) > 0:
        x, y = queue.pop(0)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbour = ((x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT)
            if neighbour not in seen and neighbour not in blocked:
                seen.add(neighbour)
                queue.append(neighbour)
    return len(seen)


# the golden apple is worth a detour, but only if the AI can reach it before it vanishes
def pick_target(game, player):
    food = game["food"]
    bonus = game["bonus"]
    if bonus is None:
        return food
    head = player["snake"][0]
    d_food = cell_distance(head, food)
    d_bonus = cell_distance(head, bonus)
    if d_bonus <= bonus["ticks_left"] and d_bonus < d_food + 6:
        return bonus
    return food


def choose_ai_direction(game, index, level):
    player = game["players"][index]
    target = pick_target(game, player)
    options = get_safe_moves(player, [game["food"]] + bonus_cells(game))

    if len(options) == 0:
        return player["direction"]                  # trapped, nothing safe left

    if random.random() < AI_MISTAKE_CHANCE[level]:
        return random.choice(options)[0]            # a deliberate "mistake" (still safe)

    best_direction = None
    best_score = None
    for direction, head in options:
        score = cell_distance(head, target) * 10    # closer to the target is better

        # how much open space can the snake still reach after this move?
        future_snake = [head] + player["snake"][:-1]
        if count_reachable(future_snake, head) < len(future_snake):
            score += 1000                           # not enough room left: this move traps the snake

        if best_score is None or score < best_score:
            best_score = score
            best_direction = direction
    return best_direction


def step_versus(game):
    if game["status"] == "RUNNING" and game["ai_level"] is not None:
        game["players"][1]["next_direction"] = choose_ai_direction(game, 1, game["ai_level"])
    advance_versus(game)
    refresh_clock(game)