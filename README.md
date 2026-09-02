# Multi-Agent Research Assistant

A Python system that compares two architectures for answering research questions — a single-LLM baseline versus a multi-agent pipeline with specialized agents — and benchmarks them across quality, source coverage, and latency.

Built to explore how agent decomposition affects output quality in LLM-powered systems.

---

## What It Does

You give it a research question. It answers it two ways — then tells you which approach did better and why.

**Baseline (single-LLM):** One web search → one LLM call → cited report  
**Multi-agent pipeline:** Planner breaks the question into sub-questions → Researcher searches each one separately → Synthesizer writes a structured, cited report

---

## Architecture

```
User Question
     │
     ├──► BASELINE ──────────────────────────────────────────────────────┐
     │         │                                                          │
     │    Web Search (1×)  →  LLM Call (1×)  →  Cited Report            │
     │                                                                    │
     └──► MULTI-AGENT PIPELINE ─────────────────────────────────────────┘
               │
          PLANNER AGENT
          Breaks question into 3-4 focused sub-questions
               │
          RESEARCHER AGENT (runs per sub-question)
          Web search for each sub-question → extracts sources & findings
               │
          SYNTHESIZER AGENT
          Combines all findings → structured report with citations
```

**Stack:** Python · Groq (LLaMA 3) · Tavily Search API · python-dotenv

---

## Key Findings

Benchmarked across 9 questions spanning technical comparisons, business decisions, and career advice:

| Metric | Baseline | Multi-Agent | Delta |
|--------|----------|-------------|-------|
| Avg sources used | 5.0 | 12.0 | **+140%** |
| Avg comprehensiveness (LLM-judged, /10) | 8.0 | 8.44 | +0.44 |
| Avg clarity (LLM-judged, /10) | 8.44 | 8.67 | +0.23 |
| Avg response time | 10.86s | 32.96s | 3× slower |

**Conclusion:** Agent decomposition dramatically improves source coverage (2.4×) with modest quality gains at roughly 3× the latency cost. For moderately complex questions, the tradeoff favors the baseline; for genuinely multi-faceted research questions, the multi-agent approach justifies the overhead.

---

## Project Structure

```
multi-agent-research-assistant/
├── src/
│   ├── baseline.py        # Single-LLM pipeline
│   ├── multi_agent.py     # Multi-agent pipeline (planner + researcher + synthesizer)
│   ├── evaluate.py        # Evaluation harness with LLM-as-judge scoring
│   └── questions.py       # 9-question benchmark set
├── results.json           # Full evaluation output
├── requirements.txt
├── .env                   # API keys (not committed)
└── .gitignore
```

---

## How to Run

**1. Clone and set up environment**
```bash
git clone https://github.com/Khushi3743/Multi-Agent-Research-Assistant.git
cd Multi-Agent-Research-Assistant
python -m venv venv
.\venv\Scripts\activate       # Windows
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**2. Add your API keys**

Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Get keys free at: [console.groq.com](https://console.groq.com) · [app.tavily.com](https://app.tavily.com)

**3. Verify setup**
```bash
python test_setup.py
```

**4. Run a single question**
```bash
python src/baseline.py        # Single-LLM approach
python src/multi_agent.py     # Multi-agent approach
```

**5. Run full evaluation**
```bash
python src/evaluate.py        # Benchmarks both systems, saves to results.json
```

---

## Skills Demonstrated

- **Agentic system design** — decomposing a task into specialized agents (planner, researcher, synthesizer)
- **LLM integration** — Groq API with LLaMA 3, prompt engineering for structured outputs
- **Evaluation methodology** — LLM-as-judge scoring, quantitative benchmarking across multiple metrics
- **API integration** — Tavily Search for real-time web retrieval
- **Python engineering** — modular code structure, environment management, JSON state persistence

---

## Technologies

| Tool | Purpose |
|------|---------|
| Python 3.14 | Core language |
| Groq + LLaMA 3 | LLM inference (fast, free tier) |
| Tavily Search API | Real-time web search |
| python-dotenv | Secure API key management |

---

*Built as a hands-on exploration of multi-agent LLM architectures and their real-world tradeoffs.*
