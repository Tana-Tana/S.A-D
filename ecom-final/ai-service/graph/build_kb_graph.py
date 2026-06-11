"""
Xay dung Knowledge Base Graph (KB_Graph) trong Neo4j tu data_user500.csv
va model_best (RNN/LSTM/BiLSTM tot nhat duoc chon o buoc training).

Cau truc graph:
  (:User {user_id})
  (:Product {product_id})

  (:User)-[:VIEWED|CLICKED|ADDED_TO_CART {step, timestamp}]->(:Product)
      tu du lieu hanh vi thuc te (data_user500.csv)

  (:Product)-[:CO_OCCURS {weight}]->(:Product)
      hai san pham cung duoc 1 user tuong tac -> dung cho goi y "san pham lien quan"

  (:User)-[:PREDICTED_NEXT_ACTION {action, confidence, model}]->(:Product)
      du doan cua model_best ve hanh dong tiep theo cua user, gan voi san pham
      o buoc cuoi cung trong chuoi dau vao (step 7)
"""

import json
import os
import sys
from collections import defaultdict

import pandas as pd
import torch
from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.sequence_models import ACTION_TO_IDX, IDX_TO_ACTION, build_model  # noqa: E402

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'data_user500.csv')
LIVE_DATA_PATH = os.path.join(BASE_DIR, 'live_data', 'user_behavior_log.csv')
MODEL_BEST_PATH = os.path.join(BASE_DIR, 'training', 'model_best.pt')
MODEL_BEST_META = os.path.join(BASE_DIR, 'training', 'model_best.json')

ACTION_REL = {'view': 'VIEWED', 'click': 'CLICKED', 'add_to_cart': 'ADDED_TO_CART'}
SEQ_LEN_IN = 7


def get_data_path() -> str:
    """Uu tien du lieu hanh vi that (ghi lien tuc tu /events/), fallback sang dataset goc."""
    return LIVE_DATA_PATH if os.path.exists(LIVE_DATA_PATH) else DATA_PATH


def load_data() -> pd.DataFrame:
    df = pd.read_csv(get_data_path())
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.sort_values(['user_id', 'timestamp'])


def load_model_best():
    with open(MODEL_BEST_META, encoding='utf-8') as f:
        meta = json.load(f)
    model = build_model(meta['best_model'])
    model.load_state_dict(torch.load(MODEL_BEST_PATH, map_location='cpu'))
    model.eval()
    return model, meta


def predict_next_action(model, prod_seq, act_seq):
    with torch.no_grad():
        p = torch.tensor([prod_seq], dtype=torch.long)
        a = torch.tensor([act_seq], dtype=torch.long)
        logits = model(p, a)
        probs = torch.softmax(logits, dim=-1).squeeze().numpy()
        pred = int(probs.argmax())
        return IDX_TO_ACTION[pred], float(probs[pred])


def build_graph():
    df = load_data()
    model, meta = load_model_best()

    behavior_rows = []
    predictions = []
    cooccur = defaultdict(int)

    for user_id, g in df.groupby('user_id'):
        g = g.reset_index(drop=True)
        products_seen = set()

        for step, row in g.iterrows():
            behavior_rows.append({
                'user_id': int(user_id),
                'product_id': int(row['product_id']),
                'rel_type': ACTION_REL[row['action']],
                'step': int(step) + 1,
                'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            })
            products_seen.add(int(row['product_id']))

        if len(g) >= SEQ_LEN_IN:
            # Dung 7 hanh vi GAN NHAT de du doan hanh dong tiep theo -> moi luot
            # view/click/add_to_cart that se lam thay doi du doan ngay khi KB_Graph
            # duoc build lai (xem main.py: vong lap refresh ngam).
            prod_seq = g['product_id'].values[-SEQ_LEN_IN:].astype(int).tolist()
            act_seq = [ACTION_TO_IDX[a] for a in g['action'].values[-SEQ_LEN_IN:]]
            action, confidence = predict_next_action(model, prod_seq, act_seq)
            predictions.append({
                'user_id': int(user_id),
                'action': action,
                'confidence': confidence,
                'context_product_id': prod_seq[-1],
            })

        for p1 in products_seen:
            for p2 in products_seen:
                if p1 < p2:
                    cooccur[(p1, p2)] += 1

    cooccur_rows = [{'p1': k[0], 'p2': k[1], 'weight': v} for k, v in cooccur.items()]

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        session.run("""
            UNWIND $rows AS r
            MERGE (u:User {user_id: r.user_id})
            MERGE (p:Product {product_id: r.product_id})
        """, rows=behavior_rows)

        for rel_type in set(ACTION_REL.values()):
            rows = [r for r in behavior_rows if r['rel_type'] == rel_type]
            if not rows:
                continue
            session.run(f"""
                UNWIND $rows AS r
                MATCH (u:User {{user_id: r.user_id}})
                MATCH (p:Product {{product_id: r.product_id}})
                CREATE (u)-[:{rel_type} {{step: r.step, timestamp: r.timestamp}}]->(p)
            """, rows=rows)

        session.run("""
            UNWIND $rows AS r
            MATCH (p1:Product {product_id: r.p1})
            MATCH (p2:Product {product_id: r.p2})
            MERGE (p1)-[c:CO_OCCURS]->(p2)
            SET c.weight = r.weight
        """, rows=cooccur_rows)

        session.run("""
            UNWIND $rows AS r
            MATCH (u:User {user_id: r.user_id})
            MATCH (p:Product {product_id: r.context_product_id})
            MERGE (u)-[pred:PREDICTED_NEXT_ACTION]->(p)
            SET pred.action = r.action, pred.confidence = r.confidence,
                pred.model = $model_name
        """, rows=predictions, model_name=meta['best_model_label'])

        counts = session.run("""
            MATCH (u:User) WITH count(u) AS users
            MATCH (p:Product) WITH users, count(p) AS products
            MATCH ()-[r]->() WITH users, products, count(r) AS rels
            RETURN users, products, rels
        """).single()

    driver.close()

    summary = {
        'data_path': get_data_path(),
        'rows': len(df),
        'users': counts['users'],
        'products': counts['products'],
        'relationships': counts['rels'],
        'predictions': len(predictions),
        'model': meta['best_model_label'],
    }

    print(f"KB_Graph da duoc xay dung tu model_best={meta['best_model_label']}:")
    print(f"  - du lieu: {summary['data_path']} ({summary['rows']} dong)")
    print(f"  - {counts['users']} User node")
    print(f"  - {counts['products']} Product node")
    print(f"  - {counts['rels']} relationships (VIEWED/CLICKED/ADDED_TO_CART/CO_OCCURS/PREDICTED_NEXT_ACTION)")
    print(f"  - {len(predictions)} du doan PREDICTED_NEXT_ACTION")

    return summary


if __name__ == '__main__':
    build_graph()
