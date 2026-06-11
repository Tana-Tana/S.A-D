"""
Sinh tap du lieu hanh vi nguoi dung: data_user500.csv

500 user x 8 hanh vi (behaviors) lien tiep theo thoi gian.
Cac cot: user_id, product_id, action, timestamp
  - action: view | click | add_to_cart

Moi user duoc gan mot "persona" (browser / researcher / buyer) quyet dinh
xu huong hanh dong, va mot nhom san pham yeu thich (category) de tao ra
pattern co the hoc duoc cho cac model RNN/LSTM/biLSTM.
"""

import csv
import os
import random
from datetime import datetime, timedelta

NUM_USERS = 500
SEQ_LEN = 8
NUM_PRODUCTS = 17  # khop voi so san pham da seed trong product-service
ACTIONS = ['view', 'click', 'add_to_cart']

# (ten_persona, [p_view, p_click, p_add_to_cart], ti_le_xuat_hien)
PERSONAS = {
    'browser':    [0.80, 0.15, 0.05],
    'researcher': [0.35, 0.45, 0.20],
    'buyer':      [0.15, 0.30, 0.55],
}
PERSONA_WEIGHTS = [0.5, 0.3, 0.2]

# Cac nhom san pham (category) theo product_id da seed:
# 1-8: electronics, 9-13: books, 14-17: fashion
CATEGORY_RANGES = [(1, 8), (9, 13), (14, 17)]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data_user500.csv')


def generate_rows(seed: int = 42):
    rng = random.Random(seed)
    base_time = datetime(2026, 1, 1)
    rows = []

    for user_id in range(1, NUM_USERS + 1):
        persona = rng.choices(list(PERSONAS.keys()), weights=PERSONA_WEIGHTS)[0]
        base_probs = PERSONAS[persona]
        cat_start, cat_end = rng.choice(CATEGORY_RANGES)

        ts = base_time + timedelta(
            days=rng.randint(0, 150), hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
        )

        for step in range(SEQ_LEN):
            # Hieu ung "funnel": cang ve cuoi chuoi, xac suat add_to_cart cang tang
            shift = step / (SEQ_LEN - 1)
            adj = [
                base_probs[0] * (1 - 0.5 * shift),
                base_probs[1],
                base_probs[2] * (1 + 1.0 * shift),
            ]
            total = sum(adj)
            adj = [p / total for p in adj]
            action = rng.choices(ACTIONS, weights=adj)[0]

            # 90% chon san pham trong category yeu thich, 10% kham pha ngau nhien
            if rng.random() < 0.90:
                product_id = rng.randint(cat_start, cat_end)
            else:
                product_id = rng.randint(1, NUM_PRODUCTS)

            rows.append([user_id, product_id, action, ts.strftime('%Y-%m-%d %H:%M:%S')])
            ts += timedelta(minutes=rng.randint(1, 30))

    return rows


def main():
    rows = generate_rows()
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'product_id', 'action', 'timestamp'])
        writer.writerows(rows)

    print(f"Da sinh {len(rows)} dong ({NUM_USERS} user x {SEQ_LEN} behaviors) -> {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
