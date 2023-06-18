import pygame.key

from game_maze import *


class BallSprite(pygame.sprite.Sprite):
    def __init__(self, config: dict, maze: list):
        super(BallSprite, self).__init__()
        self.config = config
        self.block_size = self.config["BLOCK_SIZE"]
        self.margin_size = self.config["MARGIN_SIZE"]
        self.row_num = self.config["ROW_NUM"]
        self.col_num = self.config["COL_NUM"]

        self.start_point = (0, 0)
        self.end_point = (self.row_num - 1, self.col_num - 1)

        self.image = pygame.image.load(self.config["BALL_IMG_PATH"])
        self.image = pygame.transform.scale(self.image, (self.block_size, self.block_size))
        self.rect = self.image.get_rect()
        self.row, self.col = self.start_point
        self.adjust()
        self.last_key_time = pygame.time.get_ticks()
        self.played = False
        self.maze = maze

        self.collide = pygame.mixer.Sound(self.config["COLLIDE_SOUND_PATH"])
        self.walk = pygame.mixer.Sound(self.config["WALK_SOUND_PATH"])
        self.success = pygame.mixer.Sound(self.config["SUCCESS_SOUND_PATH"])

    def adjust(self):
        self.rect.topleft = (
            self.col * self.block_size + (self.col + 1) * self.margin_size,
            self.row * self.block_size + (self.row + 1) * self.margin_size,
        )

    def move_up(self):
        if self.row - 1 >= 0 and self.maze[self.row - 1][self.col]:
            self.row -= 1
            self.walk.play()
        else:
            self.collide.play()

    def move_down(self):
        if self.row + 1 < self.row_num and self.maze[self.row + 1][self.col]:
            self.row += 1
            self.walk.play()
        else:
            self.collide.play()

    def move_left(self):
        if self.col - 1 >= 0 and self.maze[self.row][self.col - 1]:
            self.col -= 1
            self.walk.play()
        else:
            self.collide.play()

    def move_right(self):
        if self.col + 1 < self.col_num and self.maze[self.row][self.col + 1]:
            self.col += 1
            self.walk.play()
        else:
            self.collide.play()

    def move_up_down(self, row):
        row = min(max(0, row), self.row_num - 1)
        step = 1 if self.row < row else -1
        next_row = self.row + step
        while self.maze[next_row][self.col]:
            self.row = next_row
            if next_row == row:
                return
            next_row += step

    def move_left_right(self, col):
        col = min(max(0, col), self.col_num - 1)
        step = 1 if self.col < col else -1
        next_col = self.col + step
        while self.maze[self.row][next_col]:
            self.col = next_col
            if next_col == col:
                return
            next_col += step

    def update(self, keys_pressed: pygame.key.ScancodeWrapper, mouse_pos: tuple[int, int]):
        if mouse_pos != (-1, -1):
            col, row = mouse_pos
            col -= self.margin_size
            row -= self.margin_size
            col = col // (self.block_size + self.margin_size)
            row = row // (self.block_size + self.margin_size)
            if row == self.row:
                self.move_left_right(col)
            elif col == self.col:
                self.move_up_down(row)
        else:
            current_time = pygame.time.get_ticks()
            if keys_pressed[pygame.K_UP] and current_time - self.last_key_time > 200:
                self.move_up()
                self.last_key_time = current_time
            elif keys_pressed[pygame.K_DOWN] and current_time - self.last_key_time > 200:
                self.move_down()
                self.last_key_time = current_time
            elif keys_pressed[pygame.K_LEFT] and current_time - self.last_key_time > 200:
                self.move_left()
                self.last_key_time = current_time
            elif keys_pressed[pygame.K_RIGHT] and current_time - self.last_key_time > 200:
                self.move_right()
                self.last_key_time = current_time
            elif keys_pressed[pygame.K_r]:
                self.row, self.col = self.start_point
            elif keys_pressed[pygame.K_j] and current_time - self.last_key_time > 200:
                x = random.randint(0, self.row_num - 1)
                y = random.randint(0, self.col_num - 1)
                while not self.maze[x][y]:
                    x = random.randint(0, self.row_num - 1)
                    y = random.randint(0, self.col_num - 1)
                self.row, self.col = x, y
                self.last_key_time = current_time

        self.adjust()

        if (self.row, self.col) == self.end_point:
            if not self.played:
                self.success.play()
                self.played = True
        else:
            self.played = False
