# Security review pack: HR policy assistant

<!-- A worked example. The feature, the team and every number here are invented to show what a
     filled-in pack looks like. It does not describe a real system. -->

| | |
|---|---|
| Feature | HR policy assistant |
| Owning team and contact | People systems team, people-systems@example.com |
| Reviewer | Application security |
| Review date | 2026-11-24 |
| Status | Sent for review |
| Stage | Pilot, 200 employees |
| Model and provider | A hosted chat model through the company's cloud provider, version pinned |
| Changed since the last review | First review |

## What it does

- Who uses it: employees, signed in with their company account.
- What it reads: HR policy documents from the document store, through a search index.
- What it can change: it can file a leave request for the signed-in employee.
- Out of scope for this review: payroll data, which the assistant does not read.

## Data flows

| Step | Data | Sent to | Stored where, and for how long | Who can read it there |
|---|---|---|---|---|
| User asks a question | Prompt | Assistant API | Not stored outside the trace | See "Logs and traces" |
| Retrieval | Query, retrieved passages | Search index | Index holds policy text until the source changes | Employees, filtered by their document permissions |
| Model call | Prompt, passages, tool results | Model provider | Provider keeps nothing after the response, per contract | Nobody at the provider |
| Answer returned | Answer, citations | The employee's browser | Not stored in the browser | The employee |
| Chat history and memory | Earlier turns in the same chat | Chat store | 30 days, nothing kept between chats | The employee |
| Logs and traces | Full prompts and outputs | Trace store | 30 days | People systems on-call, 6 people |
| Cache | Answers that cite only published policies | Answer cache | 45 minutes | The assistant only |

- What the cache key includes: the question text. An answer that cites manager-only guidance is never cached, so a cached answer cannot be served across a permission boundary.

## Data sources

| Source | Sensitivity label | Owner | Steward | How access is enforced for this feature |
|---|---|---|---|---|
| Published HR policies | Internal | Head of HR operations | HR policy editor | Shared to all employees |
| Manager-only guidance | Confidential | Head of HR operations | HR policy editor | Per-user filter from document permissions |
| Individual case files | Restricted | Head of HR business partners | Case management lead | Excluded from indexing |

| Source | How the copy is refreshed | A changed document shows up within | A deleted document is gone within | A removed permission takes effect within |
|---|---|---|---|---|
| Published HR policies | Scheduled indexer, every 15 minutes | 15 minutes in the index, up to an hour in cached answers | 15 minutes | Not applicable, shared to all |
| Manager-only guidance | Scheduled indexer, every 15 minutes | 15 minutes, never cached | 15 minutes | 15 minutes |

- Who is told when a source's label or owner changes, and what the feature does about it: the HR policy editor tells the people systems team. A document relabelled Restricted is removed from the index the same day.

## Retention and deletion

| Store | What it holds | Kept for | What deletes it | Also in backups for |
|---|---|---|---|---|
| Source documents | HR policies and guidance | Until replaced, then archived for 7 years | HR records retention policy | 35 days |
| Search or vector index | Chunks of current policies | As long as the source document is current | Follows the source on the next indexer run | Not backed up, rebuilt from source |
| Chat history | Questions and answers | 30 days | Scheduled purge, nightly | 35 days |
| Logs and traces | Full prompts and outputs | 30 days | Store's retention setting | Not backed up |
| Cache | Answers that cite only published policies | 45 minutes | Expiry | Not backed up |

- How often each source is reviewed for out-of-date documents, and by whom: every policy has a review date, at most 12 months out, and the HR policy editor reviews it.
- What happens to a document that is past its review date: it stays in the index, and answers that cite it show the review date as overdue.
- How a request to delete one person's data is carried out across every store above, and how long it takes: chat history and traces are purged for that employee within 30 days by the people systems team. Backups age out after 35 days. Policies hold no personal data.

## Identity

| Call | Runs as | Scope of that identity |
|---|---|---|
| Retrieval | Signed-in user (on-behalf-of) | Documents that user can open |
| Leave request tool | Signed-in user (on-behalf-of) | That user's own leave record |
| Admin and configuration | Named admins with a second sign-in factor | Prompt, index settings, feature flag |

- Where permission filtering happens: in the search query, before ranking.

## Untrusted input

