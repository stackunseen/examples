"""A scripted model and stub specialists, so the practice runs offline with no API key.

ScriptedModel plays back fixed steps and keeps a copy of the history it was shown on each
turn, which is how the checks see what the supervisor told it. Anything with
next_step(history) -> Step can take its place, a real model included.
"""

from __future__ import annotations

from supervisor import Step

# A run that never stops would hang the checks, so past this many turns the scripted model
# gives up loudly instead.
RUNAWAY = 50


class ScriptedModel:
    """Plays back the given steps in order, then `repeat` for ever if given, else answers."""

    def __init__(self, *steps: Step, repeat: Step | None = None) -> None:
        self._steps = list(steps)
        self._repeat = repeat
        self.seen: list[list[str]] = []

    def next_step(self, history: list[str]) -> Step:
        self.seen.append(list(history))
        if len(self.seen) > RUNAWAY:
            raise RuntimeError(
                f"The supervisor asked the model {RUNAWAY} times and kept going. "
                "Is there a turn budget?"
            )
        if self._steps:
            return self._steps.pop(0)
        if self._repeat is not None:
            return self._repeat
        return Step("answer", text="(the script ran out of steps)")


def research(query: str) -> str:
    """A stub search. A real one would query an index and return passages with sources."""
    return f"3 passages on '{query}' [doc-12, doc-31, doc-40]"


def analysis(findings: str) -> str:
    """A stub analyst. A real one would be a model call that writes a short, cited answer."""
    return f"Summary of: {findings}"


def specialists() -> dict:
    return {"research": research, "analysis": analysis}


def make_actions() -> tuple[dict, list[str]]:
    """send_email is the one action that changes something outside.

    The outbox shows what actually went out.
    """
    outbox: list[str] = []

    def send_email(text: str) -> str:
        outbox.append(text)
        return f"Email sent: {text}"

    return {"send_email": send_email}, outbox
