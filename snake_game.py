import tkinter as tk
from tkinter import messagebox
import random

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20

BASE_SPEED = 400   # start slower (1/4 of original 100ms)
MIN_SPEED = 80     # never go faster than this
SPEED_INCREASE = 5 # reduce delay by this amount each time food is eaten


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Very Simple Snake")

        # Score
        self.score = 0

        # Starting speed
        self.speed = BASE_SPEED

        # Scoreboard
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 14))
        self.score_label.pack()

        # Canvas
        self.canvas = tk.Canvas(
            root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="black"
        )
        self.canvas.pack()

        # Starting snake position
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y)]
        self.direction = (1, 0)

        self.food = None
        self.place_food()
        self.draw()

        # Key bindings
        self.root.bind("<Up>",    lambda e: self.change_direction(0, -1))
        self.root.bind("<Down>",  lambda e: self.change_direction(0, 1))
        self.root.bind("<Left>",  lambda e: self.change_direction(-1, 0))
        self.root.bind("<Right>", lambda e: self.change_direction(1, 0))

        self.game_loop()

    def change_direction(self, dx, dy):
        current_dx, current_dy = self.direction
        if (dx, dy) == (-current_dx, -current_dy):  # prevent reversing
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

        # Losing condition: self collision
        if new_head in self.snake:
            self.game_over()
            return

        # Eating food
        if new_head == self.food:
            self.snake.insert(0, new_head)

            # Increase score
            self.score += 2
            self.update_score()

            # Increase speed slightly (but stay above minimum)
            self.speed = max(MIN_SPEED, self.speed - SPEED_INCREASE)

            self.place_food()

        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def game_over(self):
        messagebox.showinfo("Game Over", f"You lost!\nFinal Score: {self.score}")
        self.root.destroy()

    def draw_cell(self, x, y, color):
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw(self):
        self.canvas.delete("all")

        # Draw food
        fx, fy = self.food
        self.draw_cell(fx, fy, "red")

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = "lime" if i == 0 else "green"
            self.draw_cell(x, y, color)

    def game_loop(self):
        self.move_snake()
        self.draw()
        self.root.after(self.speed, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
