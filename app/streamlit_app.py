import streamlit as st

from snowmind.orchestration.state_graph import build_graph

st.set_page_config(page_title="SnowMind", page_icon="❄️", layout="wide")
st.title("SnowMind - Multi-Agent AI Assistant on Snowflake")

if "history" not in st.session_state:
    st.session_state.history = []

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

    st.session_state.history.append(
        {
            "query": query,
            "intent": result.get("intent", ""),
            "answer": result.get("final_answer", "No response."),
            "source": result.get("source", "unknown"),
        }
    )

if st.session_state.history:
    st.subheader("Query History")
    for idx, item in enumerate(reversed(st.session_state.history), start=1):
        st.markdown(f"**{idx}. Query:** {item['query']}")
        st.markdown(f"**Intent:** {item['intent']}")
        st.markdown(f"**Source:** {item.get('source', 'unknown')}")
        st.markdown(f"**Answer:** {item['answer']}")
        st.markdown("---")

st.caption("Tip: Configure Cortex API endpoints in .env before using production calls.")
