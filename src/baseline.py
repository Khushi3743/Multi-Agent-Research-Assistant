"""
Baseline: single-LLM-call research system.
Given a question, it does ONE web search, then ONE LLM call to write a report.
This is the comparison point for the multi-agent system built later.

Run with: python src/baseline.py
"""

import os
import time
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "openai/gpt-oss-20b"


def run_baseline(question: str) -> dict:
    """
    Runs the single-call baseline pipeline on one question.
    Returns a dict with the report text, sources used, and timing.
    """
    start_time = time.time()

    # Step 1: one web search covering the whole question
    search_results = tavily_client.search(query=question, max_results=5)
    sources = search_results["results"]

    # Step 2: build context from search results
    context = "\n\n".join(
        f"Source: {s['title']}\nURL: {s['url']}\nContent: {s['content']}"
        for s in sources
    )

    # Step 3: one LLM call to write the report
    prompt = f"""You are a research assistant. Answer the following question using ONLY the sources provided below. Cite sources by their URL when you use information from them.

Question: {question}

Sources:
{context}

Write a clear, well-organized report answering the question. Include a "Sources" section at the end listing the URLs you used."""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    report = response.choices[0].message.content
    elapsed = time.time() - start_time

    return {
        "question": question,
        "report": report,
        "sources": [s["url"] for s in sources],
        "num_sources": len(sources),
        "time_seconds": round(elapsed, 2),
    }


if __name__ == "__main__":
    test_question = "Should a startup use FastAPI or Django for a high-throughput API service?"
    result = run_baseline(test_question)

    print("=" * 60)
    print("QUESTION:", result["question"])
    print("=" * 60)
    print(result["report"])
    print("=" * 60)
    print(f"Sources used: {result['num_sources']}")
    print(f"Time taken: {result['time_seconds']}s")