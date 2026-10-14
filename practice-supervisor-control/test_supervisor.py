"""The checks for supervisor.py. Run them with:  python -m unittest -v

Each check says what the supervisor must do. The first passes before you start;
work down from TODO 1. PRACTICE_SOLUTION=1 runs the same checks against solution.py.
"""

import os
import unittest

import fake_model
from fake_model import ScriptedModel, make_actions, specialists
from supervisor import Step

if os.environ.get("PRACTICE_SOLUTION"):
    from solution import run_supervisor
else:
    from supervisor import run_supervisor


def answers(yes: bool):
    return lambda step: yes


def supervise(task: str, model: ScriptedModel, approve=answers(True), max_turns: int = 6):
    """Runs the supervisor with the stub specialists. Returns the run and the outbox."""
    actions, outbox = make_actions()
    run = run_supervisor(task, model, specialists(), actions, approve, max_turns=max_turns)
    return run, outbox


def said(model: ScriptedModel, turn: int) -> str:
    """Everything the supervisor had told the model by the given turn (1 is the first)."""
    return "\n".join(model.seen[turn - 1])


class SupervisorChecks(unittest.TestCase):
    def test_1_answers(self):
        """1. Returns the model's answer when it answers straight away"""
        model = ScriptedModel(Step("answer", text="The policy allows it."))
        run, _ = supervise("Can I book this hotel?", model)
        self.assertEqual(run.status, "answered")
        self.assertEqual(run.answer, "The policy allows it.")
        self.assertEqual(run.turns, 1)
        self.assertEqual(run.trace, [("answer", "")])

    def test_2_hands_off_and_reads_back(self):
        """2. Hands work to the specialists the model names and feeds back what they return"""
        model = ScriptedModel(
            Step("call", "research", "hotel policy"),
            Step("call", "analysis", "the passages"),
            Step("answer", text="Here is what the policy says."),
        )
        run, _ = supervise("What does the hotel policy say?", model)
        expected = [("call", "research"), ("call", "analysis"), ("answer", "")]
        self.assertEqual(run.trace, expected)
        self.assertIn(
            fake_model.research("hotel policy"),
            said(model, 2),
            "the model never saw what research returned",
        )
        self.assertIn(
            fake_model.analysis("the passages"),
            said(model, 3),
            "the model never saw what analysis returned",
        )
        self.assertEqual(run.status, "answered")

    def test_3_unknown_specialist(self):
        """3. Tells the model about a specialist that does not exist, instead of crashing"""
        model = ScriptedModel(
            Step("call", "planner", "plan the trip"),
            Step("answer", text="Done without a plan."),
        )
        run, _ = supervise("Plan the trip", model)
        self.assertEqual(run.trace, [("unknown", "planner"), ("answer", "")])
        self.assertIn("planner", said(model, 2), "tell the model there is no planner")
        self.assertEqual(run.status, "answered")

    def test_4_turn_budget(self):
        """4. Stops at the turn budget when the model never answers"""
        model = ScriptedModel(repeat=Step("call", "research", "more, always more"))
        run, _ = supervise("Research everything", model, max_turns=3)
        self.assertEqual(len(model.seen), 3, "ask the model at most max_turns times")
        self.assertEqual(run.status, "budget_exhausted")
        self.assertIsNone(run.answer)
        self.assertEqual(run.turns, 3)
        self.assertEqual(run.trace[-1], ("stopped", "budget"))

    def test_5_refused_action(self):
        """5. Runs nothing when approve() says no, and tells the model"""
        model = ScriptedModel(
            Step("act", "send_email", "Draft to legal"),
            Step("answer", text="Waiting for approval."),
        )
        run, outbox = supervise("Send the draft to legal", model, approve=answers(False))
        self.assertEqual(outbox, [], "the email went out without approval")
        self.assertEqual(run.trace, [("denied", "send_email"), ("answer", "")])
        self.assertIn("send_email", said(model, 2), "tell the model the action was refused")

    def test_6_approved_action(self):
        """6. Asks approve() before an action runs, then runs it once"""
        model = ScriptedModel(
            Step("act", "send_email", "Draft to legal"),
            Step("answer", text="Sent."),
        )
        # approve() looks at the real outbox while it is being asked, so sending first fails.
        actions, outbox = make_actions()
        outbox_when_asked: list[list[str]] = []

        def approve(step: Step) -> bool:
            outbox_when_asked.append(list(outbox))
            return True

        run = run_supervisor("Send the draft to legal", model, specialists(), actions, approve)
        self.assertEqual(outbox_when_asked, [[]], "ask approve() once, before anything is sent")
        self.assertEqual(outbox, ["Draft to legal"])
        self.assertEqual(run.trace, [("ran", "send_email"), ("answer", "")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
