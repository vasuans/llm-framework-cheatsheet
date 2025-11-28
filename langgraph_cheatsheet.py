# langgraph_cheatsheet.py
from dotenv import load_dotenv
load_dotenv()

from typing import Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END


# ---------- BASIC: simple graph with one node ----------

class SimpleState(TypedDict):
    messages: list


def basic_node(state: SimpleState) -> SimpleState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    reply = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [reply]}


def run_basic():
    graph = StateGraph(SimpleState)
    graph.add_node("chat", basic_node)
    graph.set_entry_point("chat")
    graph.set_finish_point("chat")
    app = graph.compile()

    result = app.invoke({"messages": ["Explain LangGraph in 1 sentence."]})
    for m in result["messages"]:
        print(m)


# ---------- ADVANCED: router + 2 tools ----------

class RouterState(TypedDict):
    query: str
    answer: str


def router(state: RouterState) -> Literal["small", "big"]:
    q = state["query"].lower()
    if "quick" in q or len(q) < 60:
        return "small"
    return "big"


def small_answer(state: RouterState) -> RouterState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    res = llm.invoke(f"Answer in 1-2 sentences: {state['query']}")
    return {"query": state["query"], "answer": res.content}


def big_answer(state: RouterState) -> RouterState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
    res = llm.invoke(
        f"Give a detailed but clear answer (4-6 paragraphs): {state['query']}"
    )
    return {"query": state["query"], "answer": res.content}


def run_advanced():
    graph = StateGraph(RouterState)
    graph.add_node("router", router)
    graph.add_node("small", small_answer)
    graph.add_node("big", big_answer)

    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        lambda s: router(s),
        {"small": "small", "big": "big"},
    )
    graph.add_edge("small", END)
    graph.add_edge("big", END)

    app = graph.compile()

    q1 = "Quick: what is RAG?"
    out1 = app.invoke({"query": q1, "answer": ""})
    print("Q1:", q1)
    print("A1:", out1["answer"])

    q2 = "Explain how to design a production-grade RAG system with LangChain and LangGraph."
    out2 = app.invoke({"query": q2, "answer": ""})
    print("\nQ2:", q2)
    print("A2:", out2["answer"])


if __name__ == "__main__":
    print("=== BASIC LANGGRAPH ===")
    run_basic()

    print("\n=== ADVANCED ROUTER GRAPH ===")
    run_advanced()
