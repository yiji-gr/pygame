import random
import sys

import numpy as np
import pygame

WIDTH = 1400
HEIGHT = 800

BLOCK_SIZE = 15
MARGIN_SIZE = 1

BALL_IMG_PATH = "ball.jfif"

COLLIDE_SOUND_PATH = "collide.wav"
WALK_SOUND_PATH = "walk.wav"
SUCCESS_SOUND_PATH = "success.wav"

ROW_NUM = HEIGHT // BLOCK_SIZE
COL_NUM = WIDTH // BLOCK_SIZE
BLOCK_RATIO = 0.45
block_num = int(ROW_NUM * COL_NUM * BLOCK_RATIO)

RED_BG_COLOR = (255, 0, 0)
WHITE_BG_COLOR = (255, 255, 255)
DARK_BG_COLOR = np.random.randint(0, 100, 3)
LIGHT_BG_COLOR = np.random.randint(200, 255, 3)

vis = [[1 for _ in range(COL_NUM)] for _ in range(ROW_NUM)]


START_POINT = (0, 0)
END_POINT = (ROW_NUM - 1, COL_NUM - 1)


print(f"ROW_NUM: {ROW_NUM}, COL_NUM: {COL_NUM}")


class BallSprite(pygame.sprite.Sprite):
    def __init__(self):
        super(BallSprite, self).__init__()
        self.image = pygame.image.load(BALL_IMG_PATH)
        self.image = pygame.transform.scale(self.image, (BLOCK_SIZE, BLOCK_SIZE))
        self.rect = self.image.get_rect()
        self.row, self.col = START_POINT
        self.adjust()
        self.last_key_time = pygame.time.get_ticks()
        self.played = False

    def adjust(self):
        self.rect.topleft = (
            self.col * BLOCK_SIZE + (self.col + 1) * MARGIN_SIZE,
            self.row * BLOCK_SIZE + (self.row + 1) * MARGIN_SIZE,
        )

    def move_up(self):
        if self.row - 1 >= 0 and maze[self.row - 1][self.col]:
            self.row -= 1
            walk.play()
        else:
            collide.play()

    def move_down(self):
        if self.row + 1 < ROW_NUM and maze[self.row + 1][self.col]:
            self.row += 1
            walk.play()
        else:
            collide.play()

    def move_left(self):
        if self.col - 1 >= 0 and maze[self.row][self.col - 1]:
            self.col -= 1
            walk.play()
        else:
            collide.play()

    def move_right(self):
        if self.col + 1 < COL_NUM and maze[self.row][self.col + 1]:
            self.col += 1
            walk.play()
        else:
            collide.play()

    def update(self, keys_pressed):
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

        if keys_pressed[pygame.K_r]:
            self.row, self.col = START_POINT
        if keys_pressed[pygame.K_j] and current_time - self.last_key_time > 200:
            x = random.randint(0, ROW_NUM - 1)
            y = random.randint(0, COL_NUM - 1)
            while not maze[x][y]:
                x = random.randint(0, ROW_NUM - 1)
                y = random.randint(0, COL_NUM - 1)
            self.row, self.col = x, y
            self.last_key_time = current_time

        self.adjust()

        if (self.row, self.col) == END_POINT:
            if not self.played:
                success.play()
                self.played = True
        else:
            self.played = False


def exit_program():
    pygame.quit()
    sys.exit()


def draw_block():
    for row in range(ROW_NUM):
        for col in range(COL_NUM):
            x = col * BLOCK_SIZE + (col + 1) * MARGIN_SIZE
            y = row * BLOCK_SIZE + (row + 1) * MARGIN_SIZE
            if maze[row][col]:
                pygame.draw.rect(screen, LIGHT_BG_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(screen, DARK_BG_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))


def handle_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit_program()


def can_pass(maze_: list):
    global vis
    vis = [[0 for _ in range(COL_NUM)] for _ in range(ROW_NUM)]
    vis[START_POINT[0]][START_POINT[1]] = 1

    path = [START_POINT]
    while path:
        for cx, cy in ((x, y) for x, y in path):
            path.remove((cx, cy))
            for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
                nx, ny = cx + dx, cy + dy
                if (nx, ny) == END_POINT:
                    vis[nx][ny] = vis[cx][cy] + 1
                    return True

                if nx < 0 or ny < 0 or nx >= ROW_NUM or ny >= COL_NUM:
                    continue

                if vis[nx][ny] == 0 and maze_[nx][ny]:
                    path.append((nx, ny))
                    vis[nx][ny] = vis[cx][cy] + 1

    return False


def print_maze(arr: list):
    for each in arr:
        print(" ".join([f"{x:<3}" for x in each]))
    print()


def random_generator():
    global block_num
    if random.random() <= 0.1:
        block_num -= 1
    print(f"block_num: {block_num}, ratio: {(block_num / ROW_NUM / COL_NUM * 100):.0f}%")
    maze1d = [False] * block_num + [True] * (ROW_NUM * COL_NUM - block_num)
    random.shuffle(maze1d)
    maze2d = [maze1d[i: i+COL_NUM] for i in range(0, ROW_NUM * COL_NUM, COL_NUM)]
    maze2d[START_POINT[0]][START_POINT[1]] = True
    maze2d[END_POINT[0]][END_POINT[1]] = True
    return maze2d


def generate_maze():
    maze_ = random_generator()
    while not can_pass(maze_):
        maze_ = random_generator()
    return maze_


if __name__ == '__main__':
    maze = generate_maze()
    # print_maze(maze)
    # print_maze(vis)

    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((
         BLOCK_SIZE * COL_NUM + MARGIN_SIZE * (COL_NUM + 1),
         BLOCK_SIZE * ROW_NUM + MARGIN_SIZE * (ROW_NUM + 1),
    ))

    collide = pygame.mixer.Sound(COLLIDE_SOUND_PATH)
    walk = pygame.mixer.Sound(WALK_SOUND_PATH)
    success = pygame.mixer.Sound(SUCCESS_SOUND_PATH)

    ball_group = pygame.sprite.Group()
    ball_sprite = BallSprite()
    ball_group.add(ball_sprite)

    pygame.display.set_caption("迷宫游戏")

    clock = pygame.time.Clock()
    while True:
        ball_group.update(pygame.key.get_pressed())

        screen.fill(WHITE_BG_COLOR)

        handle_event()

        draw_block()
        ball_group.draw(screen)

        pygame.display.update()
        clock.tick(60)
