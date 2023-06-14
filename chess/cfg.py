import numpy as np
import pygame
import yaml

with open("config.yaml") as f:
    data = yaml.safe_load(f)

pygame.init()

BLOCK_SIZE = 80
TB_MARGIN = BLOCK_SIZE // 2
LR_MARGIN = BLOCK_SIZE // 2
WIDTH = LR_MARGIN * 2 + BLOCK_SIZE * 8
HEIGHT = TB_MARGIN * 2 + BLOCK_SIZE * 9
FONT_SIZE = BLOCK_SIZE // 2

BG_COLOR = np.random.randint(200, 255, 3)
LINE_COLOR = np.random.randint(0, 100, 3)
FORCE_COLOR = np.random.randint(0, 100, 3)
TIP_COLOR = np.random.randint(100, 200, 3)
BLACK_COLOR = (0, 0, 0)
RED_COLOR = (255, 0, 0)
