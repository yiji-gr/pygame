import pygame
import sys
import random
import numpy as np

pygame.init()


BLOCK_COLOR = (np.random.randint(200, 256, 3))
BG_COLOR = np.random.randint(100, 256, 3)
SCORE_COLOR = np.random.randint(0, 200, 3)
ROW, COL = 8, 10
MARGIN_SIZE = 10
BLOCK_SIZE = 80
HEIGHT = ROW * BLOCK_SIZE + (ROW + 1) * MARGIN_SIZE
BLOCK_WIDTH = COL * BLOCK_SIZE + (COL + 1) * MARGIN_SIZE
WIDTH = BLOCK_WIDTH + 350
FONT_NAME = random.choice(pygame.font.get_fonts())

NUM_COLOR_MAPPING = {
    2**num: np.random.randint(0, 200, 3)
    for num in range(1, 30)
}

DIRECTION_MAPPING = {
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
}


def get_font(font_size=10):
    return pygame.font.SysFont(FONT_NAME, font_size)


def random_generate():
    pos = []
    for row, line in enumerate(nums):
        for col, num in enumerate(line):
            if num == 0:
                pos.append((row, col))

    row, col = random.choice(pos)
    nums[row][col] = random.choice([1024, 2048])


def exit():
    pygame.quit()
    sys.exit()


def draw_board():
    for row, line in enumerate(nums):
        for col, _ in enumerate(line):
            x = MARGIN_SIZE * (col + 1) + BLOCK_SIZE * col
            y = MARGIN_SIZE * (row + 1) + BLOCK_SIZE * row
            pygame.draw.rect(screen, pygame.Color(BLOCK_COLOR), (x, y, BLOCK_SIZE, BLOCK_SIZE))


def draw_num():
    for row, line in enumerate(nums):
        for col, num in enumerate(line):
            if num == 0:
                continue

            x = MARGIN_SIZE * (col + 1) + BLOCK_SIZE * col
            y = MARGIN_SIZE * (row + 1) + BLOCK_SIZE * row

            font = get_font(font_size=BLOCK_SIZE - 10*(1 + len(str(num))))
            text = font.render(str(num), True, pygame.Color(NUM_COLOR_MAPPING[num]))
            text_rect = text.get_rect()
            text_rect.center = (x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2)
            screen.blit(text, text_rect)


def draw_score():
    font = get_font(font_size=BLOCK_SIZE - 5*(len(str(score))))
    text = font.render(f"score: {score}", True, pygame.Color(SCORE_COLOR))
    rect = text.get_rect()
    rect.center = ((BLOCK_WIDTH + WIDTH) // 2, HEIGHT // 2)
    screen.blit(text, rect)


def transpose(nums_):
    nums_t = [[0 for _ in range(len(nums_))] for _ in range(len(nums_[0]))]
    for row, line in enumerate(nums_):
        for col, num in enumerate(line):
            nums_t[col][row] = num
    return nums_t


def merge_line_left(line):
    global score
    line_tmp = [num for num in line if num != 0]
    idx = 0
    while idx + 1 < len(line_tmp) and line_tmp[idx + 1] != 0:
        if line_tmp[idx] == line_tmp[idx + 1]:
            line_tmp[idx] *= 2
            score += line_tmp[idx]
            line_tmp[idx + 1] = 0
            idx += 1
        idx += 1

    line_tmp = [num for num in line_tmp if num != 0]
    return line_tmp + [0] * (len(line) - len(line_tmp))


def merge_line_right(line):
    global score
    line_tmp = [num for num in line if num != 0]
    idx = len(line_tmp) - 1
    while idx - 1 >= 0 and line_tmp[idx - 1] != 0:
        if line_tmp[idx] == line_tmp[idx - 1]:
            line_tmp[idx] *= 2
            score += line_tmp[idx]
            line_tmp[idx - 1] = 0
            idx -= 1
        idx -= 1

    line_tmp = [num for num in line_tmp if num != 0]
    return [0] * (len(line) - len(line_tmp)) + line_tmp


def move_up():
    nums_t = transpose(nums)
    nums_t = [merge_line_left(line) for line in nums_t]
    return transpose(nums_t)


def move_down():
    nums_t = transpose(nums)
    nums_t = [merge_line_right(line) for line in nums_t]
    return transpose(nums_t)


def move_left():
    return [merge_line_left(line) for line in nums]


def move_right():
    return [merge_line_right(line) for line in nums]


def check():
    if move_up() != nums:
        return False
    if move_down() != nums:
        return False
    if move_left() != nums:
        return False
    if move_right() != nums:
        return False
    return True


def move(direction):
    global nums
    pre_nums = nums

    if direction == "up":
        nums = move_up()
    elif direction == "down":
        nums = move_down()
    elif direction == "left":
        nums = move_left()
    elif direction == "right":
        nums = move_right()

    if nums != pre_nums:
        random_generate()


def run_game():
    while True:
        is_move = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                elif event.key in DIRECTION_MAPPING:
                    move(DIRECTION_MAPPING[event.key])
                    is_move = True

        screen.fill(pygame.Color(BG_COLOR))

        draw_board()
        draw_num()
        draw_score()

        pygame.display.update()
        if is_move and check():
            return
        clock.tick(60)


def game_over():
    font_color = (255, 255, 255)
    font_big = get_font(font_size = 60)
    font_small = get_font(font_size = 30)

    surface = screen.convert_alpha()
    surface.fill((127, 255, 212, 2))

    text = font_big.render('Game Over!', True, font_color)
    text_rect = text.get_rect()
    text_rect.centerx, text_rect.centery = WIDTH / 2, HEIGHT / 2 - 50
    surface.blit(text, text_rect)

    button_width, button_height = 100, 40
    button_start_x_left = WIDTH / 2 - button_width - 20
    button_start_y = HEIGHT / 2 - button_height / 2 + 20
    pygame.draw.rect(surface, (0, 255, 255), (button_start_x_left, button_start_y, button_width, button_height))
    button_start_x_right = WIDTH / 2 + 20
    pygame.draw.rect(surface, (0, 255, 255), (button_start_x_right, button_start_y, button_width, button_height))

    text_restart = font_small.render('Restart', True, font_color)
    text_restart_rect = text_restart.get_rect()
    text_restart_rect.centerx, text_restart_rect.centery = button_start_x_left + button_width / 2, button_start_y + button_height / 2
    surface.blit(text_restart, text_restart_rect)

    text_quit = font_small.render('Quit', True, font_color)
    text_quit_rect = text_quit.get_rect()
    text_quit_rect.centerx, text_quit_rect.centery = button_start_x_right + button_width / 2, button_start_y + button_height / 2
    surface.blit(text_quit, text_quit_rect)

    clock = pygame.time.Clock()
    while True:
        screen.blit(surface, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button:
                if text_quit_rect.collidepoint(pygame.mouse.get_pos()):
                    sys.exit()
                if text_restart_rect.collidepoint(pygame.mouse.get_pos()):
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()

        pygame.display.update()
        clock.tick(60)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
score = 0
clock = pygame.time.Clock()
while True:
    nums = [[0 for _ in range(COL)] for _ in range(ROW)]
    random_generate()
    run_game()
    game_over()
