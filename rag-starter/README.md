# RAG starter

A complete retrieval-augmented generation loop, small enough to read in one sitting: structure-aware chunking, two indexes fused into hybrid search, answers that cite their source, an honest "I could not find this", and a 20-question test set that scores retrieval on its own. Standard library only. No API key, no vector database, no downloads.

## Run it

```bash
cd rag-starter
python3 rag.py "How much can I spend on a hotel in London?"
python3 evaluate.py
```

```text
Hotels are reimbursed up to 180 pounds per night in London and 140 pounds per night elsewhere in the United Kingdom. Breakfast is included in the nightly limit when the hotel charges it separately. [travel-and-expenses#hotels]
```

```text
20 questions, 31 chunks

mode      recall@1  recall@3  recall@5    MRR
bm25          0.80      1.00      1.00   0.89
ngram         0.90      1.00      1.00   0.94
hybrid        0.85      1.00      1.00   0.93
```

Python 3.11 or newer; on Windows, type `python` where it says `python3`. `test.sh` runs `evaluate.py --min-recall 0.9`, the kind of gate that belongs in CI.

## What is in it

| File | What it does |
| --- | --- |
| `corpus/` | Eight short policy documents with headings, the kind of text an internal assistant answers from |
| `rag.py` | Chunking, BM25, character n-gram vectors, reciprocal rank fusion, extractive answers with citations, optional `--llm` |
| `golden.jsonl` | Twenty real-sounding questions, each labelled with the section that answers it |
| `evaluate.py` | Recall at 1, 3 and 5 and MRR for each retrieval mode, plus the questions it ranks wrong |

## Things to try

1. **The Spain question.** `python3 rag.py "Can I work from Spain for a month?"` retrieves the home-office section first and quotes it confidently, because it shares the words "work" and "month". The right section talks about "another country". This is the failure that makes users stop trusting an assistant. Fix it with query rewriting, a real embedding model, or a reranker, then rerun `evaluate.py` to prove it.
2. **Hybrid is not free.** In the table, the character n-gram index alone puts the right section first more often than the fusion does. Fusion protects you from one index's blind spots; it does not always win. Measure before you assume.
3. **Break the chunking.** `python3 evaluate.py --chunking windows` scores the same questions against fixed 40-word chunks that ignore headings. Hybrid recall at 1 falls from 0.85 to 0.40 and recall at 5 from 1.00 to 0.60: answers land across window boundaries, and windows lose the heading that said what they were about.
4. **Ask something the documents do not cover.** `python3 rag.py "Can I bring my dog to the office?"` declines and lists the closest sections. Set the threshold in `extractive_answer` to 0 and it quotes a section that has nothing to do with dogs, with a citation that makes it look sourced.
5. **Add a model.** `python3 -m pip install openai`, set `OPENAI_API_KEY` (or `OPENAI_BASE_URL` for a local server) and `RAG_MODEL`, then add `--llm`. The model sees only the retrieved chunks and must cite their ids.

## Taking it to production

Swap `CharNgrams` for an embedding model and a vector index, keep BM25 beside it, add a reranker over the top 20 to 50, and keep `evaluate.py` running on every change with a larger labelled set. The posts behind each step are on [stackunseen.com](https://stackunseen.com/code/rag-starter).
