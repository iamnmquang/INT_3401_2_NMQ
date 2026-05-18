"""
benchmark.py - So sánh Minimax vs Alpha-Beta trên nhiều trạng thái bàn cờ khác nhau

Chạy: python benchmark.py
Kết quả được in ra console và lưu vào benchmark_results.txt
"""

import time
from board import Board, PLAYER, AI, EMPTY, BOARD_SIZE
from ai import minimax_decision, alphabeta_decision

DEPTHS = [1, 2, 3]


# ============================================================
#  ĐỊNH NGHĨA CÁC TRẠNG THÁI KIỂM THỬ
# ============================================================

def make_board_from_moves(moves):
    """Tạo bàn cờ từ danh sách nước đi [(player, row, col), ...]."""
    board = Board(BOARD_SIZE)
    for player, r, c in moves:
        board.grid[r][c] = player
        board.move_count += 1
    return board


def state_empty():
    """Trạng thái 1: Bàn cờ gần trống (2 nước)."""
    board = Board(BOARD_SIZE)
    board.place(4, 4, PLAYER)
    board.place(4, 5, AI)
    return board


def state_midgame():
    """Trạng thái 2: Giữa ván, cả hai bên có 3-4 quân."""
    moves = [
        (PLAYER, 4, 4), (AI, 4, 5),
        (PLAYER, 3, 4), (AI, 5, 5),
        (PLAYER, 3, 3), (AI, 6, 5),
        (PLAYER, 5, 3), (AI, 3, 5),
    ]
    return make_board_from_moves(moves)


def state_ai_can_win():
    """Trạng thái 3: AI có 3 quân liên tiếp, có thể thắng ngay."""
    moves = [
        (AI, 4, 4), (PLAYER, 2, 2),
        (AI, 4, 5), (PLAYER, 2, 3),
        (AI, 4, 6), (PLAYER, 0, 0),
    ]
    return make_board_from_moves(moves)


def state_player_about_to_win():
    """Trạng thái 4: Người chơi có 3 quân liên tiếp, máy cần chặn."""
    moves = [
        (PLAYER, 3, 3), (AI, 0, 0),
        (PLAYER, 3, 4), (AI, 0, 1),
        (PLAYER, 3, 5), (AI, 0, 2),
    ]
    return make_board_from_moves(moves)


def state_mutual_attack():
    """Trạng thái 5: Cả hai bên đều có cơ hội tấn công."""
    moves = [
        (PLAYER, 4, 4), (AI, 4, 5),
        (PLAYER, 3, 3), (AI, 5, 6),
        (PLAYER, 2, 2), (AI, 6, 7),
        (PLAYER, 5, 5), (AI, 3, 4),
        (PLAYER, 6, 6), (AI, 2, 3),
    ]
    return make_board_from_moves(moves)


def state_many_moves():
    """Trạng thái 6: Nhiều quân rải rác, nhiều nước hợp lệ."""
    moves = [
        (PLAYER, 0, 0), (AI, 8, 8),
        (PLAYER, 0, 8), (AI, 8, 0),
        (PLAYER, 4, 4), (AI, 4, 3),
        (PLAYER, 3, 4), (AI, 5, 4),
        (PLAYER, 2, 6), (AI, 6, 2),
        (PLAYER, 1, 3), (AI, 7, 5),
    ]
    return make_board_from_moves(moves)


STATES = [
    ("State 1: Đầu ván (bàn gần trống)",            state_empty),
    ("State 2: Giữa ván",                            state_midgame),
    ("State 3: Máy có thể thắng ngay",               state_ai_can_win),
    ("State 4: Người chơi sắp thắng, cần chặn",     state_player_about_to_win),
    ("State 5: Hai bên đều có cơ hội",               state_mutual_attack),
    ("State 6: Nhiều nước đi hợp lệ",                state_many_moves),
]


# ============================================================
#  CHẠY BENCHMARK
# ============================================================

def run_benchmark():
    header = (f"{'Trạng thái':<45} {'Độ sâu':>6} {'Thuật toán':>12} "
              f"{'Nước đi':>10} {'Giá trị':>12} {'Trạng thái xét':>16} {'Thời gian (s)':>14}")
    sep = "-" * len(header)

    lines = [sep, header, sep]

    for name, state_fn in STATES:
        for depth in DEPTHS:
            board_mm = state_fn()
            board_ab = state_fn()

            r_mm = minimax_decision(board_mm, depth)
            r_ab = alphabeta_decision(board_ab, depth)

            same_move = "✓" if r_mm.best_move == r_ab.best_move else "✗"

            for r in [r_mm, r_ab]:
                line = (f"{name:<45} {r.depth:>6} {r.algorithm:>12} "
                        f"{str(r.best_move):>10} {r.best_value:>12,} "
                        f"{r.states_explored:>16,} {r.elapsed_time:>14.4f}")
                lines.append(line)

            # Thông tin so sánh
            if r_mm.states_explored > 0:
                reduction = (1 - r_ab.states_explored / r_mm.states_explored) * 100
                cmp_line = (f"  → Cùng nước đi: {same_move} | "
                            f"Alpha-Beta giảm {reduction:.1f}% trạng thái | "
                            f"Tăng tốc: {r_mm.elapsed_time / (r_ab.elapsed_time + 1e-9):.1f}x")
                lines.append(cmp_line)

        lines.append(sep)

    output = "\n".join(lines)
    print(output)

    with open("benchmark_results.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print("\n✓ Kết quả đã lưu vào benchmark_results.txt")


if __name__ == "__main__":
    print("Đang chạy benchmark Minimax vs Alpha-Beta...\n")
    run_benchmark()
