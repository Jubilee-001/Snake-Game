# Snake Game

A Snake game with a **Python backend** (all the game rules) and an **HTML / CSS / JavaScript frontend** (drawing and input).
No external libraries: only Python's built-in modules (`random`, `json`, `http.server`).

## How to run

1. Open a terminal in this folder.
2. Start the server:
   ```
   python server.py
   ```
3. Open **http://localhost:8000** in a browser (Chrome or Edge recommended).
4. Stop the server with `Ctrl+C`.

Do not open `index.html` by double-clicking it. The page needs the server running. No internet is needed.

## Game modes

| Mode         | Description                                                                                                      |
| ------------ | ---------------------------------------------------------------------------------------------------------------- |
| **1 Player** | Classic snake. Eat apples, grow, score points. The game speeds up in levels. Walls and your own body are deadly. |
| **Versus**   | Two players, one shared apple, best of 3 rounds.                                                                 |
| **vs AI**    | Versus against a computer player: Easy, Medium or Hard.                                                          |

### Versus rules

- Each round lasts 60 seconds after a 3-2-1 countdown. The highest score wins the round.
- First to win 2 rounds wins the match (a tied round counts for nobody; if rounds are level after 3, total points decide).
- Walls **wrap around**: leave the right edge and you come out on the left (same for top and bottom).
- Snakes pass through each other.
- **Hitting your own body loses the round immediately.**
- A normal apple is worth 10 points. A **golden apple** appears every ~12 seconds for 6 seconds and is worth 30.

## Controls

|                         | Keyboard              | Controller          |
| ----------------------- | --------------------- | ------------------- |
| Steer                   | Arrow keys or W A S D | D-pad or left stick |
| Pause / resume          | Space or P            | Options             |
| Next round / play again | Enter                 | Cross (X)           |
| Restart                 | R                     | Share               |

Versus assignments: with no controller, **P1 = W A S D** and **P2 = arrow keys**. With one controller, the **controller is P1** and the keyboard is P2. With two controllers, one each. Against the AI, all your inputs control you.

Press a button on the controller once so the browser can see it. If one controller is detected twice, press the **Controllers** button under the board until it says "use 1".

## Files

| File          | Job                                                                                  |
| ------------- | ------------------------------------------------------------------------------------ |
| `practise.py` | Single-player rules: movement, food, collisions, scoring, speed levels, pause        |
| `versus.py`   | Versus rules: rounds, countdown, timer, golden apple, wrap-around, and the AI player |
| `server.py`   | Connects the browser to the Python functions (HTTP + JSON)                           |
| `index.html`  | The page: drawing on a canvas, keyboard and controller input, game loop              |

## How it works

The browser asks the server for the game state, draws it, and sends key presses back. The server runs the matching Python function and replies with the whole game as JSON.

| Request           | Python function                        |
| ----------------- | -------------------------------------- |
| `GET /state`      | returns the game dictionary            |
| `POST /tick`      | `step_game` or `step_versus`           |
| `POST /direction` | `change_direction`                     |
| `POST /pause`     | `toggle_pause`                         |
| `POST /reset`     | creates a new game in the current mode |
| `POST /next`      | `start_next_round`                     |
| `POST /mode`      | switches between single, versus and AI |

## Tuning the game

Every number you might want to change is a named constant at the top of the file.

- `practise.py`: `START_DELAY`, `APPLES_PER_LEVEL`, `DELAY_DROP_PER_LEVEL`, `MIN_DELAY`, `POINTS_PER_APPLE`
- `versus.py`: `ROUND_SECONDS`, `MAX_ROUNDS`, `WINS_NEEDED`, `VERSUS_DELAY`, `BONUS_EVERY_SECONDS`, `BONUS_LIFETIME_SECONDS`, `BONUS_POINTS`, `AI_MISTAKE_CHANCE`

Restart `server.py` after changing a Python file.

## Troubleshooting

- **Page loads but nothing moves:** the server is not running, or the page was opened as a file. Use `http://localhost:8000`.
- **"Address already in use":** another program uses port 8000. Close it, or change `PORT` in `server.py`.
- **Controller does nothing:** press a button on it while the page is focused, and use Chrome or Edge.
- **Controller moves both snakes:** it is being detected twice. Click the **Controllers** button until it says "use 1".

## Known limitations

- One shared game: two browser tabs share the same game.
- The game and high score live in memory and reset when the server restarts.
- Built for local use on one computer.
