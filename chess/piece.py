from utils import RED, BLACK


class PIECE:
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int], name: str):
        self.color = color
        self.name = name
        self.pos = pos

    def move_candidates(self, pieces: list) -> list[tuple[int, int]]:
        raise NotImplemented

    @staticmethod
    def is_piece(pieces: list["PIECE"], pos):
        for piece in pieces:
            if pos == piece.pos:
                return piece
        return None

    def __str__(self):
        return f"name: {self.name}, pos: {self.pos}, color: {self.color}"


class CHE(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int]):
        super(CHE, self).__init__(color, pos, "车")

    def _move(self, pieces: list[PIECE], stop: tuple[int, int, int], mode: str = "updown"):
        candidates = []
        for nxt in range(*stop):
            if mode != "updown":
                x, y = nxt, self.pos[1]
            else:
                x, y = self.pos[0], nxt
            if self.is_piece(pieces, (x, y)):
                candidates.append((x, y))
                break
            candidates.append((x, y))
        return candidates

    def move_candidates(self, pieces: list[PIECE]) -> list[tuple[int, int]]:
        candidates = []
        candidates.extend(self._move(pieces, (self.pos[0] - 1, -1, -1), ""))
        candidates.extend(self._move(pieces, (self.pos[0] + 1, 9, 1), ""))
        candidates.extend(self._move(pieces, (self.pos[1] - 1, -1, -1)))
        candidates.extend(self._move(pieces, (self.pos[1] + 1, 10, 1)))
        return candidates


class MA(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int]):
        super(MA, self).__init__(color, pos, "马")

    def move_candidates(self, pieces: list[PIECE]) -> list[tuple[int, int]]:
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
        for block, values in nx_pos.items():
            if 0 <= block[0] <= 8 and 0 <= block[1] <= 9 and self.is_piece(pieces, block):
                continue
            for nx, ny in values:
                if nx < 0 or ny < 0 or nx > 8 or ny > 9:
                    continue
                candidates.append((nx, ny))

        return candidates


class XIANG(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int], name: str):
        super(XIANG, self).__init__(color, pos, name)
        self.is_top = pos[1] < 5

    def move_candidates(self, pieces: list[PIECE]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]

        nx_pos = {
            (x - 1, y - 1): (x - 2, y - 2),
            (x + 1, y - 1): (x + 2, y - 2),
            (x - 1, y + 1): (x - 2, y + 2),
            (x + 1, y + 1): (x + 2, y + 2),
        }
        for block, nxt in nx_pos.items():
            if 0 <= block[0] <= 8 and 0 <= block[1] <= 9 and self.is_piece(pieces, block):
                continue
            nx, ny = nxt
            if nx < 0 or ny < 0 or nx > 8 or ny > 9:
                continue
            if not self.is_top and ny < 5:
                continue
            if self.is_top and ny > 4:
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

    def move_candidates(self, pieces: list[PIECE]) -> list[tuple[int, int]]:
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

    def move_candidates(self, pieces: list[PIECE]) -> list[tuple[int, int]]:
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

    def _move1(self, pieces: list[PIECE], stop: tuple[int, int, int], mode: str = "updown"):
        candidates = []
        for nxt in range(*stop):
            if mode != "updown":
                x, y = nxt, self.pos[1]
            else:
                x, y = self.pos[0], nxt
            if self.is_piece(pieces, (x, y)):
                break
            candidates.append((x, y))
        return candidates

    def _move2(self, pieces: list[PIECE], stop: tuple[int, int, int], mode: str = "updown"):
        candidates = []
        find = False
        for nxt in range(*stop):
            if mode != "updown":
                x, y = nxt, self.pos[1]
            else:
                x, y = self.pos[0], nxt
            if self.is_piece(pieces, (x, y)):
                if not find:
                    find = True
                else:
                    if self.is_piece(pieces, (x, y)).color != self.color:
                        candidates.append((x, y))
                        break
        return candidates

    def move_candidates(self, pieces: list[PIECE]) -> list[tuple[int, int]]:
        candidates = []
        candidates.extend(self._move1(pieces, (self.pos[0] - 1, -1, -1), ""))
        candidates.extend(self._move1(pieces, (self.pos[0] + 1, 9, 1), ""))
        candidates.extend(self._move1(pieces, (self.pos[1] - 1, -1, -1)))
        candidates.extend(self._move1(pieces, (self.pos[1] + 1, 10, 1)))
        candidates.extend(self._move2(pieces, (self.pos[0] - 1, -1, -1), ""))
        candidates.extend(self._move2(pieces, (self.pos[0] + 1, 9, 1), ""))
        candidates.extend(self._move2(pieces, (self.pos[1] - 1, -1, -1)))
        candidates.extend(self._move2(pieces, (self.pos[1] + 1, 10, 1)))
        return candidates


