import os
import random

import numpy as np
import pygame
import yaml

from game_base import Game
from utils import get_font_adaptive

os.environ["SDL_VIDEO_CENTERED"] = '1'

NUM_COLOR_MAPPING = {
    2 ** num: np.random.randint(0, 200, 3)
    for num in range(1, 30)
}

DIRECTION_MAPPING = {
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
}


class Game2048(Game):
    def __init__(self, config_path):
        super(Game2048, self).__init__(config_path)
        self.screen = pygame.display.set_mode((self.width, self.height))

    def _read_cfg(self):
        with open(self.config_path) as f:
            self.config = yaml.safe_load(f)

        self.row_num = self.config["ROW_NUM"]
        self.col_num = self.config["COL_NUM"]

        self.block_size = self.config["BLOCK_SIZE"]
        self.margin_size = self.config["MARGIN_SIZE"]
        self.text_area_size = self.config["TEXT_AREA_SIZE"]

        self.height = self.block_size * self.row_num + self.margin_size * (self.row_num + 1)
        self.block_width = self.block_size * self.col_num + self.margin_size * (self.col_num + 1)
        self.width = self.text_area_size + self.block_width

    def _init_state(self):
        self.score = 0
        self.game_over = False
        self.in_game = True
        self.nums = [[0 for _ in range(self.col_num)] for _ in range(self.row_num)]
        self.block_color = (np.random.randint(200, 256, 3))
        self.bg_color = np.random.randint(100, 256, 3)
        self.score_color = np.random.randint(0, 100, 3)
        self.text_color = np.random.randint(0, 50, 3)
        self.font_size_mapping: dict = {}

    def _run(self):
        self.__random_generate()
        self.__run_game()

    # 随机生成一个数字
    def __random_generate(self):
        pos = []
        for row, line in enumerate(self.nums):
            for col, num in enumerate(line):
                if num == 0:
                    pos.append((row, col))

        row, col = random.choice(pos)
        self.nums[row][col] = random.choice(self.config["CANDIDATE_NUMS"])

    @staticmethod
    # 列表转置
    def __transpose(matrix: list) -> list:
        return [[row[i] for row in matrix] for i in range(len(matrix[0]))]

    # 从左往右合并相同数字
    def __merge_line_left(self, line):
        line_tmp = [num for num in line if num != 0]
        idx = 0
        while idx + 1 < len(line_tmp) and line_tmp[idx + 1] != 0:
            if line_tmp[idx] == line_tmp[idx + 1]:
                line_tmp[idx] *= 2
                self.score += line_tmp[idx]
                line_tmp[idx + 1] = 0
                idx += 1
            idx += 1

        line_tmp = [num for num in line_tmp if num != 0]
        return line_tmp + [0] * (len(line) - len(line_tmp))

    # 从右往左合并相同数字
    def __merge_line_right(self, line) -> list:
        line_tmp = [num for num in line if num != 0]
        idx = len(line_tmp) - 1
        while idx - 1 >= 0 and line_tmp[idx - 1] != 0:
            if line_tmp[idx] == line_tmp[idx - 1]:
                line_tmp[idx] *= 2
                self.score += line_tmp[idx]
                line_tmp[idx - 1] = 0
                idx -= 1
            idx -= 1

        line_tmp = [num for num in line_tmp if num != 0]
        return [0] * (len(line) - len(line_tmp)) + line_tmp

    def __move_up(self) -> list:
        nums_t = self.__transpose(self.nums)
        nums_t = [self.__merge_line_left(line) for line in nums_t]
        return self.__transpose(nums_t)

    def __move_down(self) -> list:
        nums_t = self.__transpose(self.nums)
        nums_t = [self.__merge_line_right(line) for line in nums_t]
        return self.__transpose(nums_t)

    def __move_left(self) -> list:
        return [self.__merge_line_left(line) for line in self.nums]

    def __move_right(self) -> list:
        return [self.__merge_line_right(line) for line in self.nums]

    def __move(self, direction: str):
        pre_nums = self.nums

        if direction == "up":
            self.nums = self.__move_up()
        elif direction == "down":
            self.nums = self.__move_down()
        elif direction == "left":
            self.nums = self.__move_left()
        elif direction == "right":
            self.nums = self.__move_right()

        if self.nums != pre_nums:
            # 如果可以移动，才生成随机数
            self.__random_generate()

    def __draw_board(self):
        for row, line in enumerate(self.nums):
            for col, _ in enumerate(line):
                x = self.margin_size * (col + 1) + self.block_size * col
                y = self.margin_size * (row + 1) + self.block_size * row
                pygame.draw.rect(self.screen, self.block_color, (x, y, self.block_size, self.block_size))

    def __draw_num(self):
        for row, line in enumerate(self.nums):
            for col, num in enumerate(line):
                if num == 0:
                    continue

                x = self.margin_size * (col + 1) + self.block_size * col
                y = self.margin_size * (row + 1) + self.block_size * row

                content = str(num)
                if content not in self.font_size_mapping:
                    self.font_size_mapping[content] = get_font_adaptive(content, self.block_size, self.block_size)
                font = self.font_size_mapping[content]
                text = font.render(content, True, NUM_COLOR_MAPPING[num])
                text_rect = text.get_rect()
                text_rect.center = (x + self.block_size // 2, y + self.block_size // 2)
                self.screen.blit(text, text_rect)

    def __draw_score(self):
        texts = (
            ("按上下左右方向键", "microsoftyahei", self.text_color),
            ("按q键结束游戏", "microsoftyahei", self.text_color),
            (f"score: {self.score}", "timesnewroman", self.score_color),
        )

        for idx, (content, font_name, color) in enumerate(texts):
            if content not in self.font_size_mapping:
                self.font_size_mapping[content] = get_font_adaptive(
                    content,
                    self.text_area_size,
                    self.height // (len(texts) + 1),
                    font_name=font_name
                )
            font = self.font_size_mapping[content]
            text = font.render(content, True, color)
            rect = text.get_rect()
            rect.center = ((self.block_width + self.width) // 2, self.height // (len(texts) + 1) * (idx + 1))
            self.screen.blit(text, rect)

    def __can_move(self) -> bool:
        if self.__move_up() != self.nums:
            return True
        if self.__move_down() != self.nums:
            return True
        if self.__move_left() != self.nums:
            return True
        if self.__move_right() != self.nums:
            return True
        return False

    def __run_game(self):
        clock = pygame.time.Clock()
        while self.in_game:
            self.screen.fill(self.bg_color)

            self.__draw_board()
            self.__draw_num()
            self.__draw_score()

            if self.game_over:
                self.shade_down()
                content = "游戏结束!按q键退出游戏,按r键重新游戏!"
                font = get_font_adaptive(content, self.width // 10 * 9, self.height, font_name="microsoftyahei")
                text = font.render(content, True, (255, 0, 0))
                rect = text.get_rect()
                rect.center = (self.width // 2, self.height // 2)
                self.screen.blit(text, rect)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.in_game = False
                        elif event.key == pygame.K_r:
                            self.start()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.in_game = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.in_game = False
                        elif event.key in DIRECTION_MAPPING:
                            self.__move(DIRECTION_MAPPING[event.key])
                            score = self.score
                            # 如果按了方向键且不能移动了，游戏结束
                            if not self.__can_move():
                                self.game_over = True
                            self.score = score

            pygame.display.update()
            clock.tick(60)

    def shade_down(self):
        for color in [
            self.bg_color,
            self.text_color,
            self.score_color,
            self.block_color,
        ]:
            color += 1
            np.clip(color, 0, 255, out=color)

        for num in NUM_COLOR_MAPPING:
            NUM_COLOR_MAPPING[num] += 1
            np.clip(NUM_COLOR_MAPPING[num], 0, 255, out=NUM_COLOR_MAPPING[num])
