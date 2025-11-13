import tkinter as tk
from tkinter import messagebox
import random
import os

# ---- Optional short sound effects (Windows only) ----
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# ---- Background music with pygame ----
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20

BASE_SPEED = 400   # slower start
MIN_SPEED = 80
SPEED_INCREASE = 5

# Path to this script's folder
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Very Simple Snake")

        # Game state flags
        self.game_running = False
        self.music_initialized = False
        self.music_playing = False
        self.paused = False          # pause flag

        # Initialise music (but don't start it yet)
        self.init_music()

        # Score
        self.score = 0

        # Start menu popup
        self.start_menu()

        # Scoreboard
        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 14))
        self.score_label.pack()

        # Pause / Resume button
        self.pause_button = tk.Button(root, text="Pause", width=10,
                                      command=self.toggle_pause)
        self.pause_button.pack(pady=5)

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
        self.root.bind("p",       lambda e: self.toggle_pause())
        self.root.bind("P",       lambda e: self.toggle_pause())

        # Make sure closing the window stops music too
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)

    # ---------- MUSIC CONTROL ----------

    def init_music(self):
        """Initialise pygame mixer and load background music safely."""
        if not HAS_PYGAME:
            print("pygame not available, background music disabled.")
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(r"C:\Users\semoy\OneDrive\Documentos\Keele University\1.Foundations of Programming\Pokemon music.mp3")
            pygame.mixer.music.set_volume(0.4)
            self.music_initialized = True
            print("Music initialised successfully.")
        except Exception as e:
            print("Could not initialise music:", e)
            self.music_initialized = False

    def start_music(self):
        """Start looping background music."""
        if self.music_initialized and not self.music_playing:
            try:
                pygame.mixer.music.play(-1)  # loop forever
                self.music_playing = True
                print("Music started.")
            except Exception as e:
                print("Could not start music:", e)

    def stop_music(self):
        """Stop background music."""
        if self.music_initialized and self.music_playing:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print("Error stopping music:", e)
            finally:
                self.music_playing = False
                self.music_initialized = False
                print("Music stopped.")

    # ---------- SIMPLE EFFECTS (optional) ----------

    def play_eat_sound(self):
        if HAS_WINSOUND:
            winsound.Beep(1000, 70)
        else:
            self.root.bell()

    def play_game_over_sound(self):
        if HAS_WINSOUND:
            winsound.Beep(300, 250)
        else:
            self.root.bell()

    # ---------- MENUS & EXIT ----------

    def start_menu(self):
        start_win = tk.Toplevel(self.root)
        start_win.title("Snake")
        start_win.geometry("240x120")
        start_win.grab_set()

        tk.Label(start_win, text="Welcome to Snake!", font=("Arial", 12)).pack(pady=10)

        tk.Button(
            start_win, text="Start Game", width=15,
            command=lambda: self.start_game(start_win)
        ).pack(pady=5)

        tk.Button(
            start_win, text="Exit", width=15,
            command=self.quit_game
        ).pack()

    def start_game(self, popup):
        popup.destroy()
        self.game_running = True
        self.paused = False
        self.pause_button.config(text="Pause")
        self.root.focus_set()

        # Start background music when the game truly starts
        self.start_music()

        self.game_loop()

    def game_over_menu(self):
        self.game_running = False
        self.play_game_over_sound()

        go = tk.Toplevel(self.root)
        go.title("Game Over")
        go.geometry("240x150")
        go.grab_set()

        tk.Label(
            go,
            text=f"Game Over!\nFinal Score: {self.score}",
            font=("Arial", 12)
        ).pack(pady=10)

        tk.Button(
            go, text="Try Again", width=15,
            command=lambda: self.restart(go)
        ).pack(pady=5)

        tk.Button(
            go, text="Exit", width=15,
            command=self.quit_game
        ).pack(pady=5)

    def restart(self, popup):
        popup.destroy()
        self.reset_game()
        self.game_running = True
        self.paused = False
        self.pause_button.config(text="Pause")
        self.root.focus_set()
        self.game_loop()

    def quit_game(self):
        """Cleanly exit game + stop music."""
        self.game_running = False
        self.stop_music()
        self.root.destroy()

    # ---------- PAUSE LOGIC ----------

    def toggle_pause(self):
        """Toggle paused state and update button text."""
        # If the game hasn't started yet, ignore
        if not self.game_running:
            return

        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")

    # ---------- GAME LOGIC ----------

    def reset_game(self):
        self.score = 0
        self.score_label.config(text="Score: 0")
        self.speed = BASE_SPEED

        # Reset pause state
        self.paused = False
        if hasattr(self, "pause_button"):
            self.pause_button.config(text="Pause")

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

        # Self-collision
        if new_head in self.snake:
            self.game_over_menu()
            return

        # Eating food
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
            if not self.paused:
                self.move_snake()
                self.draw()
            # Even if paused, keep scheduling the loop
            self.root.after(self.speed, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
