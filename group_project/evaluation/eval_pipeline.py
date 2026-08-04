"""
RAG Evaluation Pipeline.

Sử dụng DeepEval / RAGAS / TruLens để đánh giá chất lượng RAG pipeline.
Chọn 1 framework và implement đầy đủ.

Yêu cầu:
    1. Load golden_dataset.json (≥15 Q&A pairs)
    2. Chạy RAG pipeline trên từng question
    3. Evaluate với 4 metrics: faithfulness, relevance, context_recall, context_precision
    4. So sánh A/B ít nhất 2 configs
    5. Export results ra results.md

Lưu ý rate limit nếu dùng model OpenRouter ":free": RAGAS/DeepEval gọi LLM RẤT NHIỀU LẦN
(không phải 1 lần/câu hỏi mà nhiều lần/metric/câu hỏi). Model free của OpenRouter giới hạn
50 request/ngày CHO CẢ TÀI KHOẢN (không phải theo model hay theo API key — đổi model free
khác hay tạo key mới KHÔNG reset quota). Nếu chạy full 15+ câu hỏi mà bị rate limit giữa
chừng, thử giảm xuống subset 5 câu để chạy kịp trong buổi, hoặc nạp $10 credit để mở khóa
1000 request/ngày.
"""

import json
from pathlib import Path

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent / "results.md"


def load_golden_dataset() -> list[dict]:
    """Load golden dataset từ JSON file."""
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Option 1: DeepEval
# =============================================================================

def evaluate_with_deepeval(rag_pipeline, golden_dataset: list[dict]) -> dict:
    """
    Evaluate RAG pipeline sử dụng DeepEval.

    pip install deepeval
    """
    # TODO: Implement
    #
    # from deepeval import evaluate
    # from deepeval.metrics import (
    #     FaithfulnessMetric,
    #     AnswerRelevancyMetric,
    #     ContextualRecallMetric,
    #     ContextualPrecisionMetric,
    # )
    # from deepeval.test_case import LLMTestCase
    #
    # test_cases = []
    # for item in golden_dataset:
    #     result = rag_pipeline.generate_with_citation(item["question"])
    #     test_case = LLMTestCase(
    #         input=item["question"],
    #         actual_output=result["answer"],
    #         expected_output=item["expected_answer"],
    #         retrieval_context=[c["content"] for c in result["sources"]],
    #     )
    #     test_cases.append(test_case)
    #
    # metrics = [
    #     FaithfulnessMetric(threshold=0.7),
    #     AnswerRelevancyMetric(threshold=0.7),
    #     ContextualRecallMetric(threshold=0.7),
    #     ContextualPrecisionMetric(threshold=0.7),
    # ]
    #
    # results = evaluate(test_cases, metrics)
    # return results
    raise NotImplementedError("Implement evaluate_with_deepeval")


# =============================================================================
# Option 2: RAGAS
# =============================================================================

def evaluate_with_ragas(rag_pipeline, golden_dataset: list[dict]) -> dict:
    """
    Evaluate RAG pipeline sử dụng RAGAS.

    pip install ragas
    """
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
    )
    from datasets import Dataset
    import os
    from langchain_openai import ChatOpenAI
    from langchain_community.embeddings import HuggingFaceEmbeddings

    eval_data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

    for item in golden_dataset:
        result = rag_pipeline.generate_with_citation(item["question"])
        eval_data["question"].append(item["question"])
        eval_data["answer"].append(result["answer"])
        eval_data["contexts"].append([c["content"] for c in result["sources"]])
        eval_data["ground_truth"].append(item["expected_answer"])

    dataset = Dataset.from_dict(eval_data)
    
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    # Sử dụng ChatOpenAI wrapper trỏ tới OpenRouter
    llm = ChatOpenAI(
        api_key=api_key, 
        base_url="https://openrouter.ai/api/v1", 
        model="openai/gpt-4o-mini"
    )
    # Dùng local embeddings để không tốn API call
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
        llm=llm,
        embeddings=embeddings
    )
    return result.to_pandas()


# =============================================================================
# Option 3: TruLens
# =============================================================================

def evaluate_with_trulens(rag_pipeline, golden_dataset: list[dict]) -> dict:
    """
    Evaluate RAG pipeline sử dụng TruLens.

    pip install trulens
    """
    # TODO: Implement
    #
    # from trulens.apps.custom import TruCustomApp
    # from trulens.core import Feedback
    # from trulens.providers.openai import OpenAI as TruOpenAI
    #
    # provider = TruOpenAI()
    #
    # f_faithfulness = Feedback(provider.groundedness_measure_with_cot_reasons).on_output()
    # f_relevance = Feedback(provider.relevance).on_input_output()
    # f_context_relevance = Feedback(provider.context_relevance).on_input()
    #
    # tru_rag = TruCustomApp(
    #     rag_pipeline,
    #     app_name="EcommerceSupport_RAG",
    #     feedbacks=[f_faithfulness, f_relevance, f_context_relevance],
    # )
    #
    # with tru_rag as recording:
    #     for item in golden_dataset:
    #         rag_pipeline.generate_with_citation(item["question"])
    #
    # # Dashboard: from trulens.dashboard import run_dashboard; run_dashboard()
    raise NotImplementedError("Implement evaluate_with_trulens")


# =============================================================================
# A/B Comparison
# =============================================================================

def compare_configs(rag_pipeline, golden_dataset: list[dict]):
    """
    So sánh A/B giữa ít nhất 2 configs.

    Gợi ý configs để so sánh:
    - Config A: hybrid search + reranking
    - Config B: dense-only (không reranking)
    - Config C: hybrid search + PageIndex fallback
    """
    configs = {
        "hybrid_rerank": {"use_reranking": True},
        "dense_only": {"use_reranking": False},
    }

    results = {}
    original_retrieve = rag_pipeline.retrieve
    
    for config_name, params in configs.items():
        print(f"\n--- Running evaluation for config: {config_name} ---")
        
        # Monkey patch
        def mock_retrieve(query, top_k=5, **kwargs):
            return original_retrieve(query, top_k=top_k, use_reranking=params["use_reranking"])
            
        rag_pipeline.retrieve = mock_retrieve
        
        try:
            df = evaluate_with_ragas(rag_pipeline, golden_dataset)
            # Drop non-numeric columns for mean
            numeric_df = df.select_dtypes(include='number')
            results[config_name] = numeric_df.mean().to_dict()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error evaluating {config_name}: {e}")
            results[config_name] = {}
            
    # Restore original retrieve
    rag_pipeline.retrieve = original_retrieve

    return results


# =============================================================================
# Export Results
# =============================================================================

def export_results(results: dict, comparison: dict):
    """Export evaluation results to results.md"""
    content = "# RAG Evaluation Results\n\n"
    
    content += "## A/B Comparison\n\n"
    content += "| Config | Faithfulness | Relevancy | Context Recall | Context Precision |\n"
    content += "|--------|--------------|-----------|----------------|-------------------|\n"
    
    for config_name, scores in comparison.items():
        if not scores:
            content += f"| {config_name} | ERROR | ERROR | ERROR | ERROR |\n"
            continue
            
        f_score = scores.get('faithfulness', 0.0)
        r_score = scores.get('answer_relevancy', 0.0)
        cr_score = scores.get('context_recall', 0.0)
        cp_score = scores.get('context_precision', 0.0)
        
        content += f"| {config_name} | {f_score:.4f} | {r_score:.4f} | {cr_score:.4f} | {cp_score:.4f} |\n"

    content += "\n## Recommendations\n\n"
    content += "- Cấu hình có sử dụng reranking thường cho ra context precision và recall tốt hơn.\n"
    content += "- Nếu OpenRouter limit, có thể xem xét dùng local model hoặc fallback."

    RESULTS_PATH.write_text(content, encoding="utf-8")
    print(f"\n✅ Đã xuất kết quả ra {RESULTS_PATH}")


if __name__ == "__main__":
    # Giới hạn 15 câu hỏi để không bị OpenRouter block
    golden_dataset = load_golden_dataset()[:15]
    print(f"Loaded {len(golden_dataset)} test cases")

    import src.task10_generation as pipeline
    
    print("Running A/B Comparison...")
    comparison = compare_configs(pipeline, golden_dataset)
    export_results(None, comparison)
