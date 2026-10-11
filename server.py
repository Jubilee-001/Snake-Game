# server.py - glue between the browser and practise.py / versus.py
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from practise import create_new_game, step_game, change_direction, toggle_pause
from versus import create_versus_game, step_versus, start_next_round

PORT = 8000
VALID_DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

mode = "single"          # "single", "versus" or "ai"
ai_level = "medium"      # "easy", "medium" or "hard"
high_score = 0           # remembered so switching modes doesn't lose it
game = create_new_game()


def make_game():
    if mode == "versus":
        return create_versus_game()
    if mode == "ai":
        return create_versus_game(ai_level)
    return create_new_game(high_score)


class SnakeHandler(BaseHTTPRequestHandler):

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_state(self):
        data = dict(game)       # copy, so we can add the mode without touching the game
        data["mode"] = mode
        self.send_json(data)

    def do_GET(self):
        if self.path == "/state":
            self.send_state()
        elif self.path == "/" or self.path == "/index.html":
            try:
                with open("index.html", "rb") as f:
                    page = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            except FileNotFoundError:
                self.send_error(404, "index.html not found next to server.py")
        else:
            self.send_error(404)

    def do_POST(self):
        global game, mode, high_score, ai_level

        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/tick":
            if mode in ("versus", "ai"):
                step_versus(game)
            else:
                step_game(game)
                high_score = game["high_score"]
        elif self.path == "/direction":
            direction = data.get("direction")
            player = data.get("player")
            if direction in VALID_DIRECTIONS:
                if mode == "single":
                    change_direction(game, direction)
                elif player in (1, 2) and not (mode == "ai" and player == 2):
                    change_direction(game["players"][player - 1], direction)   # player 2 is the AI in "ai" mode
        elif self.path == "/pause":
            toggle_pause(game)
        elif self.path == "/reset":
            game = make_game()
        elif self.path == "/next":
            if mode in ("versus", "ai"):
                start_next_round(game)
        elif self.path == "/mode":
            if data.get("mode") in ("single", "versus", "ai"):
                mode = data["mode"]
                if data.get("level") in ("easy", "medium", "hard"):
                    ai_level = data["level"]
                game = make_game()
        else:
            self.send_error(404)
            return

        self.send_state()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), SnakeHandler)
    print(f"Snake running at http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.") 