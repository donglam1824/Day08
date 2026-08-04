"""
Task 7 — Reranking Module.

Chọn 1 trong các phương pháp:
    - Cross-encoder reranker: Jina Reranker v2 (multilingual) hoặc Qwen3-Reranker
    - MMR (Maximal Marginal Relevance): tự implement
    - RRF (Reciprocal Rank Fusion): tự implement — khuyến nghị vì không cần API key

Nếu dùng MMR hoặc RRF, đảm bảo hiểu và giải thích được cơ chế.

Lưu ý quan trọng về RRF (sẽ dùng lại ở Task 9): điểm RRF fused CHỈ phụ thuộc thứ hạng,
không phải độ tương đồng thật. Top-1 sau khi fuse luôn xấp xỉ 1/(k+1) ≈ 0.0164 (k=60),
bất kể nội dung đó có thật sự liên quan đến câu hỏi hay không. Đừng dùng điểm RRF để
quyết định fallback ở Task 9 — xem ghi chú ở đó.
"""

import re
from typing import Optional


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", _normalize_text(text))


def _keyword_overlap_score(query: str, content: str) -> float:
    query_terms = set(_tokenize(query))
    content_terms = set(_tokenize(content))
    if not query_terms:
        return 0.0
    return len(query_terms & content_terms) / len(query_terms)


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank candidates bằng heuristic nhẹ dựa trên overlap từ khóa.
    """
    reranked = []
    for candidate in candidates:
        item = dict(candidate)
        base_score = float(item.get("score", 0.0))
        overlap_score = _keyword_overlap_score(query, item.get("content", ""))
        item["score"] = base_score + 0.1 * overlap_score
        reranked.append(item)

    reranked.sort(key=lambda x: x["score"], reverse=True)
    return reranked[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance — chọn candidates vừa relevant vừa diverse.
    """
    if not candidates:
        return []

    selected: list[int] = []
    remaining = list(range(len(candidates)))

    for _ in range(min(top_k, len(candidates))):
        best_idx: Optional[int] = None
        best_score = float("-inf")

        for idx in remaining:
            relevance = float(candidates[idx].get("score", 0.0))
            if query_embedding is not None and candidates[idx].get("embedding") is not None:
                try:
                    relevance = sum(
                        a * b for a, b in zip(query_embedding, candidates[idx]["embedding"])
                    )
                except (TypeError, ValueError):
                    relevance = float(candidates[idx].get("score", 0.0))

            max_sim_to_selected = 0.0
            for sel_idx in selected:
                selected_embedding = candidates[sel_idx].get("embedding")
                current_embedding = candidates[idx].get("embedding")
                if selected_embedding is not None and current_embedding is not None:
                    try:
                        similarity = sum(
                            a * b for a, b in zip(selected_embedding, current_embedding)
                        )
                        max_sim_to_selected = max(max_sim_to_selected, similarity)
                    except (TypeError, ValueError):
                        continue

            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        if best_idx is None:
            break

        selected.append(best_idx)
        remaining.remove(best_idx)

    return [dict(candidates[i]) for i in selected]


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker.
    """
    if not ranked_lists:
        return []

    rrf_scores: dict[str, float] = {}
    content_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            content = item.get("content")
            if not content:
                continue
            if content not in rrf_scores:
                rrf_scores[content] = 0.0
                content_map[content] = dict(item)
            rrf_scores[content] += 1.0 / (k + rank)

    results = []
    for content, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
        item = dict(content_map[content])
        item["score"] = score
        results.append(item)

    return results


# =============================================================================
# Main rerank interface
# =============================================================================

def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "rrf",  # "cross_encoder" | "mmr" | "rrf"
) -> list[dict]:
    """
    Unified reranking interface.
    """
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
        return rerank_mmr([], candidates, top_k)
    elif method == "rrf":
        if candidates and isinstance(candidates[0], list):
            return rerank_rrf(candidates, top_k=top_k)

        reranked = [dict(candidate) for candidate in candidates]
        for item in reranked:
            item["score"] = float(item.get("score", 0.0))
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_k]
    else:
        raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    dummy_candidates = [
        {"content": "Chính sách trả hàng và hoàn tiền Shopee trong 15 ngày", "score": 0.8, "metadata": {}},
        {"content": "Các phương thức thanh toán hỗ trợ trên Shopee Vietnam", "score": 0.6, "metadata": {}},
        {"content": "Quy định đăng bán sản phẩm dành cho người bán", "score": 0.5, "metadata": {}},
    ]
    results = rerank("chính sách trả hàng shopee", dummy_candidates, top_k=2)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content']}")
