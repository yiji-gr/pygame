import os

import numpy as np
import pygame

from game_2048 import Game2048
from game_maze import GameMaze
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
    "飞机大战": [None, ],
    "中国象棋": [None, ],
}

for i, (name, game) in enumerate(games.items()):
    text = font.render(name, True, FONT_COLOR)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // (len(games) + 1) * (i + 1)))
    games[name].append((text, rect))

clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
while True:
    screen.fill(BG_COLOR)

    for i, (name, (game, (text, rect))) in enumerate(games.items()):
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
                    screen = pygame.display.set_mode((game.width, game.height))
                    screen.get_rect()
                    game.start()
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.flip()
    clock.tick(60)
