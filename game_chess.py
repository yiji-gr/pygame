import random
from copy import deepcopy
from typing import Optional

import numpy as np
import pygame

from chess.piece import *
from game_base import Game
from utils import get_font_adaptive


class GameChess(Game):
    def __init__(self, config_path: str):
        super(GameChess, self).__init__(config_path)

        self.screen = pygame.display.set_mode((self.width, self.height))

        self.player: str = random.choice(["red", "black"])

        self.font_size_mapping: dict[str, pygame.font.FontType] = {}
        self.font_size = 0

    def _read_cfg(self):
        self.block_size = self.config["BLOCK_SIZE"]
        self.tb_margin = self.block_size // 2
        self.lr_margin = self.block_size // 2
        self.width = self.lr_margin * 2 + self.block_size * 8
        self.height = self.tb_margin * 2 + self.block_size * 9

    def _init_state(self):
        self.pieces: dict[str, list[PIECE]] = {
            "red": deepcopy(RED_PIECES),
            "black": deepcopy(BLACK_PIECES),
        }

        self.piece = self.pieces[self.player]

        self.piece_rect: dict[PIECE, pygame.rect.RectType] = {}

        self.bg_color = np.random.randint(200, 255, 3)
        self.line_color = np.random.randint(0, 100, 3)
        self.force_color = np.random.randint(0, 100, 3)
        self.tip_color = np.random.randint(100, 200, 3)

        self.in_game = True
        self.game_over = False
        self.pre_real_pos = (-1, -1)  # 上一次鼠标点击或者移动的位置
        self.cur_real_pos = (-1, -1)  # 当前鼠标点击或者移动的位置，鼠标不移动时不会触发鼠标事件，所以需要记录当前鼠标位置
        self.clicked_piece: Optional[PIECE | None] = None  # 点击的棋子

    def _run(self):
        clock = pygame.time.Clock()
        while self.in_game:
            self.screen.fill(self.bg_color)
            if self.game_over:
                self.__show_game_over()
                self.__handle_event1()
            else:
                if self.clicked_piece:
                    self.__show_hint()

                self.__handle_event2()
                self.pre_real_pos = self.cur_real_pos

                # 鼠标停留在棋子上时，突出棋子
                cur_piece = self.__is_piece(self.pre_real_pos)
                if cur_piece:
                    pygame.draw.circle(self.screen, self.force_color, self.__get_real_pos(cur_piece.pos),
                                       self.font_size // 3 * 2, 1)

            self.__draw_boards()
            self.__draw_pieces()

            pygame.display.update()
            clock.tick(60)

    def __show_game_over(self):
        content = "游戏结束!"
        font = get_font_adaptive(
            content,
            self.width // 2,
            self.height // 2,
            font_name="microsoftyahei",
        )
        text = font.render(content, True, RED)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

    def __handle_event1(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.in_game = False

    def __show_hint(self):
        pygame.draw.circle(
            self.screen,
            self.force_color,
            self.__get_real_pos(self.clicked_piece.pos),
            self.font_size // 3 * 2,
            1
        )

        for x, y in self.clicked_piece.move_candidates(self.piece):
            pygame.draw.circle(self.screen, self.tip_color, self.__get_real_pos((x, y)), 10)

    def __handle_event2(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.in_game = False

            if event.type == pygame.MOUSEMOTION:
                self.cur_real_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.cur_real_pos = pygame.mouse.get_pos()

                cur_piece = self.__is_piece(self.cur_real_pos)
                # 已经选中棋子
                if self.clicked_piece:
                    # 重复点击同一个棋子，取消点击
                    if cur_piece == self.clicked_piece:
                        self.clicked_piece = None
                    # 如果选中的棋子与上一个棋子是同阵营的，替换选中棋子
                    elif cur_piece and cur_piece.color == self.clicked_piece.color:
                        self.clicked_piece = cur_piece
                    else:
                        # 当前鼠标点击位置的索引
                        x, y = self.__get_idx_pos(self.cur_real_pos)
                        # 如果被选中的棋子可以走到当前点击位置
                        if (x, y) in self.clicked_piece.move_candidates(self.piece):
                            if cur_piece:
                                if cur_piece.name in ("将", "帅"):
                                    self.game_over = True
                                self.piece.remove(cur_piece)
                                self.piece_rect.pop(cur_piece)

                            # 更新被选中的棋子的位置
                            self.clicked_piece.pos = (x, y)
                            # 取消棋子选中
                            self.clicked_piece = None

                # 没有选中棋子
                else:
                    self.clicked_piece = cur_piece

    def __is_piece(self, mouse_pos: tuple[int, int]) -> Optional[PIECE | None]:
        for piece, rect in self.piece_rect.items():
            if rect.collidepoint(mouse_pos):
                return piece
        return None

    # 鼠标点击位置对应到棋盘上的索引
    def __get_idx_pos(self, mouse_pos: tuple[int, int]) -> tuple[int, int]:
        for x in range(9):
            for y in range(10):
                real_x = x * self.block_size + self.lr_margin
                real_y = y * self.block_size + self.tb_margin
                if real_x - self.font_size // 2 <= mouse_pos[0] <= real_x + self.font_size // 2:
                    if real_y - self.font_size // 2 <= mouse_pos[1] <= real_y + self.font_size // 2:
                        return x, y
        return -1, -1

    # 棋盘索引实际对应在图上的坐标
    def __get_real_pos(self, pos: tuple[int, int]) -> tuple[int, int]:
        return (
            self.lr_margin + self.block_size * pos[0],
            self.tb_margin + self.block_size * pos[1],
        )

    def __draw_piece(self, piece: PIECE):
        name = piece.name
        if name not in self.font_size_mapping:
            self.font_size_mapping[name], font_size = get_font_adaptive(
                name,
                self.block_size,
                self.block_size,
                font_name="microsoftyahei",
                ret_font_size=True
            )
            self.font_size = max(font_size, self.font_size)

        font = self.font_size_mapping[name]
        text = font.render(name, True, piece.color)
        text_rect = text.get_rect(center=self.__get_real_pos(piece.pos))
        self.screen.blit(text, text_rect)

        self.piece_rect[piece] = text_rect

    def __draw_pieces(self):
        for piece in self.piece:
            self.__draw_piece(piece)

    def __draw_boards(self):
        for row in range(5):
            start_pos = (self.lr_margin, self.tb_margin + self.block_size * row)
            end_pos = (self.lr_margin + self.block_size * 8, self.tb_margin + self.block_size * row)
            pygame.draw.line(self.screen, self.line_color, start_pos, end_pos, 1)
        for row in range(5):
            start_pos = (self.lr_margin, self.tb_margin + self.block_size * (row + 5))
            end_pos = (self.lr_margin + self.block_size * 8, self.tb_margin + self.block_size * (row + 5))
            pygame.draw.line(self.screen, self.line_color, start_pos, end_pos, 1)

        for col in range(1, 8):
            start_pos = (self.lr_margin + self.block_size * col, self.tb_margin)
            end_pos = (self.lr_margin + self.block_size * col, self.tb_margin + self.block_size * 4)
            pygame.draw.line(self.screen, self.line_color, start_pos, end_pos, 1)
        for col in range(1, 8):
            start_pos = (self.lr_margin + self.block_size * col, self.tb_margin + self.block_size * 5)
            end_pos = (self.lr_margin + self.block_size * col, self.tb_margin + self.block_size * 9)
            pygame.draw.line(self.screen, self.line_color, start_pos, end_pos, 1)

        for start_pos, end_pos in (
            ((self.lr_margin, self.tb_margin), (self.lr_margin, self.tb_margin + self.block_size * 9)),
            ((self.lr_margin + self.block_size * 8, self.tb_margin),
             (self.lr_margin + self.block_size * 8, self.tb_margin + self.block_size * 9)),
            ((self.lr_margin + self.block_size * 3, self.tb_margin),
             (self.lr_margin + self.block_size * 5, self.tb_margin + self.block_size * 2)),
            ((self.lr_margin + self.block_size * 5, self.tb_margin),
             (self.lr_margin + self.block_size * 3, self.tb_margin + self.block_size * 2)),
            ((self.lr_margin + self.block_size * 3, self.tb_margin + self.block_size * 7),
             (self.lr_margin + self.block_size * 5, self.tb_margin + self.block_size * 9)),
            ((self.lr_margin + self.block_size * 5, self.tb_margin + self.block_size * 7),
             (self.lr_margin + self.block_size * 3, self.tb_margin + self.block_size * 9))
        ):
            pygame.draw.line(self.screen, self.line_color, start_pos, end_pos, 1)
