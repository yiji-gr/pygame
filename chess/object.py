from typing import Optional

from cfg import BLACK_COLOR, RED_COLOR, BLOCK_SIZE, LR_MARGIN, TB_MARGIN


class PIECE:
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int], name: str):
        self.color = color
        self.name = name
        self.pos = pos
        self.x = LR_MARGIN + BLOCK_SIZE * self.pos[0]
        self.y = TB_MARGIN + BLOCK_SIZE * self.pos[1]
        self.real_pos = (
            LR_MARGIN + BLOCK_SIZE * self.pos[0],
            TB_MARGIN + BLOCK_SIZE * self.pos[1],
        )

    def move_candidates(self, board: list) -> list[tuple[int, int]]:
        raise NotImplemented

    def move(self, click_pos: tuple[int, int], board: list):
        game_over = False
        if click_pos in self.move_candidates(board):
            # 上一个位置的棋盘置空
            if board[click_pos[0]][click_pos[1]] and board[click_pos[0]][click_pos[1]].name in ("将", "帅"):
                game_over = True
            board[self.pos[0]][self.pos[1]] = None
            # 将当前棋子放到点击的位置
            board[click_pos[0]][click_pos[1]] = self
            self.pos = click_pos
            self.real_pos = (
                LR_MARGIN + BLOCK_SIZE * self.pos[0],
                TB_MARGIN + BLOCK_SIZE * self.pos[1],
            )
            return True, game_over
        return False, game_over

    def __str__(self):
        return f"name: {self.name}, pos: {self.pos}, color: {self.color}"


class CHE(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int]):
        super(CHE, self).__init__(color, pos, "车")

    def _move(self, board: list[list[Optional[PIECE | None]]], stop: tuple[int, int, int], mode: str = "updown"):
        candidates = []
        for nxt in range(*stop):
            if mode != "updown":
                x, y = nxt, self.pos[1]
            else:
                x, y = self.pos[0], nxt
            if board[x][y]:
                candidates.append((x, y))
                break
            candidates.append((x, y))
        return candidates

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        candidates.extend(self._move(board, (self.pos[0] - 1, -1, -1), ""))
        candidates.extend(self._move(board, (self.pos[0] + 1, 9, 1), ""))
        candidates.extend(self._move(board, (self.pos[1] - 1, -1, -1)))
        candidates.extend(self._move(board, (self.pos[1] + 1, 10, 1)))
        return candidates


class MA(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int]):
        super(MA, self).__init__(color, pos, "马")

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]
        nx_pos = {
            (x - 1, y): [
                (x - 2, y - 1),
                (x - 2, y + 1),
            ],
            (x + 1, y): [
                (x + 2, y - 1),
                (x + 2, y + 1),
            ],
            (x, y - 1): [
                (x - 1, y - 2),
                (x + 1, y - 2),
            ],
            (x, y + 1): [
                (x - 1, y + 2),
                (x + 1, y + 2),
            ]
        }
        for key, values in nx_pos.items():
            if board[key[0]][key[1]]:
                continue
            for nx, ny in values:
                if nx < 0 or ny < 0 or nx > 8 or ny > 9:
                    continue
                candidates.append((nx, ny))

        return candidates


class XIANG(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int], name: str):
        super(XIANG, self).__init__(color, pos, name)

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]
        nx_pos = [
            (x - 2, y - 2),
            (x + 2, y - 2),
            (x - 2, y + 2),
            (x + 2, y + 2),
        ]
        for nx, ny in nx_pos:
            if nx < 0 or ny < 0 or nx > 8 or ny > 9:
                continue
            if self.color == RED_COLOR and ny < 5:
                continue
            if self.color == BLACK_COLOR and ny > 4:
                continue
            candidates.append((nx, ny))

        return candidates


