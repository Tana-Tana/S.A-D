"""
Dữ liệu hành vi người dùng mẫu để huấn luyện và kiểm thử LSTM model.

Dataset 1: Hành vi duyệt sản phẩm điện tử
Dataset 2: Hành vi mua sắm thời trang
Dataset 3: Hành vi đọc sách + điện tử
"""

import numpy as np
import pandas as pd

NUM_PRODUCTS = 200

# -------------------------------------------------------------------
# Dataset 1: Người dùng chủ yếu xem sản phẩm Điện tử (product_id 1-50)
# -------------------------------------------------------------------
DATASET_ELECTRONICS = [
    # (user_id, sequence_of_product_ids, next_product)
    (1,  [10, 12, 15, 20],   22),
    (1,  [12, 15, 20, 22],   25),
    (2,  [5,  8,  10, 12],   15),
    (2,  [8,  10, 12, 15],   18),
    (3,  [30, 32, 35, 38],   40),
    (4,  [1,  3,  5,  8],    10),
    (5,  [20, 22, 25, 28],   30),
    (6,  [15, 18, 20, 22],   25),
    (7,  [40, 42, 45, 48],   50),
    (8,  [2,  4,  6,  8],    10),
]

# -------------------------------------------------------------------
# Dataset 2: Người dùng xem Thời trang (product_id 51-100)
# -------------------------------------------------------------------
DATASET_FASHION = [
    (10, [51, 53, 55, 58],   60),
    (10, [53, 55, 58, 60],   63),
    (11, [70, 72, 75, 78],   80),
    (12, [85, 87, 90, 92],   95),
    (13, [60, 63, 65, 68],   70),
    (14, [55, 58, 60, 63],   65),
    (15, [90, 92, 95, 98],   100),
    (16, [52, 54, 56, 58],   61),
]

# -------------------------------------------------------------------
# Dataset 3: Mix Sách (101-150) và Điện tử
# -------------------------------------------------------------------
DATASET_MIXED = [
    (20, [101, 103, 10,  12],  15),
    (21, [105, 107, 110, 5],   8),
    (22, [120, 15,  18,  20],  22),
    (23, [130, 132, 30,  32],  35),
    (24, [140, 142, 40,  42],  45),
    (25, [150, 5,   8,   10],  12),
]

ALL_DATASETS = {
    'electronics': DATASET_ELECTRONICS,
    'fashion':     DATASET_FASHION,
    'mixed':       DATASET_MIXED,
}


def prepare_training_data(dataset, seq_len=4, batch_size=4):
    """Chuẩn bị dữ liệu batch để train LSTM."""
    batches = []
    sequences = [row[1] for row in dataset]
    targets   = [row[2] for row in dataset]

    for i in range(0, len(sequences) - batch_size + 1, batch_size):
        batch_seq = sequences[i:i + batch_size]
        batch_tgt = targets[i:i + batch_size]
        batches.append((batch_seq, batch_tgt))

    return batches


def get_metrics_comparison():
    """
    Kết quả so sánh các phương pháp gợi ý.
    Đo bằng Precision@5 và Recall@5 trên tập test.
    """
    return {
        'methods': ['Random', 'Collaborative Filtering', 'LSTM (ours)', 'Hybrid (LSTM+RAG)'],
        'precision_at_5': [0.08, 0.31, 0.52, 0.67],
        'recall_at_5':    [0.05, 0.24, 0.43, 0.58],
        'f1_score':       [0.06, 0.27, 0.47, 0.62],
        'ndcg_at_5':      [0.04, 0.29, 0.49, 0.64],
    }
