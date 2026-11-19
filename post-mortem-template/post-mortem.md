# Post-mortem: <one line on what users saw, not on the cause>

<!-- Blameless: describe what people knew and did at the time, and why it made sense to them then.
     Name systems, changes and decisions, never a person as the cause. If a sentence would make
     someone defensive in the review, rewrite it around the process that let it happen. -->

| | |
|---|---|
| Status | Draft / In review / Final |
| Incident date | YYYY-MM-DD |
| Severity | SEV1 / SEV2 / SEV3 (use your own scale) |
| Authors | |
| Incident lead | |
| Review meeting | YYYY-MM-DD |
| Tickets | |

## Summary

<!-- Three or four sentences that someone outside the team can read on their own:
     what users experienced, for how long, what caused it, and what fixed it. Write it last. -->

## Impact

<!-- Numbers where you have them, and say how you got them. Where you do not, say so. -->

- Who was affected:
- What they could not do, or what went wrong for them:
- Duration of user impact (start to full recovery):
- Data lost, corrupted or exposed:
- Commitments affected (SLOs, contracts, regulatory notifications):

## Key times

<!-- All times in one stated time zone. These four gaps are what the actions should shrink. -->

| Measure | Time | Gap |
|---|---|---|
| Problem started | | |
| Detected | | Time to detect: |
| Incident declared | | Time to decide: |
| Impact mitigated | | Time to mitigate: |
| Fully resolved | | |

How it was detected: <!-- An alert, a dashboard someone happened to look at, a customer, a colleague?
     If a person noticed before a system did, that is a finding in its own right. -->

## Timeline

<!-- What happened and what people believed at each point. Include the dead ends: the hypothesis
     that cost forty minutes teaches as much as the one that was right. -->

| Time | What happened | What we believed then |
|---|---|---|
| | | |

## What happened

<!-- The mechanism, in plain technical terms. Start from the change or condition that set it off,
     then follow the failure through the system to what users saw. -->

## How we responded

<!-- What the responders did, in order, and why: what they tried first, what worked, what made it worse,
     and who decided to roll back, fail over or wait. Gaps here usually point at a missing runbook or
     unclear decision rights. -->

- What was tried, and what happened:
- What finally stopped the impact:
- Who made the call, and what they needed to make it:

## Communication

<!-- Who was told, when and through which channel. Record it even when nothing was sent:
     staying silent was a decision too. -->

| When | Audience | Channel | What was said |
|---|---|---|---|
| | Customers / Internal / Leadership / Regulator | Status page / Email / Chat | |

## Why it was possible

<!-- Contributing factors, not one root cause. Answer each question; most incidents have an answer to all of them. -->

- The assumption that turned out to be wrong:
- Why nothing stopped the change or condition (tests, reviews, gates, limits):
- Why detection took as long as it did:
- Why mitigation took as long as it did (access, runbooks, rollback, decision rights):
- Anything that made the impact larger than it needed to be:

## Has this happened before?

<!-- Search earlier post-mortems and the incident log for the same assumption, component or failure shape.
     If it has happened before, the more useful question is why the earlier actions did not prevent it. -->

- Related incidents:
- Why earlier actions did not prevent this one:

## If an AI system was involved

<!-- Skip this section if no model, prompt, retrieval index or agent was in the path. Behaviour can change
     without a deploy of yours (a model alias moves, an index is rebuilt, a prompt is edited), so record
     the versions that were live at the time, not the ones in the repository today. -->

- Model and version, and the prompt version in use:
- Retrieval: index or corpus version, and when it was last rebuilt:
- Did an eval or golden set cover this case? If it passed, why did it pass:
- Guardrails or filters that fired, or should have:
- Actions the system took on its own (tool calls, writes, messages):

## What went well, and where we were lucky

<!-- Luck is a finding. If the outage stayed small because it happened at a quiet hour or one
     person happened to be awake, write that down, because next time it will not be. -->

- Went well:
- Lucky:

## Actions

<!-- Each action has an owner and a ticket, or it will not happen. Prefer actions that would catch
     the next version of this problem, not only this exact one. "Be more careful" is not an action.
     Update the status at a follow-up a month later; an action still open then needs a new date or a decision to drop it. -->

| Action | Type | Owner | Ticket | Due | Status |
|---|---|---|---|---|---|
| | Prevent / Detect / Mitigate / Process | | | | Open / In progress / Done |

## Questions still open

<!-- What the team still does not know, and who is finding out. -->

## For other teams

<!-- One or two sentences another team could act on without reading the rest, if the lesson applies beyond this system. -->
