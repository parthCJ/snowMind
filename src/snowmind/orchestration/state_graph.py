from typing import Literal, TypedDict
import requests
from langgraph.graph import END, StateGraph

from snowmind.config import settings
from snowmind.tools.snowflake_fallback import analyst_fallback, search_fallback


class AgentState(TypedDict):
    query: str
    intent: Literal["structured", "unstructured"]
    analyst_result: str
    search_result: str
    analyst_source: str
    search_source: str
    source: str
    final_answer: str


def intent_classifier(state: AgentState) -> AgentState:
    query = state["query"].lower()
    data_terms = ["sales", "revenue", "count", "orders", "users", "last month"]
    state["intent"] = (
        "structured" if any(t in query for t in data_terms) else "unstructured"
    )
    return state


def route_to_analyst(state: AgentState) -> AgentState:
    if settings.analyst_endpoint and settings.api_token:
        try:
            payload = {"query": state["query"]}
            headers = {"Authorization": f"Bearer {settings.api_token}"}
            resp = requests.post(
                settings.analyst_endpoint, json=payload, headers=headers, timeout=30
            )
            resp.raise_for_status()
            state["analyst_result"] = resp.text
            state["analyst_source"] = "cortex_analyst_api"
            return state
        except Exception as exc:
            state["analyst_result"] = (
                f"Analyst API failed, using SQL fallback. Details: {exc}\n\n{analyst_fallback(state['query'])}"
            )
            state["analyst_source"] = "snowflake_sql_fallback"
            return state

    state["analyst_result"] = analyst_fallback(state["query"])
    state["analyst_source"] = "snowflake_sql_fallback"
    return state


def route_to_search(state: AgentState) -> AgentState:
    if settings.search_endpoint and settings.api_token:
        try:
            payload = {"query": state["query"], "top_k": 5}
            headers = {"Authorization": f"Bearer {settings.api_token}"}
            resp = requests.post(
                settings.search_endpoint, json=payload, headers=headers, timeout=30
            )
            resp.raise_for_status()
            state["search_result"] = resp.text
            state["search_source"] = "cortex_search_api"
            return state
        except Exception as exc:
            state["search_result"] = (
                f"Search API failed, using KB fallback. Details: {exc}\n\n{search_fallback(state['query'])}"
            )
            state["search_source"] = "knowledge_base_sql_fallback"
            return state

    state["search_result"] = search_fallback(state["query"])
    state["search_source"] = "knowledge_base_sql_fallback"
    return state


def response_synthesizer(state: AgentState) -> AgentState:
    if state.get("intent") == "structured":
        result = state.get("analyst_result", "")
        state["source"] = state.get("analyst_source", "unknown")
    else:
        result = state.get("search_result", "")
        state["source"] = state.get("search_source", "unknown")

    state["final_answer"] = f"{result}\n\nSource: {state['source']}"
    return state


def route_intent(state: AgentState) -> str:
    return (
        "route_to_analyst" if state.get("intent") == "structured" else "route_to_search"
    )


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("route_to_analyst", route_to_analyst)
    graph.add_node("route_to_search", route_to_search)
    graph.add_node("response_synthesizer", response_synthesizer)

    graph.set_entry_point("intent_classifier")
    graph.add_conditional_edges("intent_classifier", route_intent)
    graph.add_edge("route_to_analyst", "response_synthesizer")
    graph.add_edge("route_to_search", "response_synthesizer")
    graph.add_edge("response_synthesizer", END)

    return graph.compile()
