import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

# --- Optional sound support ---
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20

BASE_SPEED = 400
MIN_SPEED = 80
SPEED_INCREASE = 5


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Very Simple Snake")

        self.game_running = False
        self.music_running = True  # flag to control background music

        # Start menu popup
        self.start_menu()

        # Scoreboard
        self.score = 0
        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 14))
        self.score_label.pack()

        # Canvas
        self.canvas = tk.Canvas(
            root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="black"
        )
        self.canvas.pack()

        # Initialize game variables
        self.reset_game()

        # Key bindings
        self.root.bind("<Up>",    lambda e: self.change_direction(0, -1))
        self.root.bind("<Down>",  lambda e: self.change_direction(0, 1))
        self.root.bind("<Left>",  lambda e: self.change_direction(-1, 0))
        self.root.bind("<Right>", lambda e: self.change_direction(1, 0))

        # Start music in background
        threading.Thread(target=self.background_music, daemon=True).start()

    # ---------- BASIC CHIPTUNE MUSIC ----------

    def background_music(self):
        """Very simple looping 8-bit-style beeping melody."""
        if not HAS_WINSOUND:
            return

        # A simple melody pattern (Hz + ms)
        melody = [
            (600, 120), (800, 120), (900, 120), (800, 120),
            (600, 120), (800, 120), (900, 120), (800, 120)
        ]

        while self.music_running:
            for freq, dur in melody:
                if not self.music_running:
                    break
                winsound.Beep(freq, dur)
                time.sleep(0.02)  # tiny pause between notes

    # ---------- SOUNDS ----------

    def play_eat_sound(self):
        if HAS_WINSOUND:
            winsound.Beep(1000, 80)
        else:
            self.root.bell()

    def play_game_over_sound(self):
        if HAS_WINSOUND:
            winsound.Beep(300, 300)
        else:
            self.root.bell()

    # ---------- MENUS ----------

    def start_menu(self):
        start_win = tk.Toplevel(self.root)
        start_win.title("Snake")
        start_win.geometry("240x120")
        start_win.grab_set()

        tk.Label(start_win, text="Welcome to Snake!", font=("Arial", 12)).pack(pady=10)

        tk.Button(start_win, text="Start Game", width=15,
                  command=lambda: self.start_game(start_win)).pack(pady=5)
        tk.Button(start_win, text="Exit", width=15,
                  command=self.quit_game).pack()

    def quit_game(self):
        self.music_running = False
        self.root.destroy()

    def start_game(self, popup):
        popup.destroy()
        self.game_running = True
        self.root.focus_set()
        self.game_loop()

    def game_over_menu(self):
        self.game_running = False
        self.play_game_over_sound()

        go = tk.Toplevel(self.root)
        go.title("Game Over")
        go.geometry("240x150")
        go.grab_set()

        tk.Label(go, text=f"Game Over!\nFinal Score: {self.score}",
                 font=("Arial", 12)).pack(pady=10)

        tk.Button(go, text="Try Again", width=15,
                  command=lambda: self.restart(go)).pack(pady=5)
        tk.Button(go, text="Exit", width=15,
                  command=self.quit_game).pack(pady=5)

    def restart(self, popup):
        popup.destroy()
        self.reset_game()
        self.game_running = True
        self.root.focus_set()
        self.game_loop()

    # ---------- GAME LOGIC ----------

    def reset_game(self):
        self.score = 0
        self.score_label.config(text="Score: 0")
        self.speed = BASE_SPEED

        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y)]
        self.direction = (1, 0)

        self.food = None
        self.place_food()
        self.draw()

    def change_direction(self, dx, dy):
        cx, cy = self.direction
        if (dx, dy) == (-cx, -cy):
            return
        self.direction = (dx, dy)

    def place_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                return

    def move_snake(self):
        hx, hy = self.snake[0]
        dx, dy = self.direction

        new_head = ((hx + dx) % GRID_WIDTH,
                    (hy + dy) % GRID_HEIGHT)

        if new_head in self.snake:
            self.game_over_menu()
            return

        if new_head == self.food:
            self.snake.insert(0, new_head)

            self.score += 2
            self.score_label.config(text=f"Score: {self.score}")

            self.play_eat_sound()

            self.speed = max(MIN_SPEED, self.speed - SPEED_INCREASE)

            self.place_food()
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

    # ---------- DRAWING ----------

    def draw_cell(self, x, y, color):
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw(self):
        self.canvas.delete("all")

        fx, fy = self.food
        self.draw_cell(fx, fy, "red")

        for i, (x, y) in enumerate(self.snake):
            col = "lime" if i == 0 else "green"
            self.draw_cell(x, y, col)

    # ---------- MAIN LOOP ----------

    def game_loop(self):
        if self.game_running:
            self.move_snake()
            self.draw()
            self.root.after(self.speed, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