class BING(PIECE):
    def __init__(self, color: tuple[int, int, int], pos: tuple[int, int], name: str):
        super(BING, self).__init__(color, pos, name)
        self.y_step = 1 if pos[1] < 5 else -1

    def move_candidates(self, pieces: list[PIECE]) -> list[tuple[int, int]]:
        candidates = []
        x = self.pos[0]
        y = self.pos[1]

        nx_pos = [(x, y + self.y_step)]
        if (self.y_step == 1 and y > 4) or (self.y_step == -1 and y < 5):
            nx_pos.extend([
                (x - 1, y),
                (x + 1, y),
            ])
        for nx, ny in nx_pos:
            if nx < 0 or ny < 0 or nx > 8 or ny > 9:
                continue
            candidates.append((nx, ny))
        return candidates


BLACK_PIECES = [
    CHE(RED, (0, 0)),
    MA(RED, (1, 0)),
    XIANG(RED, (2, 0), "相"),
    SHI(RED, (3, 0), "仕"),
    JIANG(RED, (4, 0), "帅"),
    SHI(RED, (5, 0), "仕"),
    XIANG(RED, (6, 0), "相"),
    MA(RED, (7, 0)),
    CHE(RED, (8, 0)),
    PAO(RED, (1, 2)),
    PAO(RED, (7, 2)),
    BING(RED, (0, 3), "兵"),
    BING(RED, (2, 3), "兵"),
    BING(RED, (4, 3), "兵"),
    BING(RED, (6, 3), "兵"),
    BING(RED, (8, 3), "兵"),
    CHE(BLACK, (0, 9)),
    MA(BLACK, (1, 9)),
    XIANG(BLACK, (2, 9), "象"),
    SHI(BLACK, (3, 9), "士"),
    JIANG(BLACK, (4, 9), "将"),
    SHI(BLACK, (5, 9), "士"),
    XIANG(BLACK, (6, 9), "象"),
    MA(BLACK, (7, 9)),
    CHE(BLACK, (8, 9)),
    PAO(BLACK, (1, 7)),
    PAO(BLACK, (7, 7)),
    BING(BLACK, (0, 6), "卒"),
    BING(BLACK, (2, 6), "卒"),
    BING(BLACK, (4, 6), "卒"),
    BING(BLACK, (6, 6), "卒"),
    BING(BLACK, (8, 6), "卒"),
]

RED_PIECES: list[PIECE] = [
    CHE(BLACK, (0, 0)),
    MA(BLACK, (1, 0)),
    XIANG(BLACK, (2, 0), "象"),
    SHI(BLACK, (3, 0), "士"),
    JIANG(BLACK, (4, 0), "将"),
    SHI(BLACK, (5, 0), "士"),
    XIANG(BLACK, (6, 0), "象"),
    MA(BLACK, (7, 0)),
    CHE(BLACK, (8, 0)),
    PAO(BLACK, (1, 2)),
    PAO(BLACK, (7, 2)),
    BING(BLACK, (0, 3), "卒"),
    BING(BLACK, (2, 3), "卒"),
    BING(BLACK, (4, 3), "卒"),
    BING(BLACK, (6, 3), "卒"),
    BING(BLACK, (8, 3), "卒"),
    CHE(RED, (0, 9)),
    MA(RED, (1, 9)),
    XIANG(RED, (2, 9), "相"),
    SHI(RED, (3, 9), "仕"),
    JIANG(RED, (4, 9), "帅"),
    SHI(RED, (5, 9), "仕"),
    XIANG(RED, (6, 9), "相"),
    MA(RED, (7, 9)),
    CHE(RED, (8, 9)),
    PAO(RED, (1, 7)),
    PAO(RED, (7, 7)),
    BING(RED, (0, 6), "兵"),
    BING(RED, (2, 6), "兵"),
    BING(RED, (4, 6), "兵"),
    BING(RED, (6, 6), "兵"),
    BING(RED, (8, 6), "兵"),
]
