"""
Evaluation harness: runs baseline vs multi-agent on the benchmark question set,
scores each report using an LLM judge, and saves results for comparison.

Run with: python src/evaluate.py
"""

import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

from baseline import run_baseline
from multi_agent import run_multi_agent
from questions import BENCHMARK_QUESTIONS

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"


def judge_report(question: str, report: str) -> dict:
    """
    Uses an LLM as a judge to score a report's quality.
    Scores comprehensiveness and clarity from 1-10, with a short reason.
    This is a common technique called 'LLM-as-judge' evaluation.
    """
    prompt = f"""You are an expert evaluator judging the quality of a research report.

Question the report should answer: {question}

Report:
{report}

Rate this report on two dimensions, each from 1-10:
1. Comprehensiveness: does it cover the important angles of the question?
2. Clarity: is it well-organized and easy to follow?

Respond with ONLY a JSON object in this exact format, nothing else:
{{"comprehensiveness": <number>, "clarity": <number>, "reason": "<one sentence explanation>"}}"""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        scores = json.loads(raw)
    except json.JSONDecodeError:
        scores = {"comprehensiveness": None, "clarity": None, "reason": "Failed to parse judge output"}

    return scores


def evaluate_question(question: str) -> dict:
    """
    Runs both systems on one question and scores both reports.
    """
    print(f"\nEvaluating: {question}")

    print("  Running baseline...")
    baseline_result = run_baseline(question)
    baseline_scores = judge_report(question, baseline_result["report"])

    print("  Running multi-agent...")
    multi_agent_result = run_multi_agent(question)
    multi_agent_scores = judge_report(question, multi_agent_result["report"])

    return {
        "question": question,
        "baseline": {
            "num_sources": baseline_result["num_sources"],
            "time_seconds": baseline_result["time_seconds"],
            "comprehensiveness": baseline_scores.get("comprehensiveness"),
            "clarity": baseline_scores.get("clarity"),
        },
        "multi_agent": {
            "num_sources": multi_agent_result["num_sources"],
            "time_seconds": multi_agent_result["time_seconds"],
            "comprehensiveness": multi_agent_scores.get("comprehensiveness"),
            "clarity": multi_agent_scores.get("clarity"),
        },
    }


def run_full_evaluation():
    """
    Runs evaluation across all benchmark questions and saves results to a JSON file.
    """
    all_results = []

    for question in BENCHMARK_QUESTIONS:
        try:
            result = evaluate_question(question)
            all_results.append(result)
        except Exception as e:
            print(f"  FAILED on this question: {e}")
        time.sleep(2)  # small pause to avoid hitting rate limits

    with open("results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print_summary(all_results)


def print_summary(results: list[dict]):
    """
    Prints an averaged comparison table across all evaluated questions.
    """
    def avg(values):
        clean = [v for v in values if v is not None]
        return round(sum(clean) / len(clean), 2) if clean else None

    baseline_sources = avg([r["baseline"]["num_sources"] for r in results])
    baseline_time = avg([r["baseline"]["time_seconds"] for r in results])
    baseline_comp = avg([r["baseline"]["comprehensiveness"] for r in results])
    baseline_clarity = avg([r["baseline"]["clarity"] for r in results])

    ma_sources = avg([r["multi_agent"]["num_sources"] for r in results])
    ma_time = avg([r["multi_agent"]["time_seconds"] for r in results])
    ma_comp = avg([r["multi_agent"]["comprehensiveness"] for r in results])
    ma_clarity = avg([r["multi_agent"]["clarity"] for r in results])

    print("\n" + "=" * 60)
    print(f"SUMMARY ACROSS {len(results)} QUESTIONS")
    print("=" * 60)
    print(f"{'Metric':<20}{'Baseline':<15}{'Multi-Agent':<15}")
    print(f"{'Avg sources':<20}{baseline_sources:<15}{ma_sources:<15}")
    print(f"{'Avg time (s)':<20}{baseline_time:<15}{ma_time:<15}")
    print(f"{'Avg comprehensiveness':<20}{baseline_comp:<15}{ma_comp:<15}")
    print(f"{'Avg clarity':<20}{baseline_clarity:<15}{ma_clarity:<15}")
    print("=" * 60)
    print("Full results saved to results.json")


if __name__ == "__main__":
    run_full_evaluation()