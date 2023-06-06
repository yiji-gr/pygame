import random
import sys
import threading

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

FONT_SIZE = 50
TEXT_COLOR = np.random.randint(0, 100, 3)

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

    def move_up_down(self, row):
        row = min(max(0, row), ROW_NUM - 1)
        step = 1 if self.row < row else -1
        next_row = self.row + step
        while maze[next_row][self.col]:
            self.row = next_row
            if next_row == row:
                return
            next_row += step

    def move_left_right(self, col):
        col = min(max(0, col), COL_NUM - 1)
        step = 1 if self.col < col else -1
        next_col = self.col + step
        while maze[self.row][next_col]:
            self.col = next_col
            if next_col == col:
                return
            next_col += step

    def update(self, keys_pressed):
        if mouse_pos != (-1, -1):
            col, row = mouse_pos
            col -= MARGIN_SIZE
            row -= MARGIN_SIZE
            col = col // (BLOCK_SIZE + MARGIN_SIZE)
            row = row // (BLOCK_SIZE + MARGIN_SIZE)
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


def handle_event1():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit_program()


def handle_event2():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit_program()
            if event.key == pygame.K_s:
                global show_text
                show_text = not show_text

        if event.type == pygame.MOUSEBUTTONDOWN:
            global mouse_pos
            mouse_pos = pygame.mouse.get_pos()


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
    maze2d = [maze1d[i: i + COL_NUM] for i in range(0, ROW_NUM * COL_NUM, COL_NUM)]
    maze2d[START_POINT[0]][START_POINT[1]] = True
    maze2d[END_POINT[0]][END_POINT[1]] = True
    return maze2d


def generate_maze():
    maze_ = random_generator()
    while not can_pass(maze_):
        maze_ = random_generator()
    return maze_


def draw_text():
    text1 = font.render("你好，欢迎开始迷宫游戏!", True, TEXT_COLOR)
    text2 = font.render("使用上下左右方向键移动小球!", True, TEXT_COLOR)
    text3 = font.render("起点在左上角，终点在右上角!", True, TEXT_COLOR)
    text4 = font.render("点击与小球相同行/列的空白处，可以移动小球到点击位置!", True, TEXT_COLOR)
    text5 = font.render("按s键打开/关闭该提示!", True, TEXT_COLOR)

    text_rect1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - FONT_SIZE * 2))
    text_rect2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 - FONT_SIZE))
    text_rect3 = text3.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    text_rect4 = text4.get_rect(center=(WIDTH // 2, HEIGHT // 2 + FONT_SIZE))
    text_rect5 = text5.get_rect(center=(WIDTH // 2, HEIGHT // 2 + FONT_SIZE * 2))

    screen.blit(text1, text_rect1)
    screen.blit(text2, text_rect2)
    screen.blit(text3, text_rect3)
    screen.blit(text4, text_rect4)
    screen.blit(text5, text_rect5)


def my_thread():
    global maze, init
    maze = generate_maze()
    init = False

    # print_maze(maze)
    # print_maze(vis)


if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()

    pygame.display.set_caption("迷宫游戏")

    font = pygame.font.SysFont("microsoftyahei", FONT_SIZE)

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

    clock = pygame.time.Clock()

    mouse_pos = (-1, -1)
    show_text = True

    maze = []
    init = True

    thread = threading.Thread(target=my_thread)
    thread.daemon = True
    thread.start()
    idx = 0
    while True:
        idx += 1
        handle_event1()
        screen.fill(WHITE_BG_COLOR)

        if init:
            texts = [f"正在生成迷宫，请稍等{'.'*i}" for i in range(4)]
            text = font.render(texts[idx % len(texts)], True, TEXT_COLOR)
            text_rect = text.get_rect(topleft=(WIDTH // 4, HEIGHT // 2))
            screen.blit(text, text_rect)
        else:
            thread.join()

            while True:
                mouse_pos = (-1, -1)
                screen.fill(WHITE_BG_COLOR)
                handle_event2()
                ball_group.update(pygame.key.get_pressed())

                if show_text:
                    draw_text()
                else:
                    draw_block()
                    ball_group.draw(screen)

                pygame.display.flip()
                clock.tick(60)

        pygame.display.flip()
        clock.tick(6)
