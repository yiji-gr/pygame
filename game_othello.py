import random

import numpy as np
import pygame

from game_base import Game
from utils import WHITE, BLACK, get_font_adaptive, RED


class GameOthello(Game):
    def __init__(self, config_path: str):
        super(GameOthello, self).__init__(config_path)

        self.screen = pygame.display.set_mode((self.width, self.height))

    def _read_cfg(self):
        self.row_num = self.config["ROW_NUM"]
        self.col_num = self.config["COL_NUM"]

        assert self.row_num % 2 == 0 and self.col_num % 2 == 0, "行列必须都设置为偶数"

        self.block_size = self.config["BLOCK_SIZE"]
        self.tip_width = self.config["TIP_WIDTH"]

        self.width = self.col_num * self.block_size + self.tip_width
        self.height = self.row_num * self.block_size

        self.font_size_mapping = {}

    def _init_state(self):
        self.in_game = True
        self.game_over = False
        self.show_tips = False

        self.bg_color = np.random.randint(200, 256, 3)
        self.hint_color = np.random.randint(0, 50, 3)
        self.tip_color = np.random.randint(0, 50, 3)

        self.board = [
            [0 for _ in range(self.col_num)]
            for _ in range(self.row_num)
        ]

        self.board[(self.row_num - 1) // 2][(self.col_num - 1) // 2] = 1
        self.board[(self.row_num - 1) // 2][self.col_num // 2] = -1
        self.board[self.row_num // 2][(self.col_num - 1) // 2] = -1
        self.board[self.row_num // 2][self.col_num // 2] = 1

        self.player = random.choice([-1, 1])
        self.player = -1

        self.piece_num: dict[int, int] = {
            1: 2,
            -1: 2,
        }

    def _run(self):
        clock = pygame.time.Clock()
        while self.in_game:
            self.screen.fill(self.bg_color)

            self.__draw_line()
            self.__draw_piece()
            self.__show_tip()

            if self.show_tips:
                self.__show_candidates()

            if self.game_over:
                self.__game_over()
            else:
                self.__handle_event()
                self.__is_over()

            pygame.display.flip()
            clock.tick(60)

    def __show_tip(self):
        contents = [
            "",
            f"black: {self.piece_num[1]}",
            f"white: {self.piece_num[-1]}",
        ]
        for idx, content in enumerate(contents):
            x, y = self.width - self.tip_width // 2, self.height // (len(contents) + 1) * (idx + 1)
            if idx == 0:
                color = BLACK if self.player == 1 else WHITE
                pygame.draw.circle(self.screen, color, (x, y), self.tip_width // 4)
                continue

            if content not in self.font_size_mapping:
                self.font_size_mapping[content] = get_font_adaptive(
                    content,
                    self.tip_width,
                    self.height // (len(contents) + 1),
                )
            font = self.font_size_mapping[content]
            text = font.render(content, True, self.tip_color)
            rect = text.get_rect(center=(x, y))
            self.screen.blit(text, rect)

    def __handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.in_game = False
                elif event.key == pygame.K_c:
                    self.show_tips = not self.show_tips

            if event.type == pygame.MOUSEBUTTONDOWN:
                col, row = self.__get_idx_pos(pygame.mouse.get_pos())
                if self.board[row][col] == 0 and self.__is_valid(col, row):
                    self.__flip(col, row)
                    self.board[row][col] = self.player
                    self.piece_num[self.player] += 1
                    self.player = -self.player

    def __is_over(self):
        if len(list(self.__get_valid_pos())) == 0:
            # 如果当前方无法行动，行动权给对方
            self.player = -self.player
            # 如果双方均无法行动，游戏结束
            if len(list(self.__get_valid_pos())) == 0:
                self.game_over = True

        if self.piece_num[1] + self.piece_num[-1] == self.row_num * self.col_num:
            # 如果棋盘满了，游戏结束
            self.game_over = True

    def __game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.in_game = False

        content = f"游戏结束!"
        if self.piece_num[1] > self.piece_num[-1]:
            content += f"黑子胜利!"
        elif self.piece_num[1] < self.piece_num[-1]:
            content += f"白子胜利!"
        else:
            content += f"平手!"

        font = get_font_adaptive(
            content,
            self.width,
            self.height // 2,
            font_name="microsoftyahei"
        )
        text = font.render(content, True, RED)
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, rect)

    def __show_candidates(self):
        for row, col in self.__get_valid_pos():
            x = col * self.block_size + self.block_size // 2
            y = row * self.block_size + self.block_size // 2
            pygame.draw.circle(self.screen, self.hint_color, (x, y), self.block_size // 4, 1)

    def __get_valid_pos(self):
        for row in range(self.row_num):
            for col in range(self.col_num):
                if self.board[row][col] != 0:
                    continue
                if self.__is_valid(col, row):
                    yield row, col

    def __is_valid(self, col: int, row: int) -> bool:
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if d_row == 0 and d_col == 0:
                    continue

                nx_row, nx_col = row + d_row, col + d_col
                if self.__is_out(nx_row, nx_col):
                    continue

                while self.board[nx_row][nx_col] == -self.player:
                    nx_row, nx_col = nx_row + d_row, nx_col + d_col

                    if self.__is_out(nx_row, nx_col):
                        break

                    if self.board[nx_row][nx_col] == self.player:
                        return True

        return False

    def __flip(self, col: int, row: int):
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if d_row == 0 and d_col == 0:
                    continue

                nx_row, nx_col = row + d_row, col + d_col
                if self.__is_out(nx_row, nx_col):
                    continue

                flipped = []
                while self.board[nx_row][nx_col] == -self.player:
                    flipped.append((nx_row, nx_col))

                    nx_row, nx_col = nx_row + d_row, nx_col + d_col

                    if self.__is_out(nx_row, nx_col):
                        break

                    if self.board[nx_row][nx_col] == self.player:
                        self.piece_num[self.player] += len(flipped)
                        self.piece_num[-self.player] -= len(flipped)
                        for x, y in flipped:
                            self.board[x][y] = self.player
                        break

    def __is_out(self, row: int, col: int) -> bool:
        return row < 0 or col < 0 or row >= self.row_num or col >= self.col_num

    def __get_idx_pos(self, mouse_pos: tuple[int, int]) -> tuple[int, int]:
        return (
            mouse_pos[0] // self.block_size,
            mouse_pos[1] // self.block_size,
        )

    def __draw_line(self):
        for row in range(0, self.row_num):
            y = row * self.block_size
            pygame.draw.line(self.screen, BLACK, (0, y), (self.width - self.tip_width, y))

        for col in range(0, self.col_num + 1):
            x = col * self.block_size
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, self.height))

    def __draw_piece(self):
        for row in range(self.row_num):
            for col in range(self.col_num):
                x = col * self.block_size + self.block_size // 2
                y = row * self.block_size + self.block_size // 2
                if self.board[row][col] == 1:
                    pygame.draw.circle(self.screen, BLACK, (x, y), self.block_size // 5 * 2)
                elif self.board[row][col] == -1:
                    pygame.draw.circle(self.screen, WHITE, (x, y), self.block_size // 5 * 2)
