"""
Train + danh gia + so sanh 3 model RNN / LSTM / BiLSTM tren data_user500.csv.

Bai toan: phan loai hanh vi (action) o buoc thu 8 dua tren 7 hanh vi
(product_id + action) truoc do cua tung user.

Outputs:
  - training/plots/training_curves.png      (val loss & accuracy theo epoch)
  - training/plots/confusion_matrices.png   (confusion matrix tren test set)
  - training/plots/model_comparison.png     (bar chart so sanh metrics)
  - training/model_best.pt                  (weights cua model tot nhat)
  - training/model_best.json                (metadata + metrics)
  - training/REPORT.md                      (bao cao danh gia bang loi)
"""

import json
import os
import random
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                              precision_score, recall_score)
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.sequence_models import ACTION_TO_IDX, build_model  # noqa: E402

SEED = 42
SEQ_LEN_IN = 7
EPOCHS = 30
BATCH_SIZE = 32
LR = 0.001

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'data_user500.csv')
PLOTS_DIR = os.path.join(BASE_DIR, 'plots')
MODEL_BEST_PATH = os.path.join(BASE_DIR, 'model_best.pt')
MODEL_BEST_META = os.path.join(BASE_DIR, 'model_best.json')
REPORT_PATH = os.path.join(BASE_DIR, 'REPORT.md')

MODEL_NAMES = ['rnn', 'lstm', 'bilstm']
MODEL_LABELS = {'rnn': 'RNN', 'lstm': 'LSTM', 'bilstm': 'BiLSTM'}


def set_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_dataset():
    """Doc data_user500.csv, tra ve tensors (product_seq, action_seq, target) da split."""
    df = pd.read_csv(DATA_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    df['action_idx'] = df['action'].map(ACTION_TO_IDX)

    products, actions, targets = [], [], []
    for _, g in df.groupby('user_id'):
        g = g.reset_index(drop=True)
        if len(g) < SEQ_LEN_IN + 1:
            continue
        prod_seq = g['product_id'].values[:SEQ_LEN_IN].astype(np.int64)
        act_seq = g['action_idx'].values[:SEQ_LEN_IN].astype(np.int64)
        target = g['action_idx'].values[SEQ_LEN_IN].astype(np.int64)
        products.append(prod_seq)
        actions.append(act_seq)
        targets.append(target)

    products = torch.tensor(np.stack(products), dtype=torch.long)
    actions = torch.tensor(np.stack(actions), dtype=torch.long)
    targets = torch.tensor(np.array(targets), dtype=torch.long)

    n = len(targets)
    idx = np.arange(n)
    rng = np.random.default_rng(SEED)
    rng.shuffle(idx)

    n_train = int(n * 0.7)
    n_val = int(n * 0.15)
    train_idx = idx[:n_train]
    val_idx = idx[n_train:n_train + n_val]
    test_idx = idx[n_train + n_val:]

    def subset(ix):
        return TensorDataset(products[ix], actions[ix], targets[ix])

    return subset(train_idx), subset(val_idx), subset(test_idx)


def evaluate(model, loader, criterion):
    model.eval()
    total_loss, all_preds, all_labels = 0.0, [], []
    with torch.no_grad():
        for prod, act, y in loader:
            logits = model(prod, act)
            loss = criterion(logits, y)
            total_loss += loss.item() * len(y)
            all_preds.append(logits.argmax(dim=1))
            all_labels.append(y)
    preds = torch.cat(all_preds).numpy()
    labels = torch.cat(all_labels).numpy()
    avg_loss = total_loss / len(labels)
    acc = accuracy_score(labels, preds)
    return avg_loss, acc, preds, labels


def train_one_model(name: str, train_ds, val_ds, test_ds):
    set_seed(SEED)
    model = build_model(name)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss, all_preds, all_labels = 0.0, [], []
        for prod, act, y in train_loader:
            optimizer.zero_grad()
            logits = model(prod, act)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(y)
            all_preds.append(logits.argmax(dim=1))
            all_labels.append(y)

        train_loss = total_loss / len(train_ds)
        train_acc = accuracy_score(torch.cat(all_labels).numpy(), torch.cat(all_preds).numpy())
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion)

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        print(f"[{MODEL_LABELS[name]}] Epoch {epoch:02d}/{EPOCHS} "
              f"- train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
              f"- val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

    test_loss, test_acc, preds, labels = evaluate(model, test_loader, criterion)
    metrics = {
        'test_loss': test_loss,
        'accuracy': test_acc,
        'precision_macro': precision_score(labels, preds, average='macro', zero_division=0),
        'recall_macro': recall_score(labels, preds, average='macro', zero_division=0),
        'f1_macro': f1_score(labels, preds, average='macro', zero_division=0),
    }
    cm = confusion_matrix(labels, preds, labels=[0, 1, 2])

    return model, history, metrics, cm


def plot_training_curves(histories):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for name in MODEL_NAMES:
        h = histories[name]
        epochs = range(1, len(h['val_loss']) + 1)
        axes[0].plot(epochs, h['val_loss'], label=MODEL_LABELS[name])
        axes[1].plot(epochs, h['val_acc'], label=MODEL_LABELS[name])

    axes[0].set_title('Validation Loss theo epoch')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].set_title('Validation Accuracy theo epoch')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    fig.suptitle('So sanh qua trinh huan luyen RNN vs LSTM vs BiLSTM')
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, 'training_curves.png'), dpi=120)
    plt.close(fig)


