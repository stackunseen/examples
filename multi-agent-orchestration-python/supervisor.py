"""A supervisor with two specialists on the OpenAI Python SDK, with no agent framework.

The supervisor is a loop your code owns: the model picks the next tool, the code runs it, and the code decides when to
stop. Each specialist is a tool backed by its own model call with its own instructions, so control comes back to the
supervisor after every step.
"""

import inspect
import json
import os

from openai import AzureOpenAI, OpenAI

# On Azure OpenAI, MODEL is your deployment name.
MODEL = os.environ.get("MODEL", "gpt-4o-mini")
# A run that needs more than a handful of turns is looping; stop it instead of paying for it.
MAX_TURNS = 8


def make_client():
    """Azure OpenAI when an endpoint is configured (it reads AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY),
    otherwise the OpenAI API (it reads OPENAI_API_KEY)."""
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        return AzureOpenAI(api_version=os.environ.get("OPENAI_API_VERSION", "2024-10-21"))
    return OpenAI()


llm = make_client()


def search_docs(query: str) -> str:
    """Search internal documentation and return passages with their source IDs."""
    # Replace with a real retrieval call. Keep the source IDs so the analysis can cite them.
    return (
        "[doc-12] Evaluate retrieval and generation separately. "
        "[doc-31] Keep a golden set of real questions and run it on every change."
    )


def ask(instructions: str, content: str) -> str:
    """One model call with its own instructions: all a specialist is, once the framework is gone."""
    response = llm.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": instructions}, {"role": "user", "content": content}],
    )
    return response.choices[0].message.content or ""


def research(question: str) -> str:
    """Find evidence, with source IDs, for a question."""
    return ask(
        "You find evidence. From the passages given, return the ones relevant to the question with their source IDs. "
        "Do not answer the question yourself. If nothing is relevant, say so plainly.",
        f"Question: {question}\n\nPassages:\n{search_docs(question)}",
    )


def analysis(findings: str) -> str:
    """Turn research findings into a cited, structured answer."""
    return ask(
        "You turn research findings into a short structured answer: at most three points, each citing a source ID. "
        "Use only the findings you are given. If they do not support an answer, say what is missing.",
        findings,
    )


SPECIALISTS = {"research": research, "analysis": analysis}


def tool(name: str, description: str, argument: str) -> dict:
    """A tool definition with one required string argument."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": {argument: {"type": "string"}}, "required": [argument]},
        },
    }


TOOLS = [
    tool("research", "Find evidence, with source IDs, for a question.", "question"),
    tool("analysis", "Turn research findings into a cited, structured answer.", "findings"),
]

SUPERVISOR = (
    "You coordinate and never answer from your own knowledge. "
    "First call research with the user's question. Then call analysis with the findings. "
    "Return the analysis to the user."
)


def supervise(question: str) -> str:
    messages = [{"role": "system", "content": SUPERVISOR}, {"role": "user", "content": question}]
    for _ in range(MAX_TURNS):
        message = llm.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        if not message.tool_calls:
            return message.content or ""
        messages.append(message.model_dump(exclude_none=True))
        for call in message.tool_calls:
            # The code, not the model, decides what runs: unknown tools and malformed arguments are refused.
            name = call.function.name
            specialist = SPECIALISTS.get(name)
            try:
                args = json.loads(call.function.arguments)
                inspect.signature(specialist).bind(**args)  # missing or unexpected arguments raise TypeError
            except (json.JSONDecodeError, TypeError, ValueError):
                args = None
            if specialist is None:
                output = f"Unknown tool: {name}"
            elif args is None:
                output = f"Invalid arguments for {name}"
            else:
                output = specialist(**args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": output})
    raise RuntimeError(f"Stopped after {MAX_TURNS} turns without an answer.")


if __name__ == "__main__":
    print(supervise("What are the best practices for RAG?"))
