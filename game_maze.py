import os
import random
import threading
import time

import numpy as np
import pygame
import yaml

from game_base import Game
from maze.ball import BallSprite
from utils import get_font_adaptive, WHITE_BG_COLOR

os.environ["SDL_VIDEO_CENTERED"] = '1'


class GameMaze(Game):
    def __init__(self, config_path: str):
        # self.end_point: tuple[int, int] = (-1, -1)
        # self.start_point: tuple[int, int] = (-1, -1)
        # self.margin_size: int = -1
        # self.block_size: int = -1
        # self.row_num: int = -1
        # self.col_num: int = -1
        # self.width: int = -1
        # self.height: int = -1
        # self.config: dict = {}

        super(GameMaze, self).__init__(config_path)

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.show_text = True
        self.mouse_pos = (-1, -1)
        self.font_size_mapping = {}
        self.init_contents = [f"正在生成迷宫，请稍等{'.' * i}" + '' * (2 - i) for i in range(4)]

    def _read_cfg(self):
        with open(self.config_path) as f:
            self.config = yaml.safe_load(f)

        self.row_num = self.config["ROW_NUM"]
        self.col_num = self.config["COL_NUM"]

        self.block_size = self.config["BLOCK_SIZE"]
        self.margin_size = self.config["MARGIN_SIZE"]

        self.height = self.block_size * self.row_num + self.margin_size * (self.row_num + 1)
        self.width = self.block_size * self.col_num + self.margin_size * (self.col_num + 1)

        self.start_point = (0, 0)
        self.end_point = (self.row_num - 1, self.col_num - 1)

    def _init_state(self):
        self.block_num = int(self.row_num * self.col_num * self.config["BLOCK_RATIO"])
        self.vis = [[1 for _ in range(self.col_num)] for _ in range(self.row_num)]
        self.maze = None
        self.in_game = True
        self.text_color = np.random.randint(0, 100, 3)
        self.dark_bg_color = np.random.randint(0, 100, 3)
        self.light_bg_color = np.random.randint(200, 255, 3)

    def __handle_base_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.in_game = False

    def _run(self):
        thread = threading.Thread(target=self.__build_maze)
        thread.start()

        idx = 0
        clock = pygame.time.Clock()
        while self.in_game:
            idx += 1
            self.__handle_base_event()
            self.screen.fill(WHITE_BG_COLOR)

            if not self.maze:
                content = self.init_contents[idx % len(self.init_contents)]
                if content not in self.font_size_mapping:
                    self.font_size_mapping[content] = get_font_adaptive(
                        max(self.init_contents),
                        self.width // 2,
                        self.height // 2,
                        font_name="microsoftyahei"
                    )

                font = self.font_size_mapping[content]
                text = font.render(content, True, self.text_color)
                text_rect = text.get_rect(topleft=(self.width // 4, self.height // 2))
                self.screen.blit(text, text_rect)

            else:
                ball_group = pygame.sprite.Group()
                ball_sprite = BallSprite(self.config, self.maze)
                ball_group.add(ball_sprite)

                while self.in_game:
                    self.mouse_pos = (-1, -1)
                    self.screen.fill(WHITE_BG_COLOR)
                    self.__handle_event()
                    ball_group.update(pygame.key.get_pressed(), self.mouse_pos)

                    if self.show_text:
                        self.__draw_text()
                    else:
                        self.__draw_block()
                        ball_group.draw(self.screen)

                    pygame.display.flip()
                    clock.tick(60)

            pygame.display.flip()
            clock.tick(10)

    def __draw_block(self):
        for row in range(self.row_num):
            for col in range(self.col_num):
                x = col * self.block_size + (col + 1) * self.margin_size
                y = row * self.block_size + (row + 1) * self.margin_size
                if self.maze[row][col]:
                    pygame.draw.rect(self.screen, self.light_bg_color, (x, y, self.block_size, self.block_size))
                else:
                    pygame.draw.rect(self.screen, self.dark_bg_color, (x, y, self.block_size, self.block_size))

    def __draw_text(self):
        contents = [
            "你好，欢迎开始迷宫游戏!",
            "使用上下左右方向键移动小球!",
            "起点在左上角，终点在右上角!",
            "点击与小球相同行/列的空白处，可以移动小球到点击位置!",
            "按s键打开/关闭该提示!",
        ]
        for idx, content in enumerate(contents):
            if content not in self.font_size_mapping:
                self.font_size_mapping[content] = get_font_adaptive(
                    content,
                    self.width // 2,
                    self.height // 2,
                    font_name="microsoftyahei"
                )
            font = self.font_size_mapping[content]
            text = font.render(content, True, self.text_color)
            rect = text.get_rect(center=(self.width // 2, self.height // (len(contents) + 1) * (idx + 1)))
            self.screen.blit(text, rect)

    def __handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.in_game = False
                elif event.key == pygame.K_s:
                    self.show_text = not self.show_text

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = pygame.mouse.get_pos()

    def __build_maze(self):
        time.sleep(0.1)
        maze = self.__random_generator()
        while self.in_game and not self.__can_pass(maze):
            maze = self.__random_generator()
        self.maze = maze

    def __random_generator(self):
        if random.random() <= 0.1:
            self.block_num -= 5
        print(f"block_num: {self.block_num}, ratio: {(self.block_num / self.row_num / self.col_num * 100):.0f}%")
        maze1d = [False] * self.block_num + [True] * (self.row_num * self.col_num - self.block_num)
        random.shuffle(maze1d)
        maze2d = [maze1d[i: i + self.col_num] for i in range(0, self.row_num * self.col_num, self.col_num)]
        maze2d[self.start_point[0]][self.start_point[1]] = True
        maze2d[self.end_point[0]][self.end_point[1]] = True
        return maze2d

    def __can_pass(self, maze: list):
        self.vis = [[0 for _ in range(self.col_num)] for _ in range(self.row_num)]
        self.vis[self.start_point[0]][self.start_point[1]] = 1

        path = [self.start_point]
        while self.in_game and path:
            for cx, cy in ((x, y) for x, y in path):
                path.remove((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) == self.end_point:
                        self.vis[nx][ny] = self.vis[cx][cy] + 1
                        return True

                    if nx < 0 or ny < 0 or nx >= self.row_num or ny >= self.col_num:
                        continue

                    if self.vis[nx][ny] == 0 and maze[nx][ny]:
                        path.append((nx, ny))
                        self.vis[nx][ny] = self.vis[cx][cy] + 1

        return False
