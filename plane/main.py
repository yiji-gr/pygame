import random
import sys

import numpy as np
import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600
REAL_WIDTH = 1000

FONT_NAME = random.choice(pygame.font.get_fonts())

BG_IMG_PATH = "bg.jfif"

PLAYER_STEP = 2
PLAYER_IMG_PATH = "player.jpg"

ENEMY_MAX_NUM = 30
ENEMY_INIT_NUM = 5
ENEMY_X_STEPS = (3, 5)
ENEMY_Y_STEPS = (5, 10)
ENEMY_IMG_PATH = "enemy.jpg"

BULLET_MAX_NUM = 60
BULLET_STEP = 5
BULLET_IMG_PATH = "bullet.jfif"

TIP_COLOR1 = np.random.randint(0, 100, 3)
TIP_COLOR2 = np.random.randint(0, 100, 3)
TIP_COLOR3 = np.random.randint(0, 100, 3)

enemy_spawn_num = 0
hit_num = 0


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, img_path, tlx, tly, step):
        super(PlayerSprite, self).__init__()
        self.image = pygame.image.load(img_path).convert()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (tlx, tly)
        self.step = step
        self.last_key_time = pygame.time.get_ticks()

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.step
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.step

        self.rect.x = max(self.rect.x, 0)
        self.rect.x = min(self.rect.x, WIDTH - self.rect.width)

        current_time = pygame.time.get_ticks()
        if keys_pressed[pygame.K_s] and current_time - self.last_key_time > 200:
            bullet_sprite = BulletSprite(
                BULLET_IMG_PATH,
                self.rect.x + self.rect.width / 2,
                self.rect.y,
                BULLET_STEP
            )
            bullet_group.add(bullet_sprite)
            self.last_key_time = current_time


class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, img_path, tlx, tly, x_steps, y_steps):
        super(EnemySprite, self).__init__()
        self.image = pygame.image.load(img_path).convert()
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (tlx, tly)
        self.x_step = random.randint(*x_steps) * random.choice([1, -1])
        self.y_step = random.randint(*y_steps)

    def update(self):
        self.rect.x += self.x_step
        if self.rect.x < 0:
            self.rect.x = 0
            self.x_step *= -1
            self.rect.y += self.y_step
        if self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width
            self.x_step *= -1
            self.rect.y += self.y_step


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, img_path, tlx, tly, step):
        super(BulletSprite, self).__init__()
        self.image = pygame.image.load(img_path).convert()
        self.image = pygame.transform.scale(self.image, (10, 30))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (tlx, tly)
        self.step = step

    def update(self):
        self.rect.y -= self.step
        if self.rect.y - self.rect.height < 0:
            bullet_group.remove(self)


def generate_player():
    p_group = pygame.sprite.Group()
    player = PlayerSprite(
        PLAYER_IMG_PATH,
        random.randint(WIDTH // 4 - 50, WIDTH // 4 + 50),
        HEIGHT - 120,
        PLAYER_STEP
    )
    p_group.add(player)
    return p_group


def generate_enemy():
    global enemy_spawn_num
    enemy_spawn_num += 1
    return EnemySprite(
        ENEMY_IMG_PATH,
        random.choice([WIDTH // 10, WIDTH // 10 * 9]),
        random.randint(HEIGHT // 10, HEIGHT // 6),
        ENEMY_X_STEPS,
        ENEMY_Y_STEPS
    )


def generate_enemies():
    e_group = pygame.sprite.Group()
    for _ in range(ENEMY_INIT_NUM):
        e_group.add(generate_enemy())

    return e_group


def get_font(font_size=10):
    return pygame.font.SysFont(FONT_NAME, font_size)


def show_victory():
    font = get_font(30)
    text = font.render("VICTORY!", True, pygame.Color(TIP_COLOR3))
    text_rect = text.get_rect()
    text_rect.center = ((WIDTH + REAL_WIDTH) // 2, 80)
    screen.blit(text, text_rect)


def show_tips():
    font = get_font(30)
    text = font.render(f"rest: {ENEMY_MAX_NUM - enemy_spawn_num}", True, pygame.Color(TIP_COLOR1))
    text_rect = text.get_rect()
    text_rect.center = ((WIDTH + REAL_WIDTH) // 2, 20)
    screen.blit(text, text_rect)

    text = font.render(f"hit: {hit_num}", True, pygame.Color(TIP_COLOR2))
    text_rect = text.get_rect()
    text_rect.center = ((WIDTH + REAL_WIDTH) // 2, 50)
    screen.blit(text, text_rect)


def exit_program():
    pygame.quit()
    sys.exit()


def handle_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            exit_program()


def show_bg():
    # 不加背景图片移动图片不刷新
    screen.blit(bg_img, (0, 0))
    screen.blit(tip_surface, (WIDTH, 0))


if __name__ == '__main__':
    screen = pygame.display.set_mode((REAL_WIDTH, HEIGHT))
    pygame.display.set_caption("plane")

    bg_img = pygame.image.load(BG_IMG_PATH)
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    tip_surface = pygame.Surface((REAL_WIDTH - WIDTH, HEIGHT))
    tip_surface.fill(np.random.randint(200, 255, 3))

    player_group = generate_player()
    enemy_group = generate_enemies()
    bullet_group = pygame.sprite.Group()

    clock = pygame.time.Clock()
    while True:
        handle_event()

        player_group.update(pygame.key.get_pressed())
        enemy_group.update()
        bullet_group.update()

        show_bg()
        show_tips()

        player_group.draw(screen)
        enemy_group.draw(screen)
        bullet_group.draw(screen)

        if pygame.sprite.groupcollide(enemy_group, bullet_group, True, True):
            hit_num += 1
            if hit_num + ENEMY_INIT_NUM <= ENEMY_MAX_NUM:
                enemy_group.add(generate_enemy())

        if hit_num == ENEMY_MAX_NUM:
            show_victory()

        pygame.display.flip()
        clock.tick(60)
