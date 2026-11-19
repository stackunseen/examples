# Post-mortem: policy answers quoted last quarter's parental leave rules for eleven days

<!-- A worked example. It fills in the template from the published failure story
     "The retrieval cache that served stale policies". Where that write-up does not record
     something, this example says so instead of guessing. -->

| | |
|---|---|
| Status | Final |
| Incident date | Not recorded in the original write-up |
| Severity | Not recorded in the original write-up |
| Authors | The team that owned the retrieval system |
| Incident lead | Not recorded |
| Review meeting | Not recorded |
| Tickets | Cache key change, freshness metric |

## Summary

For eleven days, repeated questions about parental leave got answers based on the rules in force before the change. A query cache in front of retrieval kept serving answers built from the old corpus after the policy documents were re-indexed. Each stale answer carried a confident citation to a document that no longer said that. Adding the corpus version to the cache key fixed it.

## Impact

- Who was affected: anyone who asked a question someone else had already asked during those eleven days.
- What went wrong for them: they got the old parental leave rules, cited to a document that had since changed.
- Duration of user impact: eleven days.
- Data lost, corrupted or exposed: none. The answers were stale, not leaked.
- Commitments affected: not recorded.

## Key times

| Measure | Time | Gap |
|---|---|---|
| Problem started | When the policy corpus was re-indexed | |
| Detected | Eleven days later | Time to detect: eleven days |
| Incident declared | Not recorded | Time to decide: not recorded |
| Impact mitigated | When the versioned cache key shipped | Time to mitigate: not recorded |
| Fully resolved | With the fix and the freshness metric in place | |

How it was detected: not recorded in the original write-up. No metric or alert caught it, because none measured answer freshness.

## Timeline

| Time | What happened | What we believed then |
|---|---|---|
| Before the incident | A query-level cache was added in front of retrieval to cut cost and latency, keyed on a hash of the normalised question. | The cache was a pure performance win. Hit rate was excellent. |
| Day 0 | The policy corpus was re-indexed after a change to the parental leave rules. | The re-index updated what users would be told. |
| Days 0 to 11 | Repeated questions were served from the cache, built from the old corpus. | Dashboards showed nothing wrong. Recall on the golden set stayed perfect and latency had never looked better. |
| Day 11 | The stale answers were found. | |
| After | The corpus version went into the cache key, and a freshness metric was added. | |

## What happened

Every answer the cache stored had been built from one version of the policy corpus, but the cache key held only the question. When the corpus was re-indexed, nothing told the cache. A question that had been asked before the change matched its old key and returned the old answer, with its old citation.

## How we responded

- What was tried, and what happened: not recorded in the original write-up.
- What finally stopped the impact: making the corpus version part of the cache key, so every cached answer built from the old corpus stopped matching.
- Who made the call, and what they needed to make it: not recorded.

## Communication

| When | Audience | Channel | What was said |
|---|---|---|---|
| Not recorded | | | |

## Why it was possible

- The assumption that turned out to be wrong: that an answer to the same question stays correct, when it is only correct for the corpus version it was built from.
- Why nothing stopped the change: the re-index and the cache were separate concerns, and nothing linked an index build to cache invalidation.
- Why detection took as long as it did: there was no metric for answer freshness, and the golden set was built from the old corpus, so recall stayed perfect.
- Why mitigation took as long as it did: not recorded.
- Anything that made the impact larger: a high hit rate meant most repeated questions were served from the cache.

## Has this happened before?

- Related incidents: not recorded.
- Why earlier actions did not prevent this one: not applicable.

## If an AI system was involved

- Model and version, and the prompt version in use: not recorded. The stale answers came from the cache, not from the model.
- Retrieval: index or corpus version, and when it was last rebuilt: the policy corpus was re-indexed after the parental leave change. Before the fix, the cache did not know which version an answer came from.
- Did an eval or golden set cover this case? If it passed, why did it pass: the golden set passed with perfect recall, because it was built from the old corpus and measured retrieval, not the answers users got from the cache.
- Guardrails or filters that fired, or should have: none recorded. No check compared an answer's sources with the current corpus.
- Actions the system took on its own (tool calls, writes, messages): none recorded.

## What went well, and where we were lucky

- Went well: the fix was small, about ten lines, and a re-index now invalidates every cached answer.
- Lucky: not recorded.

## Actions

| Action | Type | Owner | Ticket | Due | Status |
|---|---|---|---|---|---|
| Write a version on every index build and make it part of the cache key | Prevent | Not recorded | | | Done |
| Track the age of the newest source passage behind each answer, plotted against corpus age | Detect | Not recorded | | | Done |

## Questions still open

Not recorded.

## For other teams

A cache in front of a knowledge base stores answers that were true for one corpus version. Put that version in the key, and measure answer freshness so a stale answer shows up on a dashboard.
