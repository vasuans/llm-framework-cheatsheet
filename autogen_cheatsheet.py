# autogen_cheatsheet.py
from dotenv import load_dotenv
load_dotenv()

import os
from autogen import AssistantAgent, UserProxyAgent


# ---------- BASIC: one assistant ----------

def basic_autogen():
    user = UserProxyAgent("user")

    assistant = AssistantAgent(
        "assistant_openai",
        llm_config={
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    )

    res = user.initiate_chat(
        assistant,
        message="Explain LangGraph in 3 bullet points.",
        max_turns=2,
    )
    print("BASIC RESPONSE:\n", res)


# ---------- ADVANCED: two assistants collaborating ----------

def advanced_autogen():
    user = UserProxyAgent("user")

    researcher = AssistantAgent(
        "researcher",
        llm_config={
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        system_message=(
            "You are a senior ML engineer. "
            "Research and propose an outline."
        ),
    )

    writer = AssistantAgent(
        "writer",
        llm_config={
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        system_message=(
            "You are a technical writer. "
            "Turn outlines into polished markdown."
        ),
    )

    # Step 1: user -> researcher
    outline = user.initiate_chat(
        researcher,
        message=(
            "Create a detailed outline for a GitHub README titled "
            "'LLM Framework Cheatsheet with LangChain, LangGraph, CrewAI, AutoGen'."
        ),
        max_turns=2,
    )
    print("OUTLINE FROM RESEARCHER:\n", outline, "\n")

    # Step 2: user forwards to writer
    final_doc = user.initiate_chat(
        writer,
        message=(
            "Using this outline, write the README in markdown:\n\n"
            f"{outline}"
        ),
        max_turns=3,
    )

    print("FINAL MARKDOWN FROM WRITER:\n", final_doc)


if __name__ == "__main__":
    print("=== BASIC AUTOGEN ===")
    basic_autogen()

    print("\n=== ADVANCED MULTI-AGENT AUTOGEN ===")
    advanced_autogen()
