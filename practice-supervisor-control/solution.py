"""One way to keep the supervisor in control. Have a go at supervisor.py first.

PRACTICE_SOLUTION=1 python -m unittest -v runs the checks against this file.
"""

from __future__ import annotations

from typing import Callable

from supervisor import Model, Run, Step


def run_supervisor(
    task: str,
    model: Model,
    specialists: dict[str, Callable[[str], str]],
    actions: dict[str, Callable[[str], str]],
    approve: Callable[[Step], bool],
    max_turns: int = 6,
) -> Run:
    history = [f"Task: {task}"]
    trace: list[tuple[str, str]] = []
    turns = 0
    while True:
        # The budget is checked before the model is asked again, so no run takes more
        # than max_turns turns.
        if turns >= max_turns:
            trace.append(("stopped", "budget"))
            return Run("budget_exhausted", None, turns, trace)

        step = model.next_step(history)
        turns += 1

        if step.kind == "answer":
            trace.append(("answer", ""))
            return Run("answered", step.text, turns, trace)

        if step.kind == "call":
            specialist = specialists.get(step.name)
            if specialist is None:
                # A made-up name goes back to the model as something it can act on,
                # not as an exception.
                trace.append(("unknown", step.name))
                choices = ", ".join(sorted(specialists))
                history.append(f"No specialist called {step.name}. Choose from: {choices}.")
                continue
            trace.append(("call", step.name))
            history.append(f"{step.name} returned: {specialist(step.text)}")
            continue

        if step.kind == "act":
            action = actions.get(step.name)
            if action is None:
                trace.append(("unknown", step.name))
                history.append(f"No action called {step.name}.")
                continue
            # Approval comes first: nothing outside changes until someone, or a policy,
            # says yes.
            if not approve(step):
                trace.append(("denied", step.name))
                history.append(f"{step.name} was not approved, so it did not run.")
                continue
            trace.append(("ran", step.name))
            history.append(f"{step.name} ran: {action(step.text)}")
