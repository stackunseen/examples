from agents import Agent, Runner, function_tool


@function_tool
def search_docs(query: str) -> str:
    """Search internal documentation."""
    # Replace with a real retrieval call.
    return "Found relevant documentation..."


research_agent = Agent(
    name="ResearchAgent",
    instructions="Find relevant information using available tools.",
    tools=[search_docs],
)

analysis_agent = Agent(
    name="AnalysisAgent",
    instructions="Analyze findings and provide structured insights.",
)

supervisor = Agent(
    name="Supervisor",
    instructions="Coordinate the workflow between agents.",
    handoffs=[research_agent, analysis_agent],
)

result = Runner.run_sync(supervisor, "What are the best practices for RAG?")
print(result.final_output)
