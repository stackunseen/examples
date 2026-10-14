"""Practice: keep a supervisor in control.

A supervisor asks the model what to do next, hands the work to a specialist and feeds
the result back, until the model answers. Getting that loop to run is the easy part.
The three things that make it safe to leave running are yours to write:

  TODO 1  Hand the work to the specialist the model names; give the model what came back.
  TODO 2  Stop at the turn budget, however keen the model is to carry on.
  TODO 3  Run an action that changes something outside only when approve() says yes.

Record each step in the trace as you go; it is what you read when a run goes wrong.

  What happened                         Trace entry
  a specialist was called               ("call", name)
  the model named no such specialist    ("unknown", name)
  an approved action ran                ("ran", name)
  an action was refused                 ("denied", name)
  the model answered                    ("answer", "")
  the turn budget ran out               ("stopped", "budget")

Check your work:  python -m unittest -v
The model is scripted (fake_model.py), so this runs offline with no API key.
solution.py has one way to do it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal, Protocol


@dataclass
class Step:
    """What the model wants next: call a specialist, take an action, or answer."""

    kind: Literal["call", "act", "answer"]
    name: str = ""  # the specialist or the action
    text: str = ""  # what to pass on, or the answer


class Model(Protocol):
    def next_step(self, history: list[str]) -> Step: ...


@dataclass
class Run:
    status: Literal["answered", "budget_exhausted"]
    answer: str | None
    turns: int
    trace: list[tuple[str, str]] = field(default_factory=list)


def run_supervisor(
    task: str,
    model: Model,
    specialists: dict[str, Callable[[str], str]],
    actions: dict[str, Callable[[str], str]],
    approve: Callable[[Step], bool],
    max_turns: int = 6,
) -> Run:
    """Work on the task until the model answers or the turn budget runs out.

    One turn is one call to the model.
    """
    history = [f"Task: {task}"]
    trace: list[tuple[str, str]] = []
    turns = 0
    while True:
        # TODO 2: once the model has had max_turns turns, stop. Record ("stopped", "budget")
        #         and return a Run with status "budget_exhausted" and no answer.

        step = model.next_step(history)
        turns += 1

        if step.kind == "answer":
            trace.append(("answer", ""))
            return Run("answered", step.text, turns, trace)

        if step.kind == "call":
            # TODO 1: run the specialist called step.name on step.text, record ("call", name)
            #         and add what it returned to history, so the model sees it next turn.
            #         A name that is not a specialist must not crash the run: record
            #         ("unknown", name) and say so in history, so the model can choose again.
            raise NotImplementedError("TODO 1: hand the work to the specialist")

        if step.kind == "act":
            # TODO 3: ask approve(step) before anything runs. If it says yes, run the action
            #         and record ("ran", name). If it says no, run nothing, record
            #         ("denied", name) and tell the model in history.
            raise NotImplementedError("TODO 3: hold the action for approval")
