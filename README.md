# Caro AI — Minimax & Alpha-Beta Pruning

Game Cờ Caro giữa người và máy tính, sử dụng thuật toán **Minimax** và **Alpha-Beta Pruning**.  
Giao diện đồ họa Pygame, bàn cờ 9×9, thắng khi có **4 quân liên tiếp**.

---

## Cài đặt

```bash
pip install -r requirements.txt
```

---

## Chạy chương trình

```bash
cd source_code
python main.py
```

Chọn:
- **1** → Mở cửa sổ game Pygame
- **2** → Chạy benchmark so sánh Minimax vs Alpha-Beta

---

## Cấu trúc source_code/

| File | Mô tả |
|------|-------|
| `board.py` | Bàn cờ, luật chơi, kiểm tra thắng/hòa, sinh nước đi |
| `evaluator.py` | Hàm đánh giá trạng thái bàn cờ |
| `ai.py` | Thuật toán Minimax và Alpha-Beta Pruning |
| `ui.py` | Giao diện đồ họa Pygame |
| `benchmark.py` | So sánh hai thuật toán trên 6 trạng thái kiểm thử |
| `main.py` | Điểm khởi động chương trình |

---

## Hướng dẫn chơi

- **Click vào ô** trên bàn cờ để đánh quân (bạn là **X**, máy là **O**)
- **Ván Mới** → bắt đầu lại
- **Minimax / Alpha-Beta** → chọn thuật toán AI
- **D=1…D=4** → chọn độ sâu tìm kiếm (D=3 khuyến nghị)
- Console in kết quả AI sau mỗi lượt: nước đi, giá trị, số trạng thái đã xét, thời gian

---

## Luật chơi

- Bàn cờ 9×9, hai người thay nhau đánh.
- **Thắng**: có **4 quân liên tiếp** theo hàng ngang, dọc hoặc chéo.
- **Hòa**: bàn cờ đầy, không ai thắng.
- Không áp dụng luật chặn hai đầu.
