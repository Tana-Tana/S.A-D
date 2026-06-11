"""
RAG (Retrieval-Augmented Generation) Pipeline cho Chatbot tư vấn sản phẩm.

Pipeline:
  1. Người dùng nhập query ("tôi cần laptop gaming dưới 20 triệu")
  2. Embedding query → vector
  3. ChromaDB tìm top-K sản phẩm tương tự (similarity search)
  4. Ghép context sản phẩm vào prompt
  5. LLM (GPT / Claude) sinh câu trả lời tự nhiên
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import json
import httpx
import os


PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class ProductVectorStore:
    """Quản lý vector database ChromaDB cho sản phẩm."""

    def __init__(self, collection_name: str = "products"):
        self.client = chromadb.Client()
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn,
        )

    def index_products(self, products: List[Dict]):
        """Đánh chỉ mục sản phẩm vào vector store."""
        documents, metadatas, ids = [], [], []
        for p in products:
            text = f"{p['name']}. {p.get('description', '')}. Giá: {p['price']} VNĐ."
            documents.append(text)
            metadatas.append({
                'product_id': str(p['id']),
                'name': p['name'],
                'price': str(p['price']),
                'type': p.get('product_type', ''),
            })
            ids.append(str(p['id']))

        if documents:
            self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        return len(documents)

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Tìm sản phẩm liên quan theo ngữ nghĩa."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        products = []
        for i, meta in enumerate(results['metadatas'][0]):
            products.append({
                'product_id': meta['product_id'],
                'name': meta['name'],
                'price': meta['price'],
                'type': meta['type'],
                'relevance_score': 1 - results['distances'][0][i],
            })
        return products


class RAGChatbot:
    """
    Chatbot tư vấn sản phẩm sử dụng RAG pipeline.
    Kết hợp: Vector Search + LLM để tạo câu trả lời tự nhiên.
    """

    SYSTEM_PROMPT = """Bạn là trợ lý tư vấn mua sắm thông minh cho sàn e-commerce.
Dựa trên thông tin sản phẩm được cung cấp, hãy tư vấn cho khách hàng một cách
thân thiện, chính xác và hữu ích. Luôn đề xuất sản phẩm phù hợp với nhu cầu.
Trả lời bằng tiếng Việt."""

    def __init__(self, vector_store: ProductVectorStore):
        self.vector_store = vector_store

    def build_context(self, products: List[Dict]) -> str:
        """Tạo context từ danh sách sản phẩm tìm được."""
        if not products:
            return "Không tìm thấy sản phẩm phù hợp."
        lines = ["Các sản phẩm liên quan:"]
        for i, p in enumerate(products, 1):
            lines.append(
                f"{i}. {p['name']} — Giá: {p['price']} VNĐ (Độ phù hợp: {p['relevance_score']:.0%})"
            )
        return "\n".join(lines)

    def chat(self, user_query: str, chat_history: List[Dict] = None) -> Dict:
        """
        Xử lý câu hỏi của user và trả về câu trả lời.

        Returns:
            {
                'answer': str,
                'products': List[Dict],
                'sources': List[str]
            }
        """
        retrieved = self.vector_store.search(user_query, n_results=5)
        context = self.build_context(retrieved)

        prompt = f"""Thông tin sản phẩm:
{context}

Câu hỏi của khách hàng: {user_query}

Hãy tư vấn dựa trên các sản phẩm trên:"""

        answer = self._call_llm(prompt, chat_history or [])

        return {
            'answer': answer,
            'products': retrieved,
            'sources': [p['name'] for p in retrieved],
        }

    def _call_llm(self, prompt: str, history: List[Dict]) -> str:
        """Gọi LLM API. Có fallback nếu không có API key."""
        if not OPENAI_API_KEY:
            return self._mock_response(prompt)

        messages = [{'role': 'system', 'content': self.SYSTEM_PROMPT}]
        for msg in history[-4:]:
            messages.append(msg)
        messages.append({'role': 'user', 'content': prompt})

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={"model": "gpt-3.5-turbo", "messages": messages, "max_tokens": 500},
                )
                return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Phản hồi mẫu khi không có LLM API (dùng cho demo/test)."""
        return ("Dựa trên yêu cầu của bạn, tôi tìm thấy một số sản phẩm phù hợp. "
                "Vui lòng xem danh sách sản phẩm được gợi ý bên dưới. "
                "Nếu cần tư vấn thêm, hãy mô tả chi tiết hơn về nhu cầu của bạn!")
