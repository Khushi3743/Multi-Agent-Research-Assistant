import streamlit as st
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from baseline import run_baseline
from multi_agent import run_multi_agent

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔍",
    layout="wide",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #0f1117; }

    .header-title {
        font-size: 2rem;
        font-weight: 600;
        color: #f0f0f0;
        margin-bottom: 0.2rem;
    }
    .header-sub {
        font-size: 0.95rem;
        color: #888;
        margin-bottom: 2rem;
    }

    .metric-box {
        background: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.4rem;
        font-weight: 500;
        color: #e0e0e0;
    }
    .metric-value.highlight { color: #4ade80; }

    .panel {
        background: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 10px;
        padding: 1.4rem;
        height: 100%;
    }
    .panel-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: #555;
        margin-bottom: 0.6rem;
    }
    .panel-title {
        font-size: 1rem;
        font-weight: 600;
        color: #c0c0c0;
        margin-bottom: 1rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #2a2d3a;
    }
    .tag {
        display: inline-block;
        background: #2a2d3a;
        color: #888;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .tag.green { background: #1a2e1a; color: #4ade80; }

    .subq {
        background: #13151f;
        border-left: 2px solid #3b4aff;
        padding: 0.5rem 0.8rem;
        border-radius: 0 4px 4px 0;
        font-size: 0.85rem;
        color: #aaa;
        margin-bottom: 0.4rem;
    }

    .stTextArea textarea {
        background: #1a1d27 !important;
        border: 1px solid #2a2d3a !important;
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background: #3b4aff;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 500;
        font-size: 0.95rem;
        width: 100%;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #2d39e0; }

    hr { border-color: #2a2d3a; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="header-title">Multi-Agent Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Baseline vs. multi-agent pipeline — live comparison</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
question = st.text_area(
    "Research question",
    placeholder="e.g. Should a startup use FastAPI or Django for a high-throughput API service?",
    height=90,
    label_visibility="collapsed",
)

col_btn, col_examples = st.columns([1, 3])
with col_btn:
    run = st.button("Run comparison")

with col_examples:
    st.markdown(
        '<div style="color:#555;font-size:0.8rem;padding-top:0.6rem;">'
        'Try: <i>PostgreSQL vs MongoDB for e-commerce</i> · '
        '<i>React vs Vue in 2026</i> · '
        '<i>AWS Lambda vs EC2 for Python apps</i>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Run ───────────────────────────────────────────────────────────────────────
if run and question.strip():

    st.markdown("<hr>", unsafe_allow_html=True)

    col_base, col_multi = st.columns(2)

    # ── Baseline column ──────────────────────────────────────────────────────
    with col_base:
        st.markdown('<div class="panel-label">APPROACH 1</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Single-LLM Baseline</div>', unsafe_allow_html=True)
        st.markdown("One web search → one LLM call → report")

        with st.spinner("Searching and generating..."):
            t0 = time.time()
            base_result = run_baseline(question)
            base_time = round(time.time() - t0, 1)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Sources</div>
                    <div class="metric-value">{base_result.get('num_sources', '—')}</div>
                </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Time</div>
                    <div class="metric-value">{base_time}s</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(base_result.get("report", "No answer returned."))

    # ── Multi-agent column ───────────────────────────────────────────────────
    with col_multi:
        st.markdown('<div class="panel-label">APPROACH 2</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Multi-Agent Pipeline</div>', unsafe_allow_html=True)
        st.markdown("Planner → Researcher (per sub-question) → Synthesizer")

        with st.spinner("Planning, researching, and synthesizing..."):
            t0 = time.time()
            multi_result = run_multi_agent(question)
            multi_time = round(time.time() - t0, 1)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Sources</div>
                    <div class="metric-value highlight">{multi_result.get('num_sources', '—')}</div>
                </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">Time</div>
                    <div class="metric-value">{multi_time}s</div>
                </div>""", unsafe_allow_html=True)

        # Sub-questions used
        sub_qs = multi_result.get("subquestions", [])
        if sub_qs:
            st.markdown("<br>**Sub-questions explored:**", unsafe_allow_html=True)
            for sq in sub_qs:
                st.markdown(f'<div class="subq">{sq}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(multi_result.get("report", "No answer returned."))

elif run and not question.strip():
    st.warning("Please enter a research question.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<div style="color:#444;font-size:0.78rem;text-align:center;">'
    'Built with Groq · Tavily · Streamlit &nbsp;|&nbsp; '
    '<a href="https://github.com/Khushi3743/Multi-Agent-Research-Assistant" '
    'style="color:#555;">GitHub</a>'
    '</div>',
    unsafe_allow_html=True,
)
