import os

from crewai import LLM, Agent, Crew, Process, Task

from tools import kb_search, log_gap, web_search


def answer(query: str) -> tuple[str, str]:
    """Run the crew. Returns (answer, source) where source is 'Knowledge Base' or 'Fallback (web)'."""
    llm = LLM(model=os.getenv("MODEL", "gpt-4o-mini"))
    kb_agent = Agent(
        role="Company Knowledge Base Agent",
        goal="Answer customer queries strictly from the company documents.",
        backstory="You never use outside knowledge. If the search tool returns NOT_FOUND, you say NOT_FOUND.",
        tools=[kb_search], llm=llm, allow_delegation=False,
    )
    web_agent = Agent(
        role="Web Search Fallback Agent",
        goal="Answer queries the company documents could not, using web search.",
        backstory="You only search the web when the Knowledge Base agent reported NOT_FOUND.",
        tools=[web_search], llm=llm, allow_delegation=False,
    )
    log_agent = Agent(
        role="Query Logging Agent",
        goal="Record queries that needed web search so the business can fill its knowledge gaps.",
        backstory="You log only queries that were answered via web search.",
        tools=[log_gap], llm=llm, allow_delegation=False,
    )
    t1 = Task(
        description="Customer query: {query}\nUse the Knowledge Base Search tool. Answer ONLY from its output. "
        "If it returns NOT_FOUND, reply with exactly: NOT_FOUND",
        expected_output="A grounded answer, or exactly NOT_FOUND.", agent=kb_agent,
    )
    t2 = Task(
        description="Customer query: {query}\nIf the previous answer is exactly NOT_FOUND, search the web and write an "
        "accurate, concise answer citing the source URL. Otherwise repeat the previous answer unchanged, without searching.",
        expected_output="The final answer for the customer.", agent=web_agent, context=[t1],
    )
    t3 = Task(
        description="Customer query: {query}\nIf the first answer was NOT_FOUND (so the web was used), call Gap Log Writer "
        "with the query and web_searched=true. Otherwise call it with web_searched=false.",
        expected_output="Confirmation of logging.", agent=log_agent, context=[t1],
    )
    crew = Crew(agents=[kb_agent, web_agent, log_agent], tasks=[t1, t2, t3], process=Process.sequential)
    result = crew.kickoff(inputs={"query": query})
    fell_back = "NOT_FOUND" in result.tasks_output[0].raw
    return result.tasks_output[1].raw, "Fallback (web)" if fell_back else "Knowledge Base"
