import tkinter as tk
import random

# --- Configuration ---
CELL_SIZE = 20
GRID_WIDTH = 30   # number of cells horizontally
GRID_HEIGHT = 20  # number of cells vertically
SPEED = 100       # milliseconds between moves

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Very Simple Snake")

        self.canvas = tk.Canvas(
            root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="black"
        )
        self.canvas.pack()

        # Snake starts in the middle
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y)]
        self.direction = (1, 0)  # moving to the right initially

        self.food = None
        self.place_food()

        # Draw everything once
        self.draw()

        # Bind keys
        self.root.bind("<Up>",    lambda e: self.change_direction(0, -1))
        self.root.bind("<Down>",  lambda e: self.change_direction(0, 1))
        self.root.bind("<Left>",  lambda e: self.change_direction(-1, 0))
        self.root.bind("<Right>", lambda e: self.change_direction(1, 0))

        # Start game loop
        self.game_loop()

    def change_direction(self, dx, dy):
        # Optional: avoid reversing directly into yourself
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
                break

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        # Move head; wrap around edges
        new_head = ((head_x + dx) % GRID_WIDTH,
                    (head_y + dy) % GRID_HEIGHT)

        # If we ate the food, grow and place new food
        if new_head == self.food:
            self.snake.insert(0, new_head)  # grow (no tail pop)
            self.place_food()
        else:
            # Normal move: add new head, remove tail
            self.snake.insert(0, new_head)
            self.snake.pop()

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
        self.root.after(SPEED, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
