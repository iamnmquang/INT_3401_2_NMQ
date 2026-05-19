"""
ui.py - Giao diện đồ họa Pygame cho game Caro AI
"""

import pygame
import sys
import time

from board import Board, PLAYER, AI, EMPTY, BOARD_SIZE
from ai import get_ai_move

# ===== Màu sắc =====
C_BG         = (245, 225, 180)   # Nền bàn cờ (màu gỗ)
C_GRID       = (180, 140,  90)   # Đường kẻ
C_X          = ( 30,  80, 180)   # Màu X (người)
C_O          = (200,  50,  50)   # Màu O (máy)
C_HOVER      = (100, 200, 100, 80)
C_LAST_MOVE  = (255, 220,   0)   # Viền nước đi cuối
C_WIN_LINE   = (255,  60,  60)
C_TEXT       = ( 30,  30,  30)
C_PANEL      = ( 50,  50,  60)
C_PANEL_TXT  = (230, 230, 230)
C_BTN        = ( 80, 130, 190)
C_BTN_HOV    = (100, 160, 220)
C_BTN_ACT    = ( 50, 100, 160)
C_GREEN      = ( 50, 180,  80)
C_RED        = (200,  60,  60)
C_YELLOW     = (240, 180,  30)

# ===== Kích thước =====
CELL         = 56     # Kích thước ô
MARGIN       = 40     # Lề bàn cờ
PANEL_W      = 280    # Chiều rộng panel bên phải
BOARD_PIXEL  = BOARD_SIZE * CELL
WINDOW_W     = BOARD_PIXEL + MARGIN * 2 + PANEL_W
WINDOW_H     = BOARD_PIXEL + MARGIN * 2

FONT_S  = 14
FONT_M  = 17
FONT_L  = 22
FONT_XL = 28


class Button:
    def __init__(self, rect, text, font, color=C_BTN, hover=C_BTN_HOV, active=C_BTN_ACT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover
        self.active_color = active
        self.active = False

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse)
        col = self.active_color if self.active else (self.hover_color if hovered else self.color)
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=8)
        txt = self.font.render(self.text, True, C_PANEL_TXT)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class CellHighlight(pygame.sprite.Sprite):
    pass


class GameUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Caro AI — Minimax & Alpha-Beta")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_s  = pygame.font.SysFont("segoeui", FONT_S)
        self.font_m  = pygame.font.SysFont("segoeui", FONT_M)
        self.font_l  = pygame.font.SysFont("segoeui", FONT_L, bold=True)
        self.font_xl = pygame.font.SysFont("segoeui", FONT_XL, bold=True)

        self._init_game()
        self._init_buttons()

    # ----------------------------------------------------------
    def _init_game(self):
        self.board = Board(BOARD_SIZE)
        self.game_over = False
        self.winner = None
        self.current_player = PLAYER   # Người đi trước
        self.ai_depth = 3
        self.use_alphabeta = True
        self.ai_thinking = False
        self.last_result = None
        self.log_lines = []
        self.hover_cell = None
        self.win_cells = []

    def _init_buttons(self):
        px = BOARD_PIXEL + MARGIN * 2 + 10   # X bắt đầu của panel
        self.btn_new     = Button((px, 20,  PANEL_W - 20, 36), "Ván Mới", self.font_m)
        self.btn_mm      = Button((px, 390, PANEL_W - 20, 34), "Minimax", self.font_m)
        self.btn_ab      = Button((px, 430, PANEL_W - 20, 34), "Alpha-Beta", self.font_m)
        self.btn_d1      = Button((px, 490, 52, 32), "D=1", self.font_m)
        self.btn_d2      = Button((px + 58, 490, 52, 32), "D=2", self.font_m)
        self.btn_d3      = Button((px + 116, 490, 52, 32), "D=3", self.font_m)
        self.btn_d4      = Button((px + 174, 490, 52, 32), "D=4", self.font_m)

        # Trạng thái ban đầu
        self.btn_ab.active = True
        self.btn_d3.active = True
        self._depth_buttons = [self.btn_d1, self.btn_d2, self.btn_d3, self.btn_d4]

    # ----------------------------------------------------------
    #  VẼ BÀN CỜ
    # ----------------------------------------------------------
    def _board_origin(self):
        return MARGIN, MARGIN

    def _cell_to_pixel(self, row, col):
        ox, oy = self._board_origin()
        return ox + col * CELL + CELL // 2, oy + row * CELL + CELL // 2

    def _pixel_to_cell(self, x, y):
        ox, oy = self._board_origin()
        col = (x - ox) // CELL
        row = (y - oy) // CELL
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            # Kiểm tra gần tâm ô
            cx, cy = self._cell_to_pixel(row, col)
            if abs(x - cx) < CELL // 2 and abs(y - cy) < CELL // 2:
                return row, col
        return None, None

    def _draw_board(self):
        ox, oy = self._board_origin()
        board_px = BOARD_SIZE * CELL

        # Nền bàn cờ
        pygame.draw.rect(self.screen, C_BG,
                         (ox, oy, board_px, board_px))

        # Đường kẻ
        for i in range(BOARD_SIZE):
            x = ox + i * CELL + CELL // 2
            y = oy + i * CELL + CELL // 2
            pygame.draw.line(self.screen, C_GRID, (x, oy + CELL // 2), (x, oy + board_px - CELL // 2), 1)
            pygame.draw.line(self.screen, C_GRID, (ox + CELL // 2, y), (ox + board_px - CELL // 2, y), 1)

        # Viền bàn cờ
        pygame.draw.rect(self.screen, C_GRID,
                         (ox, oy, board_px, board_px), 2)

        # Số hàng / cột
        for i in range(BOARD_SIZE):
            x = ox + i * CELL + CELL // 2
            y = oy + i * CELL + CELL // 2
            lbl = self.font_s.render(str(i), True, (140, 100, 50))
            self.screen.blit(lbl, (x - lbl.get_width() // 2, oy - 18))
            self.screen.blit(lbl, (ox - 22, y - lbl.get_height() // 2))

    def _draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.board.grid[r][c]
                if cell == EMPTY:
                    continue
                cx, cy = self._cell_to_pixel(r, c)
                is_last = (self.board.last_move == (r, c))
                is_win  = (r, c) in self.win_cells

                # Quân cờ
                radius = CELL // 2 - 6
                color  = C_X if cell == PLAYER else C_O
                pygame.draw.circle(self.screen, color, (cx, cy), radius)

                # Viền nước đi cuối
                if is_last:
                    pygame.draw.circle(self.screen, C_LAST_MOVE, (cx, cy), radius + 3, 3)

                # Nổi bật nước thắng
                if is_win:
                    pygame.draw.circle(self.screen, (255, 255, 100), (cx, cy), radius + 4, 4)

                # Chữ X / O bên trong
                lbl = self.font_l.render("X" if cell == PLAYER else "O", True, (255, 255, 255))
                self.screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

    def _draw_hover(self):
        if self.hover_cell and not self.game_over and self.current_player == PLAYER:
            r, c = self.hover_cell
            if self.board.is_valid(r, c):
                cx, cy = self._cell_to_pixel(r, c)
                surf = pygame.Surface((CELL - 4, CELL - 4), pygame.SRCALPHA)
                surf.fill((80, 200, 80, 60))
                self.screen.blit(surf, (cx - CELL // 2 + 2, cy - CELL // 2 + 2))

    # ----------------------------------------------------------
    #  VẼ PANEL
    # ----------------------------------------------------------
    def _draw_panel(self):
        px = BOARD_PIXEL + MARGIN * 2
        # Nền panel
        pygame.draw.rect(self.screen, C_PANEL,
                         (px, 0, PANEL_W, WINDOW_H))

        x = px + 10
        # Tiêu đề
        t = self.font_xl.render("CARO AI", True, C_YELLOW)
        self.screen.blit(t, (px + PANEL_W // 2 - t.get_width() // 2, 65))

        # Trạng thái game
        if self.game_over:
            if self.winner == AI:
                msg, col = "Máy thắng! 🤖", C_RED
            elif self.winner == PLAYER:
                msg, col = "Bạn thắng! 🎉", C_GREEN
            else:
                msg, col = "Hòa! 🤝", C_YELLOW
        else:
            if self.ai_thinking:
                msg, col = "Máy đang suy nghĩ...", C_YELLOW
            elif self.current_player == PLAYER:
                msg, col = "Lượt của bạn (X)", C_GREEN
            else:
                msg, col = "Lượt của máy (O)", C_RED

        t = self.font_m.render(msg, True, col)
        self.screen.blit(t, (px + PANEL_W // 2 - t.get_width() // 2, 105))

        if self.game_over:
            hint = self.font_s.render("Nhấn Ván Mới để chơi lại", True, C_PANEL_TXT)
            self.screen.blit(hint, (px + PANEL_W // 2 - hint.get_width() // 2, 138))
            move_y = 168
        else:
            move_y = 140

        # Số nước đã đánh
        t = self.font_s.render(f"Số nước: {self.board.move_count}", True, C_PANEL_TXT)
        self.screen.blit(t, (x, move_y))

        # Thông tin AI
        algo = "Alpha-Beta" if self.use_alphabeta else "Minimax"
        t = self.font_s.render(f"Thuật toán: {algo}   Độ sâu: {self.ai_depth}", True, C_PANEL_TXT)
        self.screen.blit(t, (x, 162))

        # Kết quả lần chạy cuối
        self._draw_last_result(x, 190)

        # Log
        self._draw_log(x, px)

        # Labels
        t = self.font_m.render("Chọn thuật toán:", True, C_PANEL_TXT)
        self.screen.blit(t, (x, 370))
        t = self.font_m.render("Độ sâu:", True, C_PANEL_TXT)
        self.screen.blit(t, (x, 472))

        # Buttons
        self.btn_new.draw(self.screen)
        self.btn_mm.draw(self.screen)
        self.btn_ab.draw(self.screen)
        for b in self._depth_buttons:
            b.draw(self.screen)

    def _draw_last_result(self, x, y):
        if not self.last_result:
            return
        r = self.last_result
        lines = [
            f"Nước đi: {r.best_move}",
            f"Giá trị: {r.best_value:,}",
            f"Trạng thái xét: {r.states_explored:,}",
            f"Thời gian: {r.elapsed_time:.4f}s",
        ]
        for i, line in enumerate(lines):
            col = C_YELLOW if i == 0 else C_PANEL_TXT
            t = self.font_s.render(line, True, col)
            self.screen.blit(t, (x, y + i * 20))

    def _draw_log(self, x, px):
        # Tiêu đề log
        t = self.font_m.render("Lịch sử nước đi:", True, C_PANEL_TXT)
        self.screen.blit(t, (x, 290))

        # Vẽ log scroll từ dưới lên
        visible = 4
        start = max(0, len(self.log_lines) - visible)
        for i, line in enumerate(self.log_lines[start:]):
            t = self.font_s.render(line, True, (180, 200, 230))
            self.screen.blit(t, (x, 312 + i * 16))

    # ----------------------------------------------------------
    #  LOGIC
    # ----------------------------------------------------------
    def _find_win_cells(self, player):
        """Tìm các ô thuộc chuỗi thắng."""
        from board import DIRECTIONS, WIN_LENGTH
        cells = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board.grid[r][c] != player:
                    continue
                for dr, dc in DIRECTIONS:
                    line = [(r + i * dr, c + i * dc) for i in range(WIN_LENGTH)]
                    if all(0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and
                           self.board.grid[nr][nc] == player for nr, nc in line):
                        cells.extend(line)
        return list(set(cells))

    def _check_end(self, row, col, player):
        if self.board.check_win(row, col, player):
            self.game_over = True
            self.winner = player
            self.win_cells = self._find_win_cells(player)
        elif self.board.is_full():
            self.game_over = True
            self.winner = None

    def _player_move(self, row, col):
        if self.board.place(row, col, PLAYER):
            self.log_lines.append(f"Người: ({row},{col})")
            self._check_end(row, col, PLAYER)
            if not self.game_over:
                self.current_player = AI

    def _ai_move(self):
        self.ai_thinking = True
        self._render()  # Hiển thị trạng thái "đang suy nghĩ"

        result = get_ai_move(self.board, self.ai_depth, self.use_alphabeta)
        self.last_result = result

        if result.best_move:
            r, c = result.best_move
            self.board.place(r, c, AI)
            log = (f"Máy: ({r},{c}) | {result.states_explored:,} trạng thái | "
                   f"{result.elapsed_time:.3f}s")
            self.log_lines.append(log)
            print(result)  # In ra console
            self._check_end(r, c, AI)

        self.ai_thinking = False
        self.current_player = PLAYER

    # ----------------------------------------------------------
    #  VÒNG LẶP CHÍNH
    # ----------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                r, c = self._pixel_to_cell(*event.pos)
                self.hover_cell = (r, c) if r is not None else None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

        # Lượt AI (xử lý sau sự kiện để tránh block)
        if (not self.game_over and
                self.current_player == AI and
                not self.ai_thinking):
            self._ai_move()

    def _handle_click(self, pos):
        # Nút Ván Mới
        if self.btn_new.is_clicked(pos):
            self._init_game()
            self._init_buttons()
            return

        # Nút thuật toán
        if self.btn_mm.is_clicked(pos):
            self.use_alphabeta = False
            self.btn_mm.active = True
            self.btn_ab.active = False
            return
        if self.btn_ab.is_clicked(pos):
            self.use_alphabeta = True
            self.btn_ab.active = True
            self.btn_mm.active = False
            return

        # Nút độ sâu
        for i, btn in enumerate(self._depth_buttons):
            if btn.is_clicked(pos):
                self.ai_depth = i + 1
                for b in self._depth_buttons:
                    b.active = False
                btn.active = True
                return

        # Click lên bàn cờ
        if (not self.game_over and
                self.current_player == PLAYER and
                not self.ai_thinking):
            r, c = self._pixel_to_cell(*pos)
            if r is not None and self.board.is_valid(r, c):
                self._player_move(r, c)

    def _draw_board_message(self):
        if not self.game_over:
            return

        if self.winner == AI:
            msg = "Máy thắng! 🤖"
            color = C_RED
        elif self.winner == PLAYER:
            msg = "Bạn thắng! 🎉"
            color = C_GREEN
        else:
            msg = "Hòa! 🤝"
            color = C_YELLOW

        board_center = (MARGIN + BOARD_PIXEL // 2, MARGIN + BOARD_PIXEL // 2)
        overlay = pygame.Surface((BOARD_PIXEL - 32, 100), pygame.SRCALPHA)
        overlay.fill((20, 20, 20, 180))
        overlay_rect = overlay.get_rect(center=board_center)
        self.screen.blit(overlay, overlay_rect)

        title = self.font_xl.render(msg, True, color)
        hint = self.font_s.render("Nhấn Ván Mới để tiếp tục", True, C_PANEL_TXT)
        self.screen.blit(title, title.get_rect(center=(board_center[0], board_center[1] - 16)))
        self.screen.blit(hint, hint.get_rect(center=(board_center[0], board_center[1] + 28)))

    def _render(self):
        self.screen.fill((30, 30, 35))
        self._draw_board()
        self._draw_pieces()
        self._draw_hover()
        self._draw_board_message()
        self._draw_panel()
        pygame.display.flip()

    def run(self):
        print("=" * 60)
        print("  CARO AI — Minimax & Alpha-Beta Pruning")
        print("  Nhấn Ván Mới để bắt đầu, chọn thuật toán và độ sâu")
        print("=" * 60)

        while True:
            self._handle_events()
            self._render()
            self.clock.tick(60)
