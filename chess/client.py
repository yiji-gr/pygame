import socket
import threading

import pygame.time

from cfg import *
from object import *

pieces = [
    CHE(BLACK_COLOR, (0, 0)),
    MA(BLACK_COLOR, (1, 0)),
    XIANG(BLACK_COLOR, (2, 0), "象"),
    SHI(BLACK_COLOR, (3, 0), "士"),
    JIANG(BLACK_COLOR, (4, 0), "将"),
    SHI(BLACK_COLOR, (5, 0), "士"),
    XIANG(BLACK_COLOR, (6, 0), "象"),
    MA(BLACK_COLOR, (7, 0)),
    CHE(BLACK_COLOR, (8, 0)),
    PAO(BLACK_COLOR, (1, 2)),
    PAO(BLACK_COLOR, (7, 2)),
    ZU((0, 3)),
    ZU((2, 3)),
    ZU((4, 3)),
    ZU((6, 3)),
    ZU((8, 3)),
    CHE(RED_COLOR, (0, 9)),
    MA(RED_COLOR, (1, 9)),
    XIANG(RED_COLOR, (2, 9), "相"),
    SHI(RED_COLOR, (3, 9), "仕"),
    JIANG(RED_COLOR, (4, 9), "帅"),
    SHI(RED_COLOR, (5, 9), "仕"),
    XIANG(RED_COLOR, (6, 9), "相"),
    MA(RED_COLOR, (7, 9)),
    CHE(RED_COLOR, (8, 9)),
    PAO(RED_COLOR, (1, 7)),
    PAO(RED_COLOR, (7, 7)),
    BING((0, 6)),
    BING((2, 6)),
    BING((4, 6)),
    BING((6, 6)),
    BING((8, 6)),
]


def draw_boards():
    for row in range(5):
        start_pos = (LR_MARGIN, TB_MARGIN + BLOCK_SIZE * row)
        end_pos = (LR_MARGIN + BLOCK_SIZE * 8, TB_MARGIN + BLOCK_SIZE * row)
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 1)
    for row in range(5):
        start_pos = (LR_MARGIN, TB_MARGIN + BLOCK_SIZE * (row + 5))
        end_pos = (LR_MARGIN + BLOCK_SIZE * 8, TB_MARGIN + BLOCK_SIZE * (row + 5))
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 1)

    for col in range(1, 8):
        start_pos = (LR_MARGIN + BLOCK_SIZE * col, TB_MARGIN)
        end_pos = (LR_MARGIN + BLOCK_SIZE * col, TB_MARGIN + BLOCK_SIZE * 4)
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 1)
    for col in range(1, 8):
        start_pos = (LR_MARGIN + BLOCK_SIZE * col, TB_MARGIN + BLOCK_SIZE * 5)
        end_pos = (LR_MARGIN + BLOCK_SIZE * col, TB_MARGIN + BLOCK_SIZE * 9)
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 1)

    for start_pos, end_pos in (
        ((LR_MARGIN, TB_MARGIN), (LR_MARGIN, TB_MARGIN + BLOCK_SIZE * 9)),
        ((LR_MARGIN + BLOCK_SIZE * 8, TB_MARGIN), (LR_MARGIN + BLOCK_SIZE * 8, TB_MARGIN + BLOCK_SIZE * 9)),
        ((LR_MARGIN + BLOCK_SIZE * 3, TB_MARGIN), (LR_MARGIN + BLOCK_SIZE * 5, TB_MARGIN + BLOCK_SIZE * 2)),
        ((LR_MARGIN + BLOCK_SIZE * 5, TB_MARGIN), (LR_MARGIN + BLOCK_SIZE * 3, TB_MARGIN + BLOCK_SIZE * 2)),
        ((LR_MARGIN + BLOCK_SIZE * 3, TB_MARGIN + BLOCK_SIZE * 7), (LR_MARGIN + BLOCK_SIZE * 5, TB_MARGIN + BLOCK_SIZE * 9)),
        ((LR_MARGIN + BLOCK_SIZE * 5, TB_MARGIN + BLOCK_SIZE * 7), (LR_MARGIN + BLOCK_SIZE * 3, TB_MARGIN + BLOCK_SIZE * 9))
    ):
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 1)


def draw_pieces():
    for x in range(9):
        for y in range(10):
            if board[x][y]:
                piece = board[x][y]
                draw_piece(piece.name, piece.color, piece.real_pos)


def draw_piece(name: str, color: tuple[int, int, int], pos: tuple[int, int]):
    text = font.render(name, True, color)
    text_rect = text.get_rect(center=pos)
    screen.blit(text, text_rect)


