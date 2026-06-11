"""
LSTM Model cho dự đoán sản phẩm tiếp theo dựa trên chuỗi hành vi người dùng.

Kiến trúc:
  Embedding → LSTM (2 layers) → Dropout → Linear → Softmax

Input:  chuỗi product_id mà user đã tương tác (view/click/add-to-cart)
Output: top-K sản phẩm có xác suất cao nhất user sẽ tương tác tiếp
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict


class LSTMRecommender(nn.Module):
    def __init__(
        self,
        num_products: int,
        embed_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.num_products = num_products
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Embedding layer: ánh xạ product_id → vector
        self.embedding = nn.Embedding(num_products + 1, embed_dim, padding_idx=0)

        # LSTM: học phụ thuộc tuần tự trong chuỗi hành vi
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )

        self.dropout = nn.Dropout(dropout)

        # Output layer: dự đoán xác suất cho mỗi sản phẩm
        self.fc = nn.Linear(hidden_dim, num_products)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch_size, seq_len) — chuỗi product_id
        returns: (batch_size, num_products) — logits
        """
        embedded = self.embedding(x)           # (B, L, embed_dim)
        lstm_out, _ = self.lstm(embedded)      # (B, L, hidden_dim)
        last_hidden = lstm_out[:, -1, :]       # lấy hidden state cuối cùng
        out = self.dropout(last_hidden)
        logits = self.fc(out)                  # (B, num_products)
        return logits

    def predict_top_k(self, sequence: List[int], k: int = 5) -> List[Dict]:
        """
        sequence: danh sách product_id gần đây của user
        returns: top-k sản phẩm được gợi ý
        """
        self.eval()
        with torch.no_grad():
            x = torch.tensor([sequence], dtype=torch.long)
            logits = self.forward(x)
            probs = torch.softmax(logits, dim=-1).squeeze()
            top_k = torch.topk(probs, k)
            return [
                {'product_id': int(idx), 'score': float(score)}
                for idx, score in zip(top_k.indices, top_k.values)
            ]


def train_lstm(model: LSTMRecommender, train_data: List, epochs: int = 10, lr: float = 0.001):
    """
    Huấn luyện LSTM model với dữ liệu hành vi người dùng.

    train_data: list of (input_sequence, target_product_id)
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    model.train()
    history = []

    for epoch in range(epochs):
        total_loss = 0
        correct = 0

        for sequences, targets in train_data:
            x = torch.tensor(sequences, dtype=torch.long)
            y = torch.tensor(targets, dtype=torch.long)

            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            preds = logits.argmax(dim=1)
            correct += (preds == y).sum().item()

        avg_loss = total_loss / len(train_data)
        accuracy = correct / (len(train_data) * len(train_data[0][1]))
        history.append({'epoch': epoch + 1, 'loss': avg_loss, 'accuracy': accuracy})
        print(f"Epoch {epoch+1}/{epochs} — Loss: {avg_loss:.4f} — Acc: {accuracy:.4f}")

    return history
