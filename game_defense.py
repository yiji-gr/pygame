import numpy as np
import pygame.display

from game_base import Game
from tower_defense.enemy import EnemySprite
from tower_defense.hero import HeroSprite
from tower_defense.map import map0_1, path0_1
from utils import WHITE, RED, BLUE


# todo 增加敌方血量以及攻击展示
class GameDefense(Game):
    def __init__(self, config_path: str):
        super(GameDefense, self).__init__(config_path)

        self.screen = pygame.display.set_mode((self.width, self.height))

    def _read_cfg(self):
        self.map = map0_1
        self.path = path0_1

        self.row_num = len(self.map)
        self.col_num = len(self.map[0])

        self.margin_size = self.config["MARGIN_SIZE"]
        self.block_size = self.config["BLOCK_SIZE"]

        self.width, self.height = self.__get_real_pos((self.row_num, self.col_num))

        self.start_pos = self.find(4)
        self.end_pos = self.find(3)

    def _init_state(self):
        self.pause = False
        self.in_game = True

        self.block_color = np.random.randint(0, 50, 3)
        self.floor_color = np.random.randint(50, 100, 3)
        self.air_color = np.random.randint(100, 150, 3)

        self.enemy_group = pygame.sprite.Group()
        self.hero_group = pygame.sprite.Group()

    def find(self, target: int):
        for row in range(self.row_num):
            for col in range(self.col_num):
                if self.map[row][col] == target:
                    return row, col
        raise ValueError(f"{target} not in self.map")

    def _run(self):
        clock = pygame.time.Clock()
        self.__gen_enemy()
        while self.in_game:
            self.screen.fill(WHITE)

            self.__handle_event()

            self.__draw_map()

            self.enemy_group.draw(self.screen)
            self.hero_group.draw(self.screen)

            self.__attack()

            if not self.pause:
                self.enemy_group.update()

            pygame.display.flip()
            clock.tick(60)

    def __gen_enemy(self):
        enemy_sprite = EnemySprite(
            self.config,
            self.path,
        )
        self.enemy_group.add(enemy_sprite)

    def __gen_hero(self, pos: tuple[int, int]):
        hero_sprite = HeroSprite(self.config, self.__get_real_pos(pos))
        self.hero_group.add(hero_sprite)

    def __handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.in_game = False
                elif event.key == pygame.K_p:
                    self.pause = not self.pause
                elif event.key == pygame.K_g:
                    self.__gen_enemy()

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = self.__get_idx_pos(pygame.mouse.get_pos())
                if self.map[row][col] == 1:
                    self.__gen_hero((row, col))
                elif self.map[row][col] == 4:
                    self.__gen_enemy()

    def __attack(self):
        for hero_sprite in self.hero_group:
            for enemy_sprite in self.enemy_group:
                if self.__get_idx_pos(enemy_sprite.rect.bottomright) in hero_sprite.attack_range:
                    enemy_sprite.kill()

    # 忽略了margin
    def __get_idx_pos(self, real_pos: tuple[int, int]) -> tuple[int, int]:
        real_row, real_col = real_pos
        return real_col // self.block_size, real_row // self.block_size

    def __get_real_pos(self, idx_pos: tuple[int, int]) -> tuple[int, int]:
        row, col = idx_pos
        return col * self.block_size + (col - 1) * self.margin_size, \
            row * self.block_size + (row - 1) * self.margin_size

    def __draw_map(self):
        for row in range(self.row_num):
            for col in range(self.col_num):
                x, y = self.__get_real_pos((row, col))
                if self.map[row][col] == 0:
                    pygame.draw.rect(self.screen, self.block_color, (x, y, self.block_size, self.block_size))
                elif self.map[row][col] == 1:
                    pygame.draw.rect(self.screen, self.floor_color, (x, y, self.block_size, self.block_size))
                elif self.map[row][col] == 2:
                    pygame.draw.rect(self.screen, self.air_color, (x, y, self.block_size, self.block_size))
                elif self.map[row][col] == 3:
                    pygame.draw.rect(self.screen, BLUE, (x, y, self.block_size, self.block_size))
                elif self.map[row][col] == 4:
                    pygame.draw.rect(self.screen, RED, (x, y, self.block_size, self.block_size))
