import random

import numpy as np
import pygame.sprite


ATTACK_DISTANCE: list[tuple[int, int, int, int]] = list({
    # 上下左右
    tuple(np.random.randint(0, 2, 4))
    for _ in range(10)
})


class HeroSprite(pygame.sprite.Sprite):
    def __init__(self, config: dict, init_pos: tuple[int, int]):
        super(HeroSprite, self).__init__()

        self.config = config
        enemy_config = self.config["HERO"]

        self.block_size = self.config["BLOCK_SIZE"]

        print(f"init_pos: {init_pos}")

        self.image = pygame.image.load(enemy_config["IMG_PATH"]).convert()
        self.image = pygame.transform.scale(self.image, (self.block_size, self.block_size))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = init_pos

        self.attack_distance: tuple[int, int, int, int] = random.choice(ATTACK_DISTANCE)
        self.attack_range: list[tuple[int, int]] = self.__get_attack_range()

    def __get_idx_pos(self, real_pos: tuple[int, int]) -> tuple[int, int]:
        real_row, real_col = real_pos
        return real_col // self.block_size, real_row // self.block_size

    def __get_attack_range(self) -> list[tuple[int, int]]:
        cur_row, cur_col = self.__get_idx_pos(self.rect.topleft)
        attack_range = [(cur_row, cur_col)]

        for idx in range(1, self.attack_distance[0] + 1):
            attack_range.append((cur_row - idx, cur_col))

        for idx in range(1, self.attack_distance[1] + 1):
            attack_range.append((cur_row + idx, cur_col))

        for idx in range(1, self.attack_distance[2] + 1):
            attack_range.append((cur_row, cur_col - idx))

        for idx in range(1, self.attack_distance[3] + 1):
            attack_range.append((cur_row, cur_col + idx))

        return attack_range
