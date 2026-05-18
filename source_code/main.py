"""
main.py - Điểm khởi động chương trình Caro AI
"""

import sys


def main():
    print("=" * 50)
    print("  CARO AI — Minimax & Alpha-Beta Pruning")
    print("=" * 50)
    print("Chọn chế độ:")
    print("  1. Chơi game (giao diện Pygame)")
    print("  2. Chạy benchmark so sánh thuật toán")
    print("  3. Thoát")

    choice = input("\nNhập lựa chọn (1/2/3): ").strip()

    if choice == "1":
        from ui import GameUI
        game = GameUI()
        game.run()

    elif choice == "2":
        from benchmark import run_benchmark
        run_benchmark()

    elif choice == "3":
        print("Tạm biệt!")
        sys.exit(0)

    else:
        print("Lựa chọn không hợp lệ.")
        main()


if __name__ == "__main__":
    main()
