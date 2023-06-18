import pygame


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, config: dict, player_pos: tuple[int, int]):
        super(BulletSprite, self).__init__()

        self.config = config
        bullet_config = self.config["BULLET"]

        self.image = pygame.image.load(bullet_config["IMG_PATH"]).convert()
        self.image = pygame.transform.scale(self.image, (bullet_config["WIDTH"], bullet_config["HEIGHT"]))
        self.step = bullet_config["STEP"]

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.bottomleft = (
            player_pos[0] - bullet_config["WIDTH"] // 2,
            player_pos[1],
        )

    def update(self, bullet_group):
        self.rect.y -= self.step
        if self.rect.y - self.rect.height < 0:
            bullet_group.remove(self)


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, config: dict):
        super(PlayerSprite, self).__init__()
        self.config = config
        player_config = self.config["PLAYER"]

        self.image = pygame.image.load(player_config["IMG_PATH"]).convert()
        self.image = pygame.transform.scale(self.image, (player_config["WIDTH"], player_config["HEIGHT"]))
        self.step = player_config["STEP"]

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.bottomleft = (
            (self.config["WIDTH"] - self.config["TIP_WIDTH"] - player_config["WIDTH"]) // 2,
            self.config["HEIGHT"] - 10,
        )

        self.last_key_time = pygame.time.get_ticks()

    def update(self, keys_pressed, bullet_group):
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.rect.x -= self.step
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.rect.x += self.step

        self.rect.x = max(self.rect.x, 0)
        self.rect.x = min(self.rect.x, self.config["WIDTH"] - self.config["TIP_WIDTH"] - self.rect.width)

        current_time = pygame.time.get_ticks()
        if keys_pressed[pygame.K_s] and current_time - self.last_key_time > 200:
            if len(bullet_group) >= self.config["BULLET_MAX_NUM"]:
                return

            bullet_sprite = BulletSprite(self.config, (self.rect.x + self.rect.width / 2, self.rect.y))
            bullet_group.add(bullet_sprite)
            self.last_key_time = current_time
