"""
board.py - Xử lý bàn cờ Caro, luật chơi và kiểm tra trạng thái kết thúc
"""

EMPTY = 0
PLAYER = 1   # X - người chơi
AI = 2       # O - máy tính

WIN_LENGTH = 4   # Số quân liên tiếp để thắng
BOARD_SIZE = 9   # Kích thước bàn cờ

# Bốn hướng kiểm tra: ngang, dọc, chéo xuống, chéo lên
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class Board:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        self.grid = [[EMPTY] * size for _ in range(size)]
        self.last_move = None
        self.move_count = 0

    def copy(self):
        """Tạo bản sao của bàn cờ."""
        new_board = Board(self.size)
        new_board.grid = [row[:] for row in self.grid]
        new_board.last_move = self.last_move
        new_board.move_count = self.move_count
        return new_board

    def is_valid(self, row, col):
        """Kiểm tra ô có hợp lệ và còn trống không."""
        return (0 <= row < self.size and
                0 <= col < self.size and
                self.grid[row][col] == EMPTY)

    def place(self, row, col, player):
        """Đặt quân vào ô (row, col)."""
        if self.is_valid(row, col):
            self.grid[row][col] = player
            self.last_move = (row, col)
            self.move_count += 1
            return True
        return False

    def count_consecutive(self, row, col, dr, dc, player):
        """Đếm số quân liên tiếp theo một hướng từ (row, col)."""
        count = 0
        r, c = row + dr, col + dc
        while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    def check_win(self, row, col, player):
        """Kiểm tra nước đi (row, col) của player có thắng không."""
        for dr, dc in DIRECTIONS:
            forward = self.count_consecutive(row, col, dr, dc, player)
            backward = self.count_consecutive(row, col, -dr, -dc, player)
            if forward + backward + 1 >= WIN_LENGTH:
                return True
        return False

    def check_winner(self):
        """Tìm người thắng trên toàn bàn cờ. Trả về PLAYER, AI hoặc None."""
        for r in range(self.size):
            for c in range(self.size):
                p = self.grid[r][c]
                if p != EMPTY and self.check_win(r, c, p):
                    return p
        return None

    def is_full(self):
        """Kiểm tra bàn cờ đầy chưa."""
        return self.move_count >= self.size * self.size

    def is_terminal(self):
        """Kiểm tra trạng thái kết thúc (thắng hoặc hòa)."""
        return self.check_winner() is not None or self.is_full()

    def get_candidate_moves(self, radius=2):
        """
        Sinh danh sách nước đi hợp lệ gần những quân đã đánh.
        Chỉ xét ô trong bán kính 'radius' quanh quân đã có.
        Nếu bàn cờ trống, trả về các ô gần trung tâm.
        """
        if self.move_count == 0:
            center = self.size // 2
            return [(center, center)]

        candidates = set()
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != EMPTY:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = r + dr, c + dc
                            if self.is_valid(nr, nc):
                                candidates.add((nr, nc))
        return list(candidates)

    def get_line_score(self, row, col, dr, dc, player):
        """
        Tính điểm cho một đoạn thẳng theo hướng (dr, dc) từ (row, col).
        Đếm quân liên tiếp hai chiều và ô còn mở.
        Trả về (count, open_ends).
        """
        opponent = PLAYER if player == AI else AI
        count = 1  # Tính ô hiện tại
        open_ends = 0

        for sign in [1, -1]:
            r, c = row + sign * dr, col + sign * dc
            while 0 <= r < self.size and 0 <= c < self.size:
                if self.grid[r][c] == player:
                    count += 1
                    r += sign * dr
                    c += sign * dc
                elif self.grid[r][c] == EMPTY:
                    open_ends += 1
                    break
                else:  # opponent
                    break
            else:
                pass  # Đụng biên không tính open end

        return count, open_ends

    def __str__(self):
        """Hiển thị bàn cờ dạng text."""
        symbols = {EMPTY: '.', PLAYER: 'X', AI: 'O'}
        header = '  ' + ' '.join(f'{c:2}' for c in range(self.size))
        lines = [header]
        for r in range(self.size):
            row_str = f'{r:2} ' + '  '.join(symbols[self.grid[r][c]] for c in range(self.size))
            lines.append(row_str)
        return '\n'.join(lines)
