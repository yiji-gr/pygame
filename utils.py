import sys

import pygame


RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def exit_program():
    pygame.quit()
    sys.exit()


def handle_base_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_program()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                exit_program()


def get_font(font_name="timesnewroman", font_size=10) -> pygame.font.FontType:
    return pygame.font.SysFont(font_name, font_size)


def get_font_adaptive(
    content: str,
    width_lim: int,
    height_lim: int,
    font_name="timesnewroman",
    font_size=100,
    ret_font_size=False,
):
    font = get_font(font_name=font_name, font_size=font_size)
    while font.size(content)[0] > width_lim or font.size(content)[1] > height_lim:
        font_size -= 5
        font = get_font(font_name=font_name, font_size=font_size)
    if ret_font_size:
        return font, font_size
    return font
