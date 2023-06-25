import random

import pygame.sprite


class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, config: dict, paths: list[list[tuple[int, int]]]):
        super(EnemySprite, self).__init__()

        self.config = config
        enemy_config = self.config["ENEMY"]

        self.margin_size = self.config["MARGIN_SIZE"]
        self.block_size = self.config["BLOCK_SIZE"]

        self.path: list[tuple[int, int]] = random.choice(paths)
        self.real_path = [self.__get_real_pos(path) for path in self.path]

        self.cur_idx_pos = self.real_path[0]
        del self.real_path[0]
        self.nxt_idx_pos = self.real_path[0]
        del self.real_path[0]

        self.image = pygame.image.load(enemy_config["IMG_PATH"]).convert()
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = self.cur_idx_pos

        self.step = 1

    def __get_real_pos(self, idx_pos: tuple[int, int]):
        return (idx_pos[1] + 0.5) * self.block_size + (idx_pos[1] - 1) * self.margin_size, \
            (idx_pos[0] + 0.5) * self.block_size + (idx_pos[0] - 1) * self.margin_size

    def update(self) -> None:
        cx, cy = self.cur_idx_pos
        nx, ny = self.nxt_idx_pos

        if cx < nx:
            cx += self.step
        elif cx > nx:
            cx -= self.step
        elif cy < ny:
            cy += self.step
        elif cy > ny:
            cy -= self.step

        self.rect.center = (cx, cy)

        if (cx, cy) == (nx, ny):
            if self.real_path:
                self.nxt_idx_pos = self.real_path[0]
                del self.real_path[0]
            else:
                self.kill()
                return

        self.cur_idx_pos = (cx, cy)