class SHI(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int], name: str):
        super(SHI, self).__init__(color, pos, name)
        self.path = {
            (3, 0), (5, 0), (4, 1), (3, 2), (5, 2),
            (3, 7), (5, 7), (4, 8), (3, 9), (5, 9),
        }

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]
        nx_pos = [
            (x - 1, y - 1),
            (x + 1, y - 1),
            (x - 1, y + 1),
            (x + 1, y + 1),
        ]
        for nx, ny in nx_pos:
            if nx < 0 or ny < 0 or nx > 8 or ny > 9 or (nx, ny) not in self.path:
                continue
            candidates.append((nx, ny))
        return candidates


class JIANG(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int], name: str):
        super(JIANG, self).__init__(color, pos, name)
        self.path = {
            (3, 0), (4, 0), (5, 0),
            (3, 1), (4, 1), (5, 1),
            (3, 2), (4, 2), (5, 2),
            (3, 7), (4, 7), (5, 7),
            (3, 8), (4, 8), (5, 8),
            (3, 9), (4, 9), (5, 9),
        }

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]
        nx_pos = [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
        ]
        for nx, ny in nx_pos:
            if nx < 0 or ny < 0 or nx > 8 or ny > 9 or (nx, ny) not in self.path:
                continue
            candidates.append((nx, ny))
        return candidates


class PAO(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int]):
        super(PAO, self).__init__(color, pos, "炮")

    def _move1(self, board: list[list[Optional[PIECE | None]]], stop: tuple[int, int, int], mode: str = "updown"):
        candidates = []
        for nxt in range(*stop):
            if mode != "updown":
                x, y = nxt, self.pos[1]
            else:
                x, y = self.pos[0], nxt
            if board[x][y]:
                break
            candidates.append((x, y))
        return candidates

    def _move2(self, board: list[list[Optional[PIECE | None]]], stop: tuple[int, int, int], mode: str = "updown"):
        candidates = []
        find = False
        for nxt in range(*stop):
            if mode != "updown":
                x, y = nxt, self.pos[1]
            else:
                x, y = self.pos[0], nxt
            if board[x][y]:
                if not find:
                    find = True
                else:
                    if board[x][y].color != self.color:
                        candidates.append((x, y))
                        break
        return candidates

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        candidates.extend(self._move1(board, (self.pos[0] - 1, -1, -1), ""))
        candidates.extend(self._move1(board, (self.pos[0] + 1, 9, 1), ""))
        candidates.extend(self._move1(board, (self.pos[1] - 1, -1, -1)))
        candidates.extend(self._move1(board, (self.pos[1] + 1, 10, 1)))
        candidates.extend(self._move2(board, (self.pos[0] - 1, -1, -1), ""))
        candidates.extend(self._move2(board, (self.pos[0] + 1, 9, 1), ""))
        candidates.extend(self._move2(board, (self.pos[1] - 1, -1, -1)))
        candidates.extend(self._move2(board, (self.pos[1] + 1, 10, 1)))
        return candidates


class ZU(PIECE):
    def __init__(self, pos):
        super(ZU, self).__init__(BLACK_COLOR, pos, "卒")

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]
        nx_pos = [(x, y + 1)]
        if y > 4:
            nx_pos.extend([
                (x - 1, y),
                (x + 1, y),
            ])
        for nx, ny in nx_pos:
            if nx < 0 or ny < 0 or nx > 8 or ny > 9:
                continue
            candidates.append((nx, ny))
        return candidates


class BING(PIECE):
    def __init__(self, pos):
        super(BING, self).__init__(RED_COLOR, pos, "兵")

    def move_candidates(self, board: list[list[Optional[PIECE | None]]]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]
        nx_pos = [
            (x, y - 1),
        ]
        if y < 5:
            nx_pos.extend([
                (x - 1, y),
                (x + 1, y),
            ])
        for nx, ny in nx_pos:
            if nx < 0 or ny < 0 or nx > 8 or ny > 9:
                continue
            candidates.append((nx, ny))
        return candidates
