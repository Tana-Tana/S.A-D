# Bao cao so sanh model RNN / LSTM / BiLSTM

Du lieu: `data_user500.csv` (500 user x 8 hanh vi). Bai toan: phan loai hanh vi (view / click / add_to_cart) o buoc thu 8 dua tren 7 hanh vi truoc do.

## Ket qua tren tap test

| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) |
|---|---|---|---|---|
| RNN | 0.5867 | 0.5171 | 0.5448 | 0.5147 |
| LSTM | 0.5733 | 0.4545 | 0.5143 | 0.4701 |
| BiLSTM | 0.5867 | 0.5303 | 0.5477 | 0.5267 |

## Hinh anh

- `plots/training_curves.png`: Validation loss & accuracy qua cac epoch.
- `plots/confusion_matrices.png`: Confusion matrix tren tap test cua 3 model.
- `plots/model_comparison.png`: Bieu do cot so sanh 4 metrics.

## Danh gia bang loi

- **RNN** co kien truc don gian, it tham so nhat trong 3 model. Voi chuoi ngan (7 buoc) va tap du lieu nho (~350 mau train), RNN it bi overfitting hon va hoi tu on dinh. F1=0.5147, gap train/val accuracy cuoi = 0.1838.
- **LSTM** co co che cong (gate) giup ghi nho thong tin dai han, nhung cung co nhieu tham so hon nen de overfit khi du lieu it. F1=0.4701, gap train/val accuracy cuoi = 0.2648.
- **BiLSTM** xu ly chuoi theo ca hai chieu (xuoi va nguoc), nam bat ngu canh day du hon nhung so tham so gap doi LSTM nen can nhieu du lieu hon de phat huy uu the. F1=0.5267, gap train/val accuracy cuoi = 0.3095.

Tren tap test, **BiLSTM dat F1 macro cao nhat (0.5267)**, nhinh hon RNN (0.5147) va LSTM (0.4701) — du gap train/val accuracy cua BiLSTM (0.3095) lon hon RNN (0.1838) va LSTM (0.2648). Dieu nay cho thay co che hai chieu (xuoi + nguoc) cua BiLSTM giup nam bat tot hon cac mau hinh hanh vi (vi du: chuoi "xem nhieu san pham cung danh muc -> sap them vao gio hang") tu du lieu hanh vi thuc te (`user_behavior_log.csv`), du mo hinh co dau hieu overfit nhe tren tap validation (xem `plots/training_curves.png`). RNN voi it tham so nhat van la phuong an on dinh, gap train/val nho nhat, la lua chon du phong tot neu du lieu it bien dong hon.

=> **Model duoc chon lam `model_best`: BiLSTM** (F1 macro cao nhat = 0.5267, Accuracy = 0.5867). Day la model se duoc su dung de sinh quan he du doan trong KB_Graph (Neo4j) va phuc vu API `/recommend`, `/chatbot` cua AI service. KB_Graph duoc lam moi dinh ky (background refresh) tu du lieu hanh vi thuc te moi nhat, nen du doan cua BiLSTM se cap nhat theo hanh vi gan day cua tung user.