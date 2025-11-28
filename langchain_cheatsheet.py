# langchain_cheatsheet.py
from dotenv import load_dotenv
load_dotenv()

import os
from typing import List

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI
from langchain_cohere import ChatCohere

from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Optional RAG pieces
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader


def get_openai():
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def get_anthropic():
    return ChatAnthropic(
        model="claude-3-opus-20240229",
        temperature=0.2,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )


def get_google():
    # Requires GOOGLE_API_KEY or default GCP auth
    return ChatVertexAI(
        model="chat-bison",
        temperature=0.2,
    )


def get_cohere():
    return ChatCohere(
        model="command",
        temperature=0.2,
        api_key=os.getenv("COHERE_API_KEY"),
    )


# ---------- BASIC: single call examples ----------

def basic_examples():
    openai = get_openai()
    anthropic = get_anthropic()
    google = get_google()
    cohere = get_cohere()

    print("OpenAI:", openai.invoke("Say hi in one sentence."))
    print("Anthropic:", anthropic.invoke("Give one quick productivity tip."))
    print("Google:", google.invoke("Explain AI to a 10 year old in 2 sentences."))
    print("Cohere:", cohere.invoke("Suggest a weekend project in 1 line."))


# ---------- ADVANCED 1: streaming responses ----------

def stream_openai():
    llm = get_openai()
    for chunk in llm.stream("Stream a 3-sentence story about a robot learning to cook."):
        print(chunk.content, end="", flush=True)
    print()


# ---------- ADVANCED 2: structured output ----------

class TodoItem(BaseModel):
    title: str = Field(..., description="Short task name")
    urgency: int = Field(..., description="1-5, 5 is highest")
    tags: List[str] = Field(default_factory=list)


def structured_openai():
    llm = get_openai().with_structured_output(TodoItem)
    todo = llm.invoke(
        "Create one todo for improving my Python skills. "
        "Return urgency between 1 and 5 and some tags."
    )
    print(todo)
    print("Title:", todo.title)
    print("Urgency:", todo.urgency)


# ---------- ADVANCED 3: tools / function calling ----------

@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def upper(text: str) -> str:
    """Uppercase a string."""
    return text.upper()


def tools_openai():
    llm = get_openai().bind_tools([add, upper])
    msg = llm.invoke(
        "Call the add tool with 3 and 7, then call upper on the sentence "
        "'sum is <result>'. Only use tools, don't explain."
    )
    print(msg)


# ---------- ADVANCED 4: mini RAG (retrieve + answer) ----------

def build_rag_store(path: str = "sample_docs.txt"):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(
                "LangChain is a framework for building applications with LLMs.\n"
                "LangGraph adds graph-based control over LLM flows.\n"
                "CrewAI and AutoGen help build multi-agent workflows.\n"
            )
    docs = TextLoader(path).load()
    vs = FAISS.from_documents(docs, OpenAIEmbeddings())
    return vs


def rag_answer(question: str):
    vs = build_rag_store()
    retriever = vs.as_retriever(k=3)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You answer from the given context only."),
            ("human", "Question: {question}\n\nContext:\n{context}"),
        ]
    )

    chain = (
        {
            "context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
            "question": lambda x: x["question"],
        }
        | prompt
        | get_openai()
        | StrOutputParser()
    )

    answer = chain.invoke({"question": question})
    print("Q:", question)
    print("A:", answer)


if __name__ == "__main__":
    print("=== BASIC LANGCHAIN ===")
    basic_examples()

    print("\n=== STREAMING ===")
    stream_openai()

    print("\n=== STRUCTURED OUTPUT ===")
    structured_openai()

    print("\n=== TOOLS / FUNCTION CALLING ===")
    tools_openai()

    print("\n=== MINI RAG ===")
    rag_answer("What is LangGraph in simple words?")
