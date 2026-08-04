# RAG Evaluation Results

## A/B Comparison

| Config | Faithfulness | Relevancy | Context Recall | Context Precision |
|--------|--------------|-----------|----------------|-------------------|
| hybrid_rerank | 0.6271 | 0.1709 | 0.8333 | 0.7155 |
| dense_only | 0.6209 | 0.0728 | 0.8333 | 0.7442 |

## Recommendations

- Cấu hình có sử dụng reranking thường cho ra context precision và recall tốt hơn.
- Nếu OpenRouter limit, có thể xem xét dùng local model hoặc fallback.