def is_piece(mouse_pos: tuple[int, int]):
    for x in range(9):
        for y in range(10):
            if board[x][y] and board[x][y].pos == get_pos(mouse_pos):
                return board[x][y]
    return None


def get_pos(mouse_pos: tuple[int, int]):
    for x in range(9):
        for y in range(10):
            real_x = x * BLOCK_SIZE + LR_MARGIN
            real_y = y * BLOCK_SIZE + TB_MARGIN
            if (real_x - FONT_SIZE // 2 <= mouse_pos[0] <= real_x + FONT_SIZE // 2) and (real_y - FONT_SIZE // 2 <= mouse_pos[1] <= real_y + FONT_SIZE // 2):
                return x, y
    return -1, -1


def get_board() -> list[list[Optional[PIECE | None]]]:
    board_ = [[None for _ in range(10)] for _ in range(9)]
    for piece in pieces:
        board_[piece.pos[0]][piece.pos[1]] = piece
    return board_


def show_hint():
    pygame.draw.circle(screen, FORCE_COLOR, clicked_piece.real_pos, FONT_SIZE // 3 * 2, 1)
    for x, y in clicked_piece.move_candidates(board):
        real_x = x * BLOCK_SIZE + LR_MARGIN
        real_y = y * BLOCK_SIZE + TB_MARGIN
        pygame.draw.circle(screen, TIP_COLOR, (real_x, real_y), 10)


def show_game_over():
    text = font.render("游戏结束!", True, RED_COLOR)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - FONT_SIZE * 2))
    screen.blit(text, text_rect)


def handle_event1():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()


def handle_message():
    global cur_real_pos, clicked_piece, game_over, message
    try:
        x, y, t = message.split(",")
        cur_real_pos = (int(x), int(y))
        cur_piece_ = is_piece(cur_real_pos)

        # 点击棋子
        if t == "down":
            # 已经选中棋子
            if clicked_piece:
                # 重复点击同一个棋子，取消点击
                if cur_piece_ == clicked_piece:
                    clicked_piece = None
                # 如果选中的棋子与上一个棋子是同阵营的，替换选中棋子
                elif cur_piece_ and cur_piece_.color == clicked_piece.color:
                    clicked_piece = cur_piece_
                else:
                    # 如果棋子可以移动，移动棋子
                    can_move, game_over = clicked_piece.move(get_pos(cur_real_pos), board)
                    if can_move:
                        # 移动后，取消选中棋子
                        clicked_piece = None
            # 没有选中棋子
            else:
                clicked_piece = cur_piece_

        message = ""
    except ValueError as ex:
        print(f"ex: {ex}")


def handle_event2():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()

        # 鼠标移动到棋子时，突出棋子
        if event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            client_socket.sendall(f"{x},{y},move".encode())
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            client_socket.sendall(f"{x},{y},down".encode())


def receive_message(sock: socket.socket):
    while True:
        msg = sock.recv(1024)
        if msg:
            global message
            message = msg.decode()
            handle_message()


# TODO: 双方显示不同的界面，红色方红在下，黑色方黑在下
# TODO: 棋子选中效果不一样
# TODO: 当前选中棋子的候选位置对方不显示
# TODO: 双人对战单人演示代码合并
if __name__ == '__main__':
    client_socket = socket.socket()
    client_socket.connect((data["HOST"], data["PORT"]))

    receive_thread = threading.Thread(
        target=receive_message,
        args=(client_socket, ),
        daemon=True,
    )
    receive_thread.start()
    message: str = ""
    while True:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("中国象棋")
        board = get_board()
        font = pygame.font.SysFont("microsoftyahei", FONT_SIZE)
        clock = pygame.time.Clock()
        pre_real_pos = (-1, -1)     # 上一次鼠标点击或者移动的位置
        cur_real_pos = (-1, -1)     # 当前鼠标点击或者移动的位置，鼠标不移动时不会触发鼠标事件，所以需要记录当前鼠标位置
        clicked_piece: Optional[None | PIECE] = None        # 点击的棋子
        game_over = False
        while True:
            screen.fill(BG_COLOR)
            draw_boards()
            draw_pieces()

            if game_over:
                show_game_over()
                handle_event1()
            else:
                if clicked_piece:
                    show_hint()

                handle_event2()
                pre_real_pos = cur_real_pos

                # 鼠标停留在棋子上时，突出棋子
                cur_piece = is_piece(pre_real_pos)
                if cur_piece:
                    pygame.draw.circle(screen, FORCE_COLOR, cur_piece.real_pos, FONT_SIZE // 3 * 2, 1)

            pygame.display.update()
            clock.tick(60)
