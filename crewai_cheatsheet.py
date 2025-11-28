# crewai_cheatsheet.py
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew
from crewai import LLM


# ---------- BASIC: one agent, one LLM ----------

def basic_crewai():
    llm = LLM(model="gpt-4o")  # auto-uses OPENAI_API_KEY
    agent = Agent(
        role="Helper",
        goal="Answer simple questions clearly",
        backstory="You are a friendly assistant.",
        llm=llm,
    )
    task = Task(
        description="Explain what LangChain is in 3 bullet points.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    print("BASIC RESULT:\n", result)


# ---------- ADVANCED: multi-agent pipeline ----------

def advanced_crewai():
    research_llm = LLM(model="gpt-4o-mini")
    writer_llm = LLM(model="gpt-4o")

    researcher = Agent(
        role="Researcher",
        goal="Gather technical insights about LLM frameworks",
        backstory="You read docs and summarize key points.",
        llm=research_llm,
    )

    writer = Agent(
        role="Technical Writer",
        goal="Create a concise GitHub README from research notes",
        backstory="You write clean, developer-friendly docs.",
        llm=writer_llm,
    )

    research_task = Task(
        description=(
            "List pros and cons of LangChain, LangGraph, CrewAI and AutoGen "
            "for building agentic workflows."
        ),
        expected_output="Bullet list of pros and cons for each framework.",
        agent=researcher,
    )

    write_task = Task(
        description=(
            "Using the research notes, draft a README section titled "
            "'Choosing a Framework' in markdown."
        ),
        expected_output="Markdown section with headings and bullet points.",
        agent=writer,
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        verbose=True,
        process="sequential",
    )

    result = crew.kickoff()
    print("\nADVANCED RESULT:\n", result)


if __name__ == "__main__":
    print("=== BASIC CREWAI ===")
    basic_crewai()

    print("\n=== ADVANCED MULTI-AGENT CREW ===")
    advanced_crewai()
