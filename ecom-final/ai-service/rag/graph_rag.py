"""
Graph-RAG: tra cuu KB_Graph (Neo4j) duoc xay tu data_user500.csv + model_best,
lam ngu canh (context) cho chatbot va API goi y san pham.
"""

import os
from typing import Dict, List, Optional

from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

ACTION_LABELS = {
    'view': 'xem',
    'click': 'click vao',
    'add_to_cart': 'them vao gio hang',
}


class GraphRAG:
    """Wrapper truy van KB_Graph trong Neo4j."""

    def __init__(self):
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        return self._driver

    def close(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def is_available(self) -> bool:
        try:
            with self._get_driver().session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception:
            return False

    def get_user_profile(self, user_id: int) -> Dict:
        """Lich su hanh vi + du doan hanh dong tiep theo cua user tu KB_Graph."""
        query = """
        OPTIONAL MATCH (u:User {user_id: $user_id})-[r]->(p:Product)
        WHERE type(r) IN ['VIEWED','CLICKED','ADDED_TO_CART']
        WITH type(r) AS action, p.product_id AS product_id, count(*) AS cnt
        ORDER BY cnt DESC
        WITH collect({action: action, product_id: product_id, count: cnt}) AS history
        OPTIONAL MATCH (u2:User {user_id: $user_id})-[pred:PREDICTED_NEXT_ACTION]->(pp:Product)
        RETURN history,
               pred.action AS predicted_action,
               pred.confidence AS confidence,
               pp.product_id AS predicted_product_id,
               pred.model AS model_name
        """
        with self._get_driver().session() as session:
            record = session.run(query, user_id=user_id).single()
        if not record:
            return {}
        history = [h for h in record['history'] if h.get('product_id') is not None]
        return {
            'history': history,
            'predicted_action': record['predicted_action'],
            'confidence': record['confidence'],
            'predicted_product_id': record['predicted_product_id'],
            'model_name': record['model_name'],
        }

    def get_related_products(self, product_id: int, limit: int = 5) -> List[Dict]:
        """San pham hay duoc tuong tac cung voi product_id (CO_OCCURS)."""
        query = """
        MATCH (p:Product {product_id: $product_id})-[c:CO_OCCURS]-(other:Product)
        RETURN other.product_id AS product_id, c.weight AS weight
        ORDER BY weight DESC LIMIT $limit
        """
        with self._get_driver().session() as session:
            return [dict(r) for r in session.run(query, product_id=product_id, limit=limit)]

    def get_popular_products(self, rel_type: str = 'ADDED_TO_CART', limit: int = 5) -> List[Dict]:
        """San pham pho bien nhat theo loai hanh dong, tinh tren toan bo KB_Graph."""
        if rel_type not in ('VIEWED', 'CLICKED', 'ADDED_TO_CART'):
            rel_type = 'ADDED_TO_CART'
        query = f"""
        MATCH (:User)-[r:{rel_type}]->(p:Product)
        RETURN p.product_id AS product_id, count(r) AS count
        ORDER BY count DESC LIMIT $limit
        """
        with self._get_driver().session() as session:
            return [dict(r) for r in session.run(query, limit=limit)]

    def build_context(self, user_id: Optional[int]) -> Dict:
        """
        Tong hop ngu canh tu KB_Graph cho 1 user de dua vao chatbot/recommend:
          - top san pham user da tuong tac nhieu nhat
          - du doan hanh dong tiep theo (tu model_best)
          - san pham lien quan (CO_OCCURS) voi san pham du doan
          - fallback: san pham pho bien toan he thong
        """
        result = {
            'product_ids': [],
            'predicted_action': None,
            'confidence': None,
            'model_name': None,
            'note': '',
        }

        profile = self.get_user_profile(user_id) if user_id else {}
        history = profile.get('history') or []

        if history:
            top_products = [h['product_id'] for h in history[:3]]
            result['product_ids'].extend(top_products)

        predicted_product_id = profile.get('predicted_product_id')
        predicted_action = profile.get('predicted_action')
        if predicted_product_id is not None:
            result['predicted_action'] = predicted_action
            result['confidence'] = profile.get('confidence')
            result['model_name'] = profile.get('model_name')
            related = self.get_related_products(predicted_product_id, limit=3)
            result['product_ids'].extend([r['product_id'] for r in related])

        if not result['product_ids']:
            popular = self.get_popular_products('ADDED_TO_CART', limit=5)
            result['product_ids'] = [p['product_id'] for p in popular]
            result['note'] = 'Khong co lich su rieng, dung san pham pho bien tu KB_Graph.'

        # khu trung, gioi han 5
        seen = set()
        unique_ids = []
        for pid in result['product_ids']:
            if pid not in seen:
                seen.add(pid)
                unique_ids.append(pid)
        result['product_ids'] = unique_ids[:5]

        return result

    def describe(self, user_id: Optional[int]) -> str:
        """Sinh doan mo ta ngu canh bang tieng Viet de chatbot tham khao."""
        ctx = self.build_context(user_id)
        if ctx['predicted_action']:
            action_vn = ACTION_LABELS.get(ctx['predicted_action'], ctx['predicted_action'])
            return (
                f"Theo KB_Graph (model {ctx['model_name']}), user {user_id} co kha nang "
                f"se '{action_vn}' tiep theo voi do tin cay {ctx['confidence']:.0%}. "
                f"Cac san pham lien quan: {ctx['product_ids']}."
            )
        return (
            f"Khong tim thay lich su rieng cho user {user_id} trong KB_Graph. "
            f"Goi y dua tren san pham pho bien: {ctx['product_ids']}."
        )


graph_rag = GraphRAG()
