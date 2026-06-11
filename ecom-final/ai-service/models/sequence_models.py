"""
3 model du doan & phan loai hanh vi tiep theo cua user: RNN, LSTM, BiLSTM.

Bai toan: cho 7 hanh vi dau (product_id + action) cua mot user, du doan
loai hanh vi (action) o buoc thu 8 trong 3 lop: view (0) / click (1) /
add_to_cart (2).

Kien truc chung:
  Embedding(product_id) + Embedding(action) -> concat -> RNN/LSTM/BiLSTM
  -> lay hidden state cuoi -> Linear -> logits (3 lop)
"""

import torch
import torch.nn as nn

NUM_PRODUCTS = 18   # product_id 1..17 (+ 0 padding)
NUM_ACTIONS = 3     # view, click, add_to_cart
NUM_CLASSES = 3
EMBED_DIM = 16
HIDDEN_DIM = 32

ACTION_TO_IDX = {'view': 0, 'click': 1, 'add_to_cart': 2}
IDX_TO_ACTION = {v: k for k, v in ACTION_TO_IDX.items()}


class SequenceClassifier(nn.Module):
    """Lop co so dung chung cho RNN / LSTM / BiLSTM."""

    def __init__(self, rnn_type: str = 'lstm', bidirectional: bool = False,
                 num_products: int = NUM_PRODUCTS, num_actions: int = NUM_ACTIONS,
                 embed_dim: int = EMBED_DIM, hidden_dim: int = HIDDEN_DIM,
                 num_classes: int = NUM_CLASSES, num_layers: int = 1):
        super().__init__()
        self.rnn_type = rnn_type
        self.bidirectional = bidirectional

        self.product_embed = nn.Embedding(num_products, embed_dim, padding_idx=0)
        self.action_embed = nn.Embedding(num_actions, embed_dim)

        input_dim = embed_dim * 2

        if rnn_type == 'rnn':
            self.rnn = nn.RNN(input_dim, hidden_dim, num_layers=num_layers,
                              batch_first=True, nonlinearity='tanh',
                              bidirectional=bidirectional)
        elif rnn_type == 'lstm':
            self.rnn = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers,
                               batch_first=True, bidirectional=bidirectional)
        else:
            raise ValueError(f"rnn_type khong hop le: {rnn_type}")

        out_dim = hidden_dim * (2 if bidirectional else 1)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(out_dim, num_classes)

    def forward(self, product_seq: torch.Tensor, action_seq: torch.Tensor) -> torch.Tensor:
        """
        product_seq, action_seq: (batch, seq_len) kieu Long
        return: (batch, num_classes) logits
        """
        p = self.product_embed(product_seq)
        a = self.action_embed(action_seq)
        x = torch.cat([p, a], dim=-1)            # (B, L, 2*embed_dim)

        out, _ = self.rnn(x)                      # (B, L, hidden*directions)
        last = out[:, -1, :]                       # hidden state buoc cuoi
        last = self.dropout(last)
        return self.fc(last)


def build_model(name: str) -> SequenceClassifier:
    """name: 'rnn' | 'lstm' | 'bilstm'"""
    if name == 'rnn':
        return SequenceClassifier(rnn_type='rnn', bidirectional=False)
    if name == 'lstm':
        return SequenceClassifier(rnn_type='lstm', bidirectional=False)
    if name == 'bilstm':
        return SequenceClassifier(rnn_type='lstm', bidirectional=True)
    raise ValueError(f"Model khong ho tro: {name}")