| Content that reaches the model | Who can write it | What limits a model that follows it |
|---|---|---|
| User message | Any employee | It can only act as that employee |
| Indexed documents | HR operations, 12 editors | The only tool files leave for the signed-in user, and the user confirms it |
| Tool results | The leave system | Returned as structured fields, not free text |

- How model output is encoded before it is rendered: as text, with links limited to the document store's domain.
- What the system prompt contains that should not be printed: nothing. It holds no secrets or internal addresses.

## Tool register

| Tool | What it changes | Reversible | Credential and its scope | Approval | Limits |
|---|---|---|---|---|---|
| search_policies | Nothing (read only) | Yes | User token, read | None | 5 calls per question |
| file_leave_request | Creates a leave request | Yes, the employee can withdraw it | User token, own record only | User confirms the dates on screen | 1 per question |

- How a retried tool call is kept from repeating its action: each leave request carries an idempotency key made from the employee and the dates.
- Private networking to the model, search and tool endpoints: yes for the search index and the leave system. The model endpoint is reached over the provider's public endpoint with an IP allow-list.
- Network egress from the agent runtime: allow-list of the search index, the leave system and the model endpoint.

## Secrets and keys

- Where model and tool keys are stored, and how they reach the runtime: in the company vault, read at start-up through the runtime's managed identity.
- How a key is rotated, and whether that needs a deploy: rotated in the vault. The runtime picks up the new key on restart, with no deploy.
- Who is called when a key leaks: security on-call, then the people systems lead.

## Tests and evidence

- Injection test set: 60 cases, 40 direct and 20 through planted documents, run on every prompt or model change. Last run 2026-11-17.
- Attempts that got through, and what they achieved: 3 of 60. All three made the assistant repeat text from a planted document in its answer. None caused a tool call.
- Permission tests: 25 questions asked as an employee about manager-only guidance. None returned a passage from it.
- Content filter false positives looked at: 2 in the pilot, both questions about medical leave. The filter setting was changed and both now pass.

## Abuse and cost limits

- Rate limits per user and per tenant: 30 questions an hour for each employee. There is one tenant.
- Cost alerts, the threshold for each and who receives them: an alert to the people systems lead at 50% and 80% of the monthly model budget.

## Detection and response

- Can any single answer be reconstructed from its trace: yes, including passages and tool calls, for 30 days.
- Where tool calls are logged, and whether the feature can edit that log: the central audit log. The assistant can write to it and cannot edit or delete.
- Who is paged, and for what: people systems on-call, for error rate and for any tool call that fails authorisation.
- Kill switch: a feature flag that turns off the leave tool alone, or the whole assistant. On-call can use it, and it takes effect within 5 minutes.
- Runbooks that exist: provider outage. Prompt injection and data leakage are drafted and not yet tested.

## Model and vendor

- Model version pinned, and how a change is evaluated: pinned. A change runs the answer-quality eval set and the injection set before rollout.
- What the provider stores, for how long, and whether it is used for training: nothing kept after the response, and no training use, per the contract.
- Region and sub-processors checked against requirements: same region as the document store. Sub-processor list reviewed by procurement.

## Risks we know about and accept

| Risk | Why it is accepted for now | Owner | Revisit by |
|---|---|---|---|
| A planted document can make the assistant repeat its text in an answer | Only 12 HR editors can publish to the index, and the text cannot trigger an action | People systems lead | 2026-12-15 |
| A manager who loses access can still get manager-only passages for up to 15 minutes | The window is short, and each retrieval is logged with the user | Search owner | 2026-12-15 |
| Chat history deleted on request stays in backups for up to 35 days | Backups cannot be edited, and restores are rare and logged | People systems lead | 2027-01-15 |
| The trace store holds confidential passages for 30 days | Needed to investigate wrong answers during the pilot. Access is limited to 6 people | People systems lead | 2027-01-15 |
| A changed policy can be answered from the old version for up to an hour | The answer shows the document date. Shorter cache lifetime is planned | Search owner | 2026-12-15 |
| Two of three runbooks are untested | Pilot is 200 users with on-call cover in working hours | On-call lead | 2026-12-01 |
| The model endpoint is public, behind an IP allow-list | Private networking for it is booked with the platform team | Platform lead | 2027-01-15 |

## Questions for the reviewer

- Is user confirmation enough for the leave tool, or should a manager approve as well?
- Is 30 days of full prompts in the trace store acceptable at general release?

## Review outcome

| Finding | Severity | Owner | Due | Status |
|---|---|---|---|---|
| | | | | |
