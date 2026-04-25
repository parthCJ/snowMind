from typing import Literal, TypedDict
import requests
from langgraph.graph import END, StateGraph

from snowmind.config import settings


class AgentState(TypedDict):
    query: str
    intent: Literal["structured", "unstructured"]
    analyst_result: str
    search_result: str
    final_answer: str


def intent_classifier(state: AgentState) -> AgentState:
    query = state["query"].lower()
    data_terms = ["sales", "revenue", "count", "orders", "users", "last month"]
    state["intent"] = (
        "structured" if any(t in query for t in data_terms) else "unstructured"
    )
    return state


def route_to_analyst(state: AgentState) -> AgentState:
    if not settings.analyst_endpoint:
        state["analyst_result"] = "Cortex Analyst endpoint not configured."
        return state

    payload = {"query": state["query"]}
    headers = {"Authorization": f"Bearer {settings.api_token}"}
    resp = requests.post(
        settings.analyst_endpoint, json=payload, headers=headers, timeout=30
    )
    resp.raise_for_status()
    state["analyst_result"] = resp.text
    return state


def route_to_search(state: AgentState) -> AgentState:
    if not settings.search_endpoint:
        state["search_result"] = "Cortex Search endpoint not configured."
        return state

    payload = {"query": state["query"], "top_k": 5}
    headers = {"Authorization": f"Bearer {settings.api_token}"}
    resp = requests.post(
        settings.search_endpoint, json=payload, headers=headers, timeout=30
    )
    resp.raise_for_status()
    state["search_result"] = resp.text
    return state


def response_synthesizer(state: AgentState) -> AgentState:
    if state.get("intent") == "structured":
        state["final_answer"] = state.get("analyst_result", "")
    else:
        state["final_answer"] = state.get("search_result", "")
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
