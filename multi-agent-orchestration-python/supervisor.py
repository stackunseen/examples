"""A supervisor with two specialists, using the OpenAI Agents SDK.

The supervisor keeps control and calls each specialist as a tool: research first, then analysis, then it decides what
the user sees. A handoff would pass control to the specialist and never come back, so it cannot run a two-step plan.
"""

from agents import Agent, Runner, function_tool


@function_tool
def search_docs(query: str) -> str:
    """Search internal documentation and return passages with their source IDs."""
    # Replace with a real retrieval call. Keep the source IDs so the analysis can cite them.
    return (
        "[doc-12] Evaluate retrieval and generation separately. "
        "[doc-31] Keep a golden set of real questions and run it on every change."
    )


research_agent = Agent(
    name="ResearchAgent",
    instructions=(
        "You find evidence. Call search_docs with the question and return the relevant passages with their source IDs. "
        "Do not answer the question yourself. If nothing relevant comes back, say so plainly."
    ),
    tools=[search_docs],
)

analysis_agent = Agent(
    name="AnalysisAgent",
    instructions=(
        "You turn research findings into a short structured answer: at most three points, each citing a source ID. "
        "Use only the findings you are given. If they do not support an answer, say what is missing."
    ),
)

supervisor = Agent(
    name="Supervisor",
    instructions=(
        "You coordinate and never answer from your own knowledge. "
        "First call research with the user's question. Then call analysis with the findings. "
        "Return the analysis to the user."
    ),
    tools=[
        research_agent.as_tool(
            tool_name="research",
            tool_description="Find evidence, with source IDs, for a question.",
        ),
        analysis_agent.as_tool(
            tool_name="analysis",
            tool_description="Turn research findings into a cited, structured answer.",
        ),
    ],
)

if __name__ == "__main__":
    # A run that needs more than a handful of turns is looping; stop it instead of paying for it.
    result = Runner.run_sync(supervisor, "What are the best practices for RAG?", max_turns=8)
    print(result.final_output)
