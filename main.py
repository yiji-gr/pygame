import os

import numpy as np
import pygame

from game_2048 import Game2048
from game_maze import GameMaze
from game_plane import GamePlane
from game_chess import GameChess
from game_othello import GameOthello
from game_defense import GameDefense
from utils import exit_program

pygame.init()

os.environ["SDL_VIDEO_CENTERED"] = '1'

WIDTH = 800
HEIGHT = 600

BG_COLOR = np.random.randint(200, 256, 3)
FONT_COLOR = np.random.randint(0, 50, 3)
HIGHLIGHT_FONT_COLOR = np.random.randint(50, 150, 3)
FONT_SIZE = 50

font = pygame.font.SysFont("microsoftyahei", FONT_SIZE)

games = {
    "迷宫游戏": [GameMaze("config/game_maze.yaml"), ],
    "2048": [Game2048("config/game_2048.yaml"), ],
    "飞机大战": [GamePlane("config/game_plane.yaml"), ],
    "中国象棋": [GameChess("config/game_chess.yaml"), ],
    "黑白棋": [GameOthello("config/game_othello.yaml"), ],
    "塔防": [GameDefense("config/game_defense.yaml"), ],
}

for idx, (name, game) in enumerate(games.items()):
    text = font.render(name, True, FONT_COLOR)
    rect = text.get_rect(center=(WIDTH // 4 * (idx % 2 * 2 + 1), HEIGHT // ((len(games) + 1) // 2 + 1) * ((idx + 2) // 2)))
    games[name].append((text, rect))

clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

while True:
    pygame.display.set_caption("几个小游戏")
    screen.fill(BG_COLOR)

    for i, (_, (_, (text, rect))) in enumerate(games.items()):
        screen.blit(text, rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            exit_program()

        if event.type == pygame.MOUSEMOTION:
            for i, (name, (_, (text, rect))) in enumerate(games.items()):
                if rect.collidepoint(pygame.mouse.get_pos()):
                    text = font.render(name, True, HIGHLIGHT_FONT_COLOR)
                    screen.blit(text, rect)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, (name, (game, (_, rect))) in enumerate(games.items()):
                if not game:
                    continue
                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.display.set_caption(name)
                    screen = pygame.display.set_mode((game.width, game.height))
                    screen.get_rect()
                    game.start()
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.flip()
    clock.tick(60)
