"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
SDK & sample code: https://github.com/VectifyAI/PageIndex

PageIndex cho phép RAG mà không cần vector store — sử dụng
structural understanding của document thay vì embedding.

Cài đặt:
    pip install pageindex

Hướng dẫn:
    1. Đăng ký account tại pageindex.ai
    2. Lấy API key
    3. Upload documents
    4. Query sử dụng PageIndex API

Lưu ý: API `/retrieval` của PageIndex hiện đã deprecated (vẫn hoạt động, nhưng response
có field "deprecation" cảnh báo) và trả kết quả trong "retrieved_nodes" — mỗi node có
"relevant_contents": list[list[{section_title, relevant_content}]]. In response thật ra
(json.dumps(...)) trước khi viết logic parse, đừng đoán schema từ ví dụ code cũ.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in this lab environment
    def load_dotenv() -> bool:
        return False

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    """
    Upload toàn bộ markdown documents lên PageIndex.
    """
    from pageindex.client import PageIndexClient
    import json
    import time
    
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    doc_ids = []
    
    print("Uploading markdown documents to PageIndex...")
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        # PageIndex now accepts .md files directly
        resp = client.submit_document(str(md_file))
        doc_id = resp.get("doc_id") or resp.get("id")
        if doc_id:
            doc_ids.append(doc_id)
            print(f"  ✓ Uploaded: {md_file.name} -> {doc_id}")
            time.sleep(1) # Prevent rate limiting
            
    # Save doc_ids for retrieval
    doc_ids_path = STANDARDIZED_DIR.parent / "pageindex_docs.json"
    with open(doc_ids_path, "w", encoding="utf-8") as f:
        json.dump(doc_ids, f)
    print(f"  ✓ Saved {len(doc_ids)} doc_ids to {doc_ids_path.name}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex.
    Dùng làm fallback khi hybrid search không có kết quả tốt.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': 'pageindex'   # Đánh dấu nguồn retrieval
        }
    """
    from pageindex.client import PageIndexClient
    import json
    import time
    
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    doc_ids_path = STANDARDIZED_DIR.parent / "pageindex_docs.json"
    
    doc_ids = []
    if doc_ids_path.exists():
        with open(doc_ids_path, "r", encoding="utf-8") as f:
            doc_ids = json.load(f)
            
    if not doc_ids:
        # Fallback to fetching from API if no local file
        resp = client.list_documents(limit=10)
        doc_ids = [doc.get("id") for doc in resp.get("documents", []) if doc.get("id")]
        
    results = []
    
    # We query the first doc_id (or loop through them if we want to combine)
    # To keep it fast, we will query all in parallel or just query the first 3 docs
    for doc_id in doc_ids[:3]:
        try:
            resp = client.submit_query(doc_id=doc_id, query=query)
            retrieval_id = resp.get("retrieval_id") or resp.get("id")
            if not retrieval_id:
                continue
                
            # Poll for completion
            retrieval = None
            max_retries = 15
            for _ in range(max_retries):
                r = client.get_retrieval(retrieval_id)
                if r.get("status") == "completed":
                    retrieval = r
                    break
                elif r.get("status") == "failed":
                    break
                time.sleep(1)
                
            if not retrieval:
                continue
                
            # Parse retrieval["retrieved_nodes"]
            for node in retrieval.get("retrieved_nodes", [])[:2]:
                for group in node.get("relevant_contents", []):
                    for item in group:
                        results.append({
                            "content": item.get("relevant_content", ""),
                            # Fake a score since PageIndex doesn't provide one directly
                            "score": 0.85, 
                            "metadata": {"section": item.get("section_title")},
                            "source": "pageindex",
                        })
        except Exception as e:
            print(f"Error querying PageIndex for doc_id {doc_id}: {e}")
            
    # Deduplicate and sort if needed
    # Sort by some logic or just take top_k
    return results[:top_k]


if __name__ == "__main__":
    if not PAGEINDEX_API_KEY:
        print("⚠ Hãy set PAGEINDEX_API_KEY trong file .env")
        print("  Đăng ký tại: https://pageindex.ai/")
    else:
        print("Uploading documents...")
        upload_documents()

        print("\nTest query:")
        results = pageindex_search("danh sách sản phẩm cấm đăng bán", top_k=3)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")
