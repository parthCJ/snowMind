from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from snowmind.orchestration.state_graph import build_graph

HISTORY_PATH = PROJECT_ROOT / "data" / "app" / "query_history.json"
FEEDBACK_PATH = PROJECT_ROOT / "data" / "app" / "feedback_log.jsonl"


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(history: list[dict]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")


def append_feedback(entry: dict) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FEEDBACK_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


st.set_page_config(page_title="SnowMind", page_icon="❄️", layout="wide")
st.title("SnowMind - Multi-Agent AI Assistant on Snowflake")

if "history" not in st.session_state:
    st.session_state.history = load_history()

if "last_result" not in st.session_state:
    st.session_state.last_result = None

col_left, col_right = st.columns([0.8, 0.2])
with col_left:
    st.caption(
        "Natural language routing across structured tables and knowledge retrieval"
    )
with col_right:
    if st.button("Clear History"):
        st.session_state.history = []
        save_history(st.session_state.history)
        st.session_state.last_result = None
        st.rerun()

query = st.text_input(
    "Ask a business question", placeholder="What were last month's sales by region?"
)
run = st.button("Run", type="primary")

if run and query:
    app = build_graph()
    result = app.invoke(
        {
            "query": query,
            "intent": "unstructured",
            "analyst_result": "",
            "search_result": "",
            "analyst_source": "",
            "search_source": "",
            "source": "",
            "final_answer": "",
        }
    )

    item = {
        "id": str(len(st.session_state.history) + 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "intent": result.get("intent", ""),
        "answer": result.get("final_answer", "No response."),
        "source": result.get("source", "unknown"),
    }
    st.session_state.history.append(item)
    st.session_state.last_result = item
    save_history(st.session_state.history)

if st.session_state.last_result:
    current = st.session_state.last_result
    st.subheader("Latest Response")
    st.info(f"Source: {current.get('source', 'unknown')}")
    st.markdown(f"**Query:** {current['query']}")
    st.markdown(f"**Answer:** {current['answer']}")
    fb_cols = st.columns([0.2, 0.2, 0.6])
    with fb_cols[0]:
        if st.button("Helpful", key="fb_helpful"):
            append_feedback(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "query": current["query"],
                    "source": current.get("source", "unknown"),
                    "rating": "helpful",
                }
            )
            st.success("Feedback saved")
    with fb_cols[1]:
        if st.button("Not Helpful", key="fb_not_helpful"):
            append_feedback(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "query": current["query"],
                    "source": current.get("source", "unknown"),
                    "rating": "not_helpful",
                }
            )
            st.warning("Feedback saved")

if st.session_state.history:
    st.subheader("Query History")
    for idx, item in enumerate(reversed(st.session_state.history), start=1):
        st.markdown(f"**{idx}. Query:** {item['query']}")
        st.caption(f"Timestamp: {item.get('timestamp', 'n/a')}")
        st.markdown(f"**Intent:** {item['intent']}")
        st.markdown(f"**Source:** {item.get('source', 'unknown')}")
        st.markdown(f"**Answer:** {item['answer']}")
        st.markdown("---")

st.caption("Tip: Configure Cortex API endpoints in .env before using production calls.")
