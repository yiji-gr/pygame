import sys

from pygame import quit, font


def exit_program():
    quit()
    sys.exit()


def get_font(font_name="timesnewroman", font_size=10) -> font:
    return font.SysFont(font_name, font_size)


def get_font_adaptive(content: str, width_lim: int, height_lim: int, font_name="timesnewroman", font_size=100) -> font:
    font = get_font(font_name=font_name, font_size=font_size)
    while font.size(content)[0] > width_lim or font.size(content)[1] > height_lim:
        font_size -= 1
        font = get_font(font_name=font_name, font_size=font_size)
    return font
