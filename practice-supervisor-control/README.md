# Practice: keep a supervisor in control

A supervisor asks the model what to do next, hands the work to a specialist and feeds the result back until the model answers. Getting that loop to run is the easy part. This exercise is about the three things that make it safe to leave running:

1. **Hand-offs that come back.** The supervisor calls the specialist the model names and gives the model what it returned. A name that is not a specialist goes back to the model as a message, not a crash.
2. **A turn budget.** The run stops after `max_turns`, however keen the model is to carry on.
3. **An approval gate.** An action that changes something outside, here sending an email, runs only when `approve()` says yes.

Each step goes into a trace, which is what you read when a run goes wrong.

The model is scripted (`fake_model.py`) and the specialists are stubs, so everything runs offline with no API key. The supervisor is yours.

## Start

Open `supervisor.py` and fill in the three TODOs. Check your work as you go:

```bash
python -m unittest -v
```

Six checks run. The first passes before you start; the others say what is still missing. `pytest` runs the same checks if you have it.

## Hints

<details>
<summary>TODO 1: hand the work over</summary>

Look the name up in `specialists` with `.get()`, so a made-up name gives you `None` instead of a `KeyError`. Whatever the specialist returns has to go into `history`: that list is all the model sees, so a result that is not in it was never seen.
</details>

<details>
<summary>TODO 2: the turn budget</summary>

Check the budget at the top of the loop, before the model is asked again. Checking after the call lets one extra turn through.
</details>

<details>
<summary>TODO 3: the approval gate</summary>

Call `approve(step)` before the action, and run the action only inside the yes branch. Check 6 looks at the outbox while `approve()` is being asked, so an action that runs first and asks afterwards fails it.
</details>

## When you are done

`solution.py` has one way to do it. To run the same checks against it:

```bash
PRACTICE_SOLUTION=1 python -m unittest -v
```

Then look at [Multi-agent orchestration](../multi-agent-orchestration-python), which builds the same supervisor with the OpenAI Agents SDK, and find where its turn limit is set and where an approval step would go.
