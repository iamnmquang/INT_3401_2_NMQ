"""
ai.py - Thuật toán Minimax và Alpha-Beta pruning cho Caro AI
"""

import time
from board import PLAYER, AI, EMPTY
from evaluator import evaluate_board, sort_moves, SCORE_WIN, SCORE_LOSE

INF = float('inf')


class AIResult:
    """Lưu kết quả sau khi AI tính toán."""
    def __init__(self):
        self.best_move = None
        self.best_value = 0
        self.states_explored = 0
        self.elapsed_time = 0.0
        self.depth = 0
        self.algorithm = ""

    def __str__(self):
        return (
            f"[{self.algorithm}] Nước đi: {self.best_move} | "
            f"Giá trị: {self.best_value} | "
            f"Độ sâu: {self.depth} | "
            f"Trạng thái đã xét: {self.states_explored:,} | "
            f"Thời gian: {self.elapsed_time:.4f}s"
        )


# ============================================================
#  MINIMAX (không có Alpha-Beta)
# ============================================================

def minimax(board, depth, is_maximizing, counter):
    """
    Thuật toán Minimax đệ quy.
    
    Args:
        board: trạng thái bàn cờ hiện tại
        depth: độ sâu còn lại
        is_maximizing: True nếu đang tìm max (lượt AI)
        counter: dict chứa {'count': int} để đếm trạng thái
    
    Returns:
        (best_value, best_move)
    """
    counter['count'] += 1

    # Trạng thái kết thúc hoặc đạt độ sâu giới hạn
    if depth == 0 or board.is_terminal():
        return evaluate_board(board), None

    moves = board.get_candidate_moves()
    if not moves:
        return evaluate_board(board), None

    best_move = None

    if is_maximizing:
        best_value = -INF
        for r, c in moves:
            board.grid[r][c] = AI
            board.move_count += 1
            val, _ = minimax(board, depth - 1, False, counter)
            board.grid[r][c] = EMPTY
            board.move_count -= 1

            if val > best_value:
                best_value = val
                best_move = (r, c)
        return best_value, best_move

    else:  # minimizing
        best_value = INF
        for r, c in moves:
            board.grid[r][c] = PLAYER
            board.move_count += 1
            val, _ = minimax(board, depth - 1, True, counter)
            board.grid[r][c] = EMPTY
            board.move_count -= 1

            if val < best_value:
                best_value = val
                best_move = (r, c)
        return best_value, best_move


def minimax_decision(board, depth):
    """
    Gọi Minimax và trả về AIResult đầy đủ.
    """
    counter = {'count': 0}
    start = time.time()

    value, move = minimax(board, depth, True, counter)

    result = AIResult()
    result.best_move = move
    result.best_value = value
    result.states_explored = counter['count']
    result.elapsed_time = time.time() - start
    result.depth = depth
    result.algorithm = "Minimax"
    return result


# ============================================================
#  ALPHA-BETA PRUNING
# ============================================================

def alpha_beta(board, depth, alpha, beta, is_maximizing, counter):
    """
    Thuật toán Minimax với Alpha-Beta pruning.
    
    Args:
        board: trạng thái bàn cờ hiện tại
        depth: độ sâu còn lại
        alpha: giá trị tốt nhất hiện tại của MAX
        beta: giá trị tốt nhất hiện tại của MIN
        is_maximizing: True nếu đang tìm max (lượt AI)
        counter: dict chứa {'count': int} để đếm trạng thái
    
    Returns:
        (best_value, best_move)
    """
    counter['count'] += 1

    # Trạng thái kết thúc hoặc đạt độ sâu giới hạn
    if depth == 0 or board.is_terminal():
        return evaluate_board(board), None

    moves = board.get_candidate_moves()
    if not moves:
        return evaluate_board(board), None

    # Sắp xếp nước đi để tăng hiệu quả cắt nhánh
    moves = sort_moves(board, moves, is_maximizing)

    best_move = None

    if is_maximizing:
        best_value = -INF
        for r, c in moves:
            board.grid[r][c] = AI
            board.move_count += 1
            val, _ = alpha_beta(board, depth - 1, alpha, beta, False, counter)
            board.grid[r][c] = EMPTY
            board.move_count -= 1

            if val > best_value:
                best_value = val
                best_move = (r, c)

            alpha = max(alpha, best_value)
            if beta <= alpha:  # Cắt nhánh Beta
                break

        return best_value, best_move

    else:  # minimizing
        best_value = INF
        for r, c in moves:
            board.grid[r][c] = PLAYER
            board.move_count += 1
            val, _ = alpha_beta(board, depth - 1, alpha, beta, True, counter)
            board.grid[r][c] = EMPTY
            board.move_count -= 1

            if val < best_value:
                best_value = val
                best_move = (r, c)

            beta = min(beta, best_value)
            if beta <= alpha:  # Cắt nhánh Alpha
                break

        return best_value, best_move


def alphabeta_decision(board, depth):
    """
    Gọi Alpha-Beta và trả về AIResult đầy đủ.
    """
    counter = {'count': 0}
    start = time.time()

    value, move = alpha_beta(board, depth, -INF, INF, True, counter)

    result = AIResult()
    result.best_move = move
    result.best_value = value
    result.states_explored = counter['count']
    result.elapsed_time = time.time() - start
    result.depth = depth
    result.algorithm = "Alpha-Beta"
    return result


# ============================================================
#  INTERFACE CHUNG
# ============================================================

def get_ai_move(board, depth, use_alphabeta=True):
    """
    Hàm giao tiếp chính: lấy nước đi từ AI.
    
    Args:
        board: bàn cờ hiện tại
        depth: độ sâu tìm kiếm
        use_alphabeta: True dùng Alpha-Beta, False dùng Minimax thuần
    
    Returns:
        AIResult
    """
    if use_alphabeta:
        return alphabeta_decision(board, depth)
    else:
        return minimax_decision(board, depth)
