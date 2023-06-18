import random

import pygame


class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, config: dict, width_lim: int, height_lim: int):
        super(EnemySprite, self).__init__()

        self.config = config
        self.width_lim = width_lim
        enemy_config = self.config["ENEMY"]

        self.image = pygame.image.load(enemy_config["IMG_PATH"]).convert()
        self.x_step = random.randint(*enemy_config["X_STEP"]) * random.choice([1, -1])
        self.y_step = random.randint(*enemy_config["Y_STEP"])

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (
            random.randint(width_lim // 10, width_lim // 10 * 9),
            random.randint(height_lim // 10, height_lim // 6),
        )

    def update(self):
        self.rect.x += self.x_step
        if self.rect.x < 0:
            self.rect.x = 0
            self.x_step *= -1
            self.rect.y += self.y_step
        if self.rect.x > self.width_lim - self.rect.width:
            self.rect.x = self.width_lim - self.rect.width
            self.x_step *= -1
            self.rect.y += self.y_step
