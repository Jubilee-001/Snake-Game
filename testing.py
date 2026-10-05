#!/usr/bin/env python3
import http.server
import json
import random
import socketserver
import os

PORT = 8000
GRID_WIDTH = 20
GRID_HEIGHT = 20

# Initial server state
game_state = {
    "snake": [{"x": 10, "y": 10}, {"x": 9, "y": 10}, {"x": 8, "y": 10}],
    "direction": "RIGHT",
    "next_direction": "RIGHT",
    "food": {"x": 15, "y": 10},
    "score": 0,
    "high_score": 0,
    "status": "RUNNING",  # RUNNING, PAUSED, GAME_OVER, WIN
    "input_locked": False,
}

def spawn_food(snake):
    all_coords = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)]
    snake_coords = {(seg["x"], seg["y"]) for seg in snake}
    available = [c for c in all_coords if c not in snake_coords]

    if not available:
        return None  # Board is full -> WIN condition

    chosen = random.choice(available)
    return {"x": chosen[0], "y": chosen[1]}

def reset_game():
    global game_state
    high_score = game_state["high_score"]
    game_state = {
        "snake": [{"x": 10, "y": 10}, {"x": 9, "y": 10}, {"x": 8, "y": 10}],
        "direction": "RIGHT",
        "next_direction": "RIGHT",
        "food": {"x": 15, "y": 10},
        "score": 0,
        "high_score": high_score,
        "status": "RUNNING",
        "input_locked": False,
    }
    new_food = spawn_food(game_state["snake"])
    if new_food:
        game_state["food"] = new_food

def step_game():
    """Advances the game simulation by one tick if running."""
    if game_state["status"] != "RUNNING":
        return

    game_state["direction"] = game_state["next_direction"]
    game_state["input_locked"] = False

    head = game_state["snake"][0]
    dx, dy = 0, 0
    d = game_state["direction"]

    if d == "UP":
        dy = -1
    elif d == "DOWN":
        dy = 1
    elif d == "LEFT":
        dx = -1
    elif d == "RIGHT":
        dx = 1

    new_head = {"x": head["x"] + dx, "y": head["y"] + dy}

    # 1. Boundary & Wall Collision Check
    if not (0 <= new_head["x"] < GRID_WIDTH and 0 <= new_head["y"] < GRID_HEIGHT):
        game_state["status"] = "GAME_OVER"
        return

    # 2. Check if food is eaten
    eating = (new_head["x"] == game_state["food"]["x"] and new_head["y"] == game_state["food"]["y"])

    # 3. Tail-Chasing / Tail-Space Collision Check
    body_to_check = game_state["snake"][:-1] if not eating else game_state["snake"]
    for seg in body_to_check:
        if seg["x"] == new_head["x"] and seg["y"] == new_head["y"]:
            game_state["status"] = "GAME_OVER"
            return

    # 4. Move snake
    game_state["snake"].insert(0, new_head)

    if eating:
        game_state["score"] += 10
        if game_state["score"] > game_state["high_score"]:
            game_state["high_score"] = game_state["score"]
        
        new_food = spawn_food(game_state["snake"])
        if new_food is None:
            game_state["status"] = "WIN"
        else:
            game_state["food"] = new_food
    else:
        game_state["snake"].pop()


class SnakeHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            if os.path.exists("index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open("index.html", "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"index.html not found.")
        elif self.path == "/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(game_state).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global game_state
        if self.path == "/tick":
            step_game()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(game_state).encode("utf-8"))
        elif self.path == "/input":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                new_dir = data.get("direction")
                current_dir = game_state["direction"]
                opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
                
                # Only accept inputs if game is actively running
                if game_state["status"] == "RUNNING" and new_dir in ["UP", "DOWN", "LEFT", "RIGHT"] and not game_state["input_locked"]:
                    if new_dir != opposites.get(current_dir):
                        game_state["next_direction"] = new_dir
                        game_state["input_locked"] = True
            except Exception:
                pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(game_state).encode("utf-8"))
        elif self.path == "/pause":
            # Toggle pause state if game is running or already paused
            if game_state["status"] == "RUNNING":
                game_state["status"] = "PAUSED"
            elif game_state["status"] == "PAUSED":
                game_state["status"] = "RUNNING"
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(game_state).encode("utf-8"))
        elif self.path == "/reset":
            reset_game()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(game_state).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), SnakeHTTPHandler) as httpd:
        print(f"==================================================")
        print(f"Snake Game Server running successfully!")
        print(f"Open your browser and navigate to:")
        print(f"    http://localhost:{PORT}")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")