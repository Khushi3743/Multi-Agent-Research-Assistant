"""
Multi-agent research system.
Given a question, it:
  1. PLANS: breaks the question into 3-4 sub-questions
  2. RESEARCHES: searches the web separately for each sub-question
  3. SYNTHESIZES: combines all findings into one cited report

This is compared against the single-call baseline in src/baseline.py

Run with: python src/multi_agent.py
"""

import os
import time
import json
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "openai/gpt-oss-20b"


def plan_subquestions(question: str) -> list[str]:
    """
    Agent 1: The Planner.
    Breaks the main question into 3-4 focused sub-questions to research separately.
    """
    prompt = f"""You are a research planner. Break the following question into 3-4 focused sub-questions that, together, would let someone answer the main question thoroughly.

Main question: {question}

Respond with ONLY a JSON list of strings, nothing else. Example format:
["sub-question 1", "sub-question 2", "sub-question 3"]"""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        subquestions = json.loads(raw)
    except json.JSONDecodeError:
        subquestions = [question]

    return subquestions


def research_subquestion(subquestion: str) -> dict:
    """
    Agent 2: The Researcher.
    Searches the web for ONE sub-question and returns the sources found.
    """
    search_results = tavily_client.search(query=subquestion, max_results=3)
    sources = search_results["results"]

    findings = "\n\n".join(
        f"Source: {s['title']}\nURL: {s['url']}\nContent: {s['content']}"
        for s in sources
    )

    return {
        "subquestion": subquestion,
        "findings": findings,
        "sources": [s["url"] for s in sources],
    }


def synthesize_report(question: str, research_results: list[dict]) -> str:
    """
    Agent 3: The Synthesizer.
    Combines findings from all sub-questions into one coherent, cited report.
    """
    combined_findings = "\n\n---\n\n".join(
        f"Sub-question: {r['subquestion']}\n{r['findings']}"
        for r in research_results
    )

    prompt = f"""You are a research synthesizer. You have been given research findings for several sub-questions that together answer a main question. Combine them into ONE clear, well-organized report.

Main question: {question}

Research findings:
{combined_findings}

Write a clear report that answers the main question, drawing on all the sub-question findings. Cite sources by URL when you use information from them. Include a "Sources" section at the end listing all URLs used."""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


def run_multi_agent(question: str) -> dict:
    """
    Runs the full multi-agent pipeline: plan -> research -> synthesize.
    Returns a dict with the report, sources, and timing -- same shape as baseline,
    so the two can be compared directly later.
    """
    start_time = time.time()

    subquestions = plan_subquestions(question)
    research_results = [research_subquestion(sq) for sq in subquestions]
    report = synthesize_report(question, research_results)

    elapsed = time.time() - start_time

    all_sources = []
    for r in research_results:
        all_sources.extend(r["sources"])

    return {
        "question": question,
        "subquestions": subquestions,
        "report": report,
        "sources": all_sources,
        "num_sources": len(all_sources),
        "time_seconds": round(elapsed, 2),
    }


if __name__ == "__main__":
    test_question = "Should a startup use FastAPI or Django for a high-throughput API service?"
    result = run_multi_agent(test_question)

    print("=" * 60)
    print("QUESTION:", result["question"])
    print("=" * 60)
    print("SUB-QUESTIONS GENERATED:")
    for sq in result["subquestions"]:
        print(" -", sq)
    print("=" * 60)
    print(result["report"])
    print("=" * 60)
    print(f"Sources used: {result['num_sources']}")
    print(f"Time taken: {result['time_seconds']}s")
    