def plot_confusion_matrices(confusions):
    labels = ['view', 'click', 'add_to_cart']
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, name in zip(axes, MODEL_NAMES):
        cm = confusions[name]
        im = ax.imshow(cm, cmap='Blues')
        ax.set_title(MODEL_LABELS[name])
        ax.set_xticks(range(3))
        ax.set_yticks(range(3))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        for i in range(3):
            for j in range(3):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                        color='white' if cm[i, j] > cm.max() / 2 else 'black')
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle('Confusion Matrix tren tap test')
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, 'confusion_matrices.png'), dpi=120)
    plt.close(fig)


def plot_comparison(all_metrics):
    metric_keys = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
    metric_labels = ['Accuracy', 'Precision (macro)', 'Recall (macro)', 'F1 (macro)']

    x = np.arange(len(metric_keys))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for i, name in enumerate(MODEL_NAMES):
        values = [all_metrics[name][k] for k in metric_keys]
        ax.bar(x + (i - 1) * width, values, width, label=MODEL_LABELS[name])

    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel('Score')
    ax.set_title('So sanh metrics tren tap test: RNN vs LSTM vs BiLSTM')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    for i, name in enumerate(MODEL_NAMES):
        for j, k in enumerate(metric_keys):
            v = all_metrics[name][k]
            ax.text(j + (i - 1) * width, v + 0.01, f"{v:.2f}", ha='center', fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, 'model_comparison.png'), dpi=120)
    plt.close(fig)


def write_report(all_metrics, best_name, histories):
    lines = []
    lines.append("# Bao cao so sanh model RNN / LSTM / BiLSTM\n")
    lines.append("Du lieu: `data_user500.csv` (500 user x 8 hanh vi). "
                  "Bai toan: phan loai hanh vi (view / click / add_to_cart) "
                  "o buoc thu 8 dua tren 7 hanh vi truoc do.\n")

    lines.append("## Ket qua tren tap test\n")
    lines.append("| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) |")
    lines.append("|---|---|---|---|---|")
    for name in MODEL_NAMES:
        m = all_metrics[name]
        lines.append(
            f"| {MODEL_LABELS[name]} | {m['accuracy']:.4f} | "
            f"{m['precision_macro']:.4f} | {m['recall_macro']:.4f} | {m['f1_macro']:.4f} |"
        )

    lines.append("\n## Hinh anh\n")
    lines.append("- `plots/training_curves.png`: Validation loss & accuracy qua cac epoch.")
    lines.append("- `plots/confusion_matrices.png`: Confusion matrix tren tap test cua 3 model.")
    lines.append("- `plots/model_comparison.png`: Bieu do cot so sanh 4 metrics.")

    best = all_metrics[best_name]
    lines.append("\n## Danh gia bang loi\n")
    lines.append(
        f"- **RNN** co kien truc don gian, it tham so nhat trong 3 model. Voi chuoi ngan "
        f"(7 buoc) va tap du lieu nho (~350 mau train), RNN it bi overfitting hon va "
        f"hoi tu on dinh. F1={all_metrics['rnn']['f1_macro']:.4f}, "
        f"gap train/val accuracy cuoi = {histories['rnn']['train_acc'][-1] - histories['rnn']['val_acc'][-1]:.4f}."
    )
    lines.append(
        f"- **LSTM** co co che cong (gate) giup ghi nho thong tin dai han, nhung cung co "
        f"nhieu tham so hon nen de overfit khi du lieu it. F1={all_metrics['lstm']['f1_macro']:.4f}, "
        f"gap train/val accuracy cuoi = {histories['lstm']['train_acc'][-1] - histories['lstm']['val_acc'][-1]:.4f}."
    )
    lines.append(
        f"- **BiLSTM** xu ly chuoi theo ca hai chieu (xuoi va nguoc), nam bat ngu canh day du "
        f"hon nhung so tham so gap doi LSTM nen can nhieu du lieu hon de phat huy uu the. "
        f"F1={all_metrics['bilstm']['f1_macro']:.4f}, "
        f"gap train/val accuracy cuoi = {histories['bilstm']['train_acc'][-1] - histories['bilstm']['val_acc'][-1]:.4f}."
    )
    gaps = {
        name: histories[name]['train_acc'][-1] - histories[name]['val_acc'][-1]
        for name in MODEL_NAMES
    }
    f1s = {name: all_metrics[name]['f1_macro'] for name in MODEL_NAMES}
    runner_up = max((n for n in MODEL_NAMES if n != best_name), key=lambda n: f1s[n])

    lines.append(
        f"\nTren tap test, **{MODEL_LABELS[best_name]} dat F1 macro cao nhat "
        f"({f1s[best_name]:.4f})**, nhinh hon {MODEL_LABELS[runner_up]} "
        f"({f1s[runner_up]:.4f}) va cac model con lai. Gap train/val accuracy cuoi cung: "
        + ", ".join(f"{MODEL_LABELS[n]}={gaps[n]:.4f}" for n in MODEL_NAMES)
        + (
            f". Du {MODEL_LABELS[best_name]} co dau hieu overfit ro hon tren tap validation "
            f"(xem `plots/training_curves.png`), no van tong quat hoa tot hon tren tap test, "
            f"cho thay kien truc nay phu hop hon voi mau hinh hanh vi trong du lieu hien tai."
            if gaps[best_name] == max(gaps.values())
            else f". {MODEL_LABELS[best_name]} vua co F1 macro cao nhat vua co gap train/val "
                 f"thap, cho thay day la lua chon on dinh va tong quat hoa tot."
        )
    )
    lines.append(
        f"\n=> **Model duoc chon lam `model_best`: {MODEL_LABELS[best_name]}** "
        f"(F1 macro cao nhat = {best['f1_macro']:.4f}, Accuracy = {best['accuracy']:.4f}). "
        f"Day la model se duoc su dung de sinh quan he du doan trong KB_Graph (Neo4j) "
        f"va phuc vu API `/recommend`, `/chatbot` cua AI service. KB_Graph duoc lam moi "
        f"dinh ky (background refresh) tu du lieu hanh vi thuc te moi nhat, nen du doan "
        f"cua `model_best` se cap nhat theo hanh vi gan day cua tung user."
    )

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(PLOTS_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        print(f"Khong tim thay {DATA_PATH}. Hay chay data/generate_data.py truoc.")
        sys.exit(1)

    train_ds, val_ds, test_ds = load_dataset()
    print(f"Train={len(train_ds)} Val={len(val_ds)} Test={len(test_ds)}")

    histories, all_metrics, confusions, models = {}, {}, {}, {}

    for name in MODEL_NAMES:
        print(f"\n===== Training {MODEL_LABELS[name]} =====")
        model, history, metrics, cm = train_one_model(name, train_ds, val_ds, test_ds)
        histories[name] = history
        all_metrics[name] = metrics
        confusions[name] = cm
        models[name] = model
        print(f"[{MODEL_LABELS[name]}] TEST -> {metrics}")

    plot_training_curves(histories)
    plot_confusion_matrices(confusions)
    plot_comparison(all_metrics)

    best_name = max(MODEL_NAMES, key=lambda n: all_metrics[n]['f1_macro'])
    torch.save(models[best_name].state_dict(), MODEL_BEST_PATH)

    meta = {
        'best_model': best_name,
        'best_model_label': MODEL_LABELS[best_name],
        'metrics': all_metrics,
    }
    with open(MODEL_BEST_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    write_report(all_metrics, best_name, histories)

    print(f"\n=> model_best = {MODEL_LABELS[best_name]} (F1={all_metrics[best_name]['f1_macro']:.4f})")
    print(f"Da luu: {MODEL_BEST_PATH}, {MODEL_BEST_META}, {REPORT_PATH}")
    print(f"Plots: {PLOTS_DIR}")


if __name__ == '__main__':
    main()
