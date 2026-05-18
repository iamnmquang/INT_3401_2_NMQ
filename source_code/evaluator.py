"""
evaluator.py - Hàm đánh giá trạng thái bàn cờ Caro
"""

from board import EMPTY, PLAYER, AI, WIN_LENGTH, DIRECTIONS

# ===== Điểm số cho các tình huống =====
SCORE_WIN      =  1_000_000   # Thắng
SCORE_LOSE     = -1_000_000   # Thua

# Điểm cho chuỗi quân của AI
SCORE_AI = {
    4: 1_000_000,   # 4 quân liên tiếp = thắng
    3: 5_000,       # 3 quân, 2 đầu mở
    3.5: 1_000,     # 3 quân, 1 đầu mở
    2: 100,         # 2 quân, 2 đầu mở
    2.5: 20,        # 2 quân, 1 đầu mở
    1: 5,
}

# Điểm cho chuỗi quân của NGƯỜI (âm = nguy hiểm)
SCORE_PLAYER = {
    4: -1_000_000,
    3: -8_000,      # Ưu tiên chặn hơn tấn công
    3.5: -2_000,
    2: -150,
    2.5: -30,
    1: -5,
}


def score_line(count, open_ends, is_ai):
    """
    Chuyển đổi (count, open_ends) thành điểm số.
    count: số quân liên tiếp
    open_ends: số đầu còn mở (0, 1, 2)
    is_ai: True nếu là quân AI
    """
    table = SCORE_AI if is_ai else SCORE_PLAYER

    if count >= WIN_LENGTH:
        return table[4]

    if count == 3:
        if open_ends == 2:
            return table[3]
        elif open_ends == 1:
            return table[3.5]

    if count == 2:
        if open_ends == 2:
            return table[2]
        elif open_ends == 1:
            return table[2.5]

    if count == 1 and open_ends > 0:
        return table[1]

    return 0


def evaluate_position(board, row, col, player):
    """Đánh giá điểm cho một ô cụ thể."""
    total = 0
    is_ai = (player == AI)
    for dr, dc in DIRECTIONS:
        count, open_ends = board.get_line_score(row, col, dr, dc, player)
        total += score_line(count, open_ends, is_ai)
    return total


def evaluate_board(board):
    """
    Hàm đánh giá tổng thể bàn cờ.
    Dương = có lợi cho AI, Âm = có lợi cho người chơi.
    """
    winner = board.check_winner()
    if winner == AI:
        return SCORE_WIN
    if winner == PLAYER:
        return SCORE_LOSE

    total_score = 0

    for r in range(board.size):
        for c in range(board.size):
            cell = board.grid[r][c]
            if cell == EMPTY:
                continue
            is_ai = (cell == AI)
            for dr, dc in DIRECTIONS:
                count, open_ends = board.get_line_score(r, c, dr, dc, cell)
                total_score += score_line(count, open_ends, is_ai)

    return total_score


def sort_moves(board, moves, maximizing):
    """
    Sắp xếp nước đi theo heuristic để Alpha-Beta cắt nhánh hiệu quả hơn.
    Đặt nước đi tiềm năng nhất lên đầu.
    """
    def move_priority(move):
        r, c = move
        score = 0
        # Kiểm tra nước thắng ngay
        board.grid[r][c] = AI if maximizing else PLAYER
        winner = board.check_winner()
        if winner == AI:
            score = 2_000_000
        elif winner == PLAYER:
            score = -2_000_000
        board.grid[r][c] = EMPTY

        # Cộng điểm từ evaluate
        board.grid[r][c] = AI if maximizing else PLAYER
        score += evaluate_board(board)
        board.grid[r][c] = EMPTY
        return score

    return sorted(moves, key=move_priority, reverse=maximizing)
