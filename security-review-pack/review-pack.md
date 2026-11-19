# Security review pack: <feature name>

<!-- Fill this in before the review and send it to the reviewer a few days ahead.
     Write what is true today and mark anything planned as planned. Where something is missing,
     write "not yet". A blank tells the reviewer nothing, and "not yet" tells them you looked. -->

| | |
|---|---|
| Feature | |
| Owning team and contact | |
| Reviewer | |
| Review date | YYYY-MM-DD |
| Status | Draft / Sent for review / Reviewed |
| Stage | Prototype / Pilot / General release |
| Model and provider | |
| Changed since the last review | First review / New tool / New data source / New model |

## What it does

<!-- Three or four sentences a reviewer who has never seen the feature can follow:
     who uses it, what they ask it, what it reads and what it can change. -->

- Who uses it:
- What it reads:
- What it can change:
- Out of scope for this review:

## Data flows

<!-- Trace one request from the user to the answer and list every place data lands on the way.
     Teams most often leave the provider, the logs and the cache off the diagram, so those rows are already here.
     Attach or link the diagram as well. -->

| Step | Data | Sent to | Stored where, and for how long | Who can read it there |
|---|---|---|---|---|
| User asks a question | Prompt | | | |
| Retrieval | Query, retrieved passages | | | |
| Model call | Prompt, passages, tool results | Model provider | | |
| Answer returned | Answer, citations | | | |
| Chat history and memory | Earlier turns, anything kept between sessions | | | |
| Logs and traces | Full prompts and outputs | | | |
| Cache | Answers or retrieved passages | | | |

- What the cache key includes (user, permissions, document version), and whether one user can be served an answer built for another:

## Data sources

<!-- Every source the feature reads. If restricted data is excluded from indexing, say how.
     The owner is accountable for the data. The steward is the person who answers questions about it
     day to day and approves a change to its label or access. They are often different people. -->

| Source | Sensitivity label | Owner | Steward | How access is enforced for this feature |
|---|---|---|---|---|
| | Public / Internal / Confidential / Restricted | | | Per-user filter / Excluded / Shared to all users |

<!-- The feature reads a copy of each source, and the copy runs behind. For a reviewer the delay that
     matters most is how long a deleted document or a removed permission stays in the copy. -->

| Source | How the copy is refreshed | A changed document shows up within | A deleted document is gone within | A removed permission takes effect within |
|---|---|---|---|---|
| | Scheduled indexer / Pushed on change / Manual | | | |

- Who is told when a source's label or owner changes, and what the feature does about it:

## Retention and deletion

<!-- How long each store keeps data and what removes it. "Kept until someone deletes it" is an answer,
     and a reviewer will ask who that someone is. Include backups, because data deleted from the
     live store is often still in them. -->

| Store | What it holds | Kept for | What deletes it | Also in backups for |
|---|---|---|---|---|
| Source documents | | | Owner archives / Retention policy / Nothing | |
| Search or vector index | | | Follows the source / Scheduled purge / Nothing | |
| Chat history | | | | |
| Logs and traces | | | | |
| Cache | | | Expiry | |

- How often each source is reviewed for out-of-date documents, and by whom:
- What happens to a document that is past its review date (flagged, archived, removed from the index):
- How a request to delete one person's data is carried out across every store above, and how long it takes:

## Identity

<!-- For each call the feature makes, the identity it runs as. A shared service account is an
     answer too, but write down everything that account can reach. -->

| Call | Runs as | Scope of that identity |
|---|---|---|
| Retrieval | Signed-in user (on-behalf-of) / Service account | |
| Each tool | | |
| Admin and configuration | | |

- Where permission filtering happens (before ranking, or after the answer is written):

## Untrusted input

<!-- Everything that can put text in front of the model, not only the chat box.
     For each, who is able to write there. -->

| Content that reaches the model | Who can write it | What limits a model that follows it |
|---|---|---|
| User message | | |
| Indexed documents | | |
| Tool results (web pages, email, records) | | |

- How model output is encoded before it is rendered:
- What the system prompt contains that should not be printed:

## Tool register

<!-- One row per tool. "Reversible" means someone can undo it afterwards without help from another team. -->

| Tool | What it changes | Reversible | Credential and its scope | Approval | Limits |
|---|---|---|---|---|---|
| | Nothing (read only) / Record / Message / Payment | Yes / No | | None / User confirms / Second person | Steps, spend, rate |

- How a retried tool call is kept from repeating its action (idempotency key or other):
- Private networking to the model, search and tool endpoints:
- Network egress from the agent runtime (allow-list or open):

## Secrets and keys

- Where model and tool keys are stored, and how they reach the runtime:
- How a key is rotated, and whether that needs a deploy:
- Who is called when a key leaks:

## Tests and evidence

<!-- Give the results with the failures. If every case passed, add harder cases before the review. -->

- Injection test set: number of cases, direct and through documents, and when it last ran:
- Attempts that got through, and what they achieved:
- Permission tests (a user asking for something they cannot see):
- Content filter false positives looked at:

## Abuse and cost limits

- Rate limits per user and per tenant:
- Cost alerts, the threshold for each and who receives them:

## Detection and response

- Can any single answer be reconstructed from its trace, including retrieved passages and tool calls:
- Where tool calls are logged, and whether the feature can edit that log:
- Who is paged, and for what:
- Kill switch: what it disables, who can use it, and how long it takes:
- Runbooks that exist (prompt injection, data leakage, provider outage):

## Model and vendor

- Model version pinned, and how a change is evaluated:
- What the provider stores, for how long, and whether it is used for training:
- Region and sub-processors checked against requirements:

## Risks we know about and accept

<!-- List what you already know is not solved, why you are going ahead anyway, and who owns it.
     A reviewer will not believe an empty table here, so fill it in before they do. -->

| Risk | Why it is accepted for now | Owner | Revisit by |
|---|---|---|---|
| | | | YYYY-MM-DD |

## Questions for the reviewer

<!-- The decisions you want the reviewer's judgment on. The meeting can start with these. -->

## Review outcome

<!-- Filled in during and after the review. Update the status when each finding is closed. -->

| Finding | Severity | Owner | Due | Status |
|---|---|---|---|---|
| | High / Medium / Low | | | Open / Fixed / Accepted |
