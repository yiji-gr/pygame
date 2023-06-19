import numpy as np
import pygame

from game_base import Game
from plane.enemy import EnemySprite
from plane.player import PlayerSprite
from utils import get_font_adaptive


class GamePlane(Game):
    def __init__(self, config_path):
        super(GamePlane, self).__init__(config_path)
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.bg_img = pygame.image.load(self.config["BG_IMG_PATH"])
        self.bg_img = pygame.transform.scale(self.bg_img, (self.width - self.tip_width, self.height))

        self.tip_surface = pygame.Surface((self.tip_width, self.height))
        self.tip_surface.fill(np.random.randint(200, 256, 3))

    def _read_cfg(self):
        self.width = self.config["WIDTH"]
        self.height = self.config["HEIGHT"]
        self.tip_width = self.config["TIP_WIDTH"]

        self.enemy_max_num = self.config["ENEMY_MAX_NUM"]
        self.font_size_mapping: dict = {}

    def _init_state(self):
        self.in_game = True
        self.enemy_spawn_num = 0
        self.hit_num = 0

        self.tip_color = (
            np.random.randint(0, 100, 3),
            (255, 0, 0),
        )

        self.player_group = self.__generate_player()
        self.enemy_group = self.__generate_enemies()
        self.bullet_group = pygame.sprite.Group()

    def _run(self):
        clock = pygame.time.Clock()
        while self.in_game:
            self.__handle_event()

            self.screen.blit(self.bg_img, (0, 0))
            self.screen.blit(self.tip_surface, (self.width - self.tip_width, 0))

            self.player_group.update(pygame.key.get_pressed(), self.bullet_group)
            self.enemy_group.update()
            self.bullet_group.update(self.bullet_group)

            self.__show_tips()

            self.player_group.draw(self.screen)
            self.enemy_group.draw(self.screen)
            self.bullet_group.draw(self.screen)

            if pygame.sprite.groupcollide(self.enemy_group, self.bullet_group, True, True):
                self.hit_num += 1
                if self.hit_num + self.config["ENEMY_INIT_NUM"] <= self.enemy_max_num:
                    self.enemy_group.add(self.__generate_enemy())

            pygame.display.flip()
            clock.tick(60)

    def __generate_player(self) -> pygame.sprite.Group:
        player_group = pygame.sprite.Group()
        player = PlayerSprite(self.config)
        player_group.add(player)
        return player_group

    def __generate_enemy(self) -> EnemySprite:
        self.enemy_spawn_num += 1
        return EnemySprite(self.config, self.width - self.tip_width, self.height)

    def __generate_enemies(self) -> pygame.sprite.Group:
        enemy_group = pygame.sprite.Group()
        for _ in range(self.config["ENEMY_INIT_NUM"]):
            enemy_group.add(self.__generate_enemy())

        return enemy_group

    def __handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.in_game = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.in_game = False

    def __show_tips(self):
        contents = [
            "按左右方向键移动",
            "按s键发射子弹",
            f"剩余{self.enemy_max_num - self.enemy_spawn_num}个敌人",
            f"已击中{self.hit_num}个敌人",
            "胜利！"
        ]

        for idx, content in enumerate(contents):
            if content not in self.font_size_mapping:
                self.font_size_mapping[content] = get_font_adaptive(
                    content,
                    self.tip_width,
                    self.height // (len(contents) + 1),
                    font_name="microsoftyahei"
                )

            color = self.tip_color[0]
            if idx == len(contents) - 1:
                if self.hit_num != self.enemy_max_num:
                    continue
                else:
                    color = self.tip_color[1]

            font = self.font_size_mapping[content]
            text = font.render(content, True, color)
            rect = text.get_rect()
            rect.center = (self.width - self.tip_width // 2, self.height // (len(contents) + 1) * (idx + 1))
            self.screen.blit(text, rect)
