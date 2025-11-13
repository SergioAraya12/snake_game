import tkinter as tk
from tkinter import messagebox
import random

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20

BASE_SPEED = 400   # slower start
MIN_SPEED = 80
SPEED_INCREASE = 5


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Very Simple Snake")

        # Block game until user clicks Start
        self.game_running = False

        # Score
        self.score = 0

        # Start menu popup
        self.start_menu()

        # Scoreboard
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

        # 🔑 Key bindings (were missing before)
        self.root.bind("<Up>",    lambda e: self.change_direction(0, -1))
        self.root.bind("<Down>",  lambda e: self.change_direction(0, 1))
        self.root.bind("<Left>",  lambda e: self.change_direction(-1, 0))
        self.root.bind("<Right>", lambda e: self.change_direction(1, 0))

    def start_menu(self):
        """Initial start menu popup."""
        start_win = tk.Toplevel(self.root)
        start_win.title("Snake")
        start_win.geometry("240x120")
        start_win.grab_set()  # Block interaction with main window

        tk.Label(start_win, text="Welcome to Snake!", font=("Arial", 12)).pack(pady=10)

        tk.Button(start_win, text="Start Game", width=15,
                  command=lambda: self.start_game(start_win)).pack(pady=5)
        tk.Button(start_win, text="Exit", width=15,
                  command=self.root.destroy).pack()

    def start_game(self, popup):
        popup.destroy()
        self.game_running = True
        self.root.focus_set()  # ensure main window receives key events
        self.game_loop()

    def reset_game(self):
        """Reset snake and game variables for replay."""
        self.score = 0
        self.score_label.config(text="Score: 0")
        self.speed = BASE_SPEED

        # Starting snake location
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y)]
        self.direction = (1, 0)

        # Place food
        self.food = None
        self.place_food()

        # Draw initial state
        self.draw()

    def change_direction(self, dx, dy):
        current_dx, current_dy = self.direction
        if (dx, dy) == (-current_dx, -current_dy):
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
        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = ((head_x + dx) % GRID_WIDTH,
                    (head_y + dy) % GRID_HEIGHT)

        # Losing condition: snake hits itself
        if new_head in self.snake:
            self.game_over_menu()
            return

        # Eating food
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.score += 2
            self.score_label.config(text=f"Score: {self.score}")

            # speed increases slightly
            self.speed = max(MIN_SPEED, self.speed - SPEED_INCREASE)

            self.place_food()
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

    def game_over_menu(self):
        """Popup with Try Again / Exit."""
        self.game_running = False

        go = tk.Toplevel(self.root)
        go.title("Game Over")
        go.geometry("240x150")
        go.grab_set()

        tk.Label(go, text=f"Game Over!\nFinal Score: {self.score}",
                 font=("Arial", 12)).pack(pady=10)

        tk.Button(go, text="Try Again", width=15,
                  command=lambda: self.restart(go)).pack(pady=5)
        tk.Button(go, text="Exit", width=15,
                  command=self.root.destroy).pack(pady=5)

    def restart(self, popup):
        popup.destroy()
        self.reset_game()
        self.game_running = True
        self.root.focus_set()
        self.game_loop()

    def draw_cell(self, x, y, color):
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw(self):
        self.canvas.delete("all")

        # Food
        fx, fy = self.food
        self.draw_cell(fx, fy, "red")

        # Snake
        for i, (x, y) in enumerate(self.snake):
            self.draw_cell(x, y, "lime" if i == 0 else "green")

    def game_loop(self):
        if self.game_running:
            self.move_snake()
            self.draw()
            self.root.after(self.speed, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
