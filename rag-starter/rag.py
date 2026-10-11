"""A small, complete RAG pipeline you can read in one sitting and run on a laptop.

What it does, in order:
  1. Chunks markdown documents by heading, keeping the document title and heading in every chunk.
  2. Indexes the chunks twice: BM25 over words, and character n-gram vectors (a cheap, offline stand-in for
     embeddings that catches word forms and typos).
  3. Retrieves with each index and fuses the two rankings with reciprocal rank fusion (hybrid search).
  4. Answers with the best supported sentences and a citation for each, or says it does not know when the
     evidence is weak. With --llm it asks a model instead, given only the retrieved chunks.

Standard library only, except the optional --llm mode, which needs the `openai` package and an
OpenAI-compatible endpoint (OPENAI_API_KEY, optional OPENAI_BASE_URL for a local server, RAG_MODEL for the model).

    python rag.py "How much can I spend on a hotel in London?"
    python rag.py --mode bm25 "Can I work from Spain for a month?"
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

CORPUS = Path(__file__).parent / "corpus"

STOPWORDS = set(
    "a an and are as at be but by can do does for from has have how i if in into is it its me my no not of on or "
    "our so than that the their then there these they this to up us was we were what when where which who why will "
    "with you your".split()
)


@dataclass
class Chunk:
    id: str  # "<document>#<heading>", the citation a reader can follow
    title: str
    heading: str
    text: str

    @property
    def indexed(self) -> str:
        # The heading path goes into the indexed text: "Hotels" alone says little; "Travel and expenses > Hotels" says where.
        return f"{self.title} > {self.heading}\n{self.text}" if self.heading else self.text


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_chunks(folder: Path = CORPUS) -> list[Chunk]:
    """One chunk per "## " section. Splitting on the document's own structure keeps a rule and its exceptions together."""
    chunks: list[Chunk] = []
    for path in sorted(folder.glob("*.md")):
        title, heading, lines = path.stem, "", []

        def flush() -> None:
            body = " ".join(line.strip() for line in lines if line.strip())
            if heading and body:
                chunks.append(Chunk(f"{path.stem}#{slug(heading)}", title, heading, body))

        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("## "):
                flush()
                heading, lines = line[3:].strip(), []
            else:
                lines.append(line)
        flush()
    return chunks


def load_windows(folder: Path = CORPUS, size: int = 40) -> list[Chunk]:
    """The common alternative, for comparison: fixed windows of `size` words that ignore headings.

    Each window is labelled with the section it starts in, so the evaluation can still score it. Text that runs
    across a boundary lands in a window labelled with the previous section, which is exactly the problem.
    """
    chunks: list[Chunk] = []
    for path in sorted(folder.glob("*.md")):
        words: list[str] = []
        owners: list[str] = []
        heading = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                continue
            if line.startswith("## "):
                heading = line[3:].strip()
                continue
            for word in line.split():
                words.append(word)
                owners.append(heading)
        for start in range(0, len(words), size):
            # No title or heading goes into a window's indexed text: that context is what fixed windows lose.
            chunks.append(Chunk(f"{path.stem}#{slug(owners[start])}", "", "", " ".join(words[start : start + size])))
    return chunks


def stem(word: str) -> str:
    """Rough suffix stripping, enough for "holidays" to meet "holiday" and "claims" to meet "claim"."""
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def terms(text: str) -> list[str]:
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


class BM25:
    """Okapi BM25: rewards chunks that contain the query's rare words, without letting long chunks win by length."""

    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.tf = [Counter(terms(d)) for d in docs]
        self.lengths = [sum(tf.values()) for tf in self.tf]
        self.avg = sum(self.lengths) / len(self.lengths)
        df = Counter(t for tf in self.tf for t in tf)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: str) -> list[float]:
        q = terms(query)
        out = []
        for tf, length in zip(self.tf, self.lengths):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / self.avg))
            out.append(s)
        return out


class CharNgrams:
    """TF-IDF over character trigrams inside words, compared by cosine similarity.

    It catches word forms and spelling slips that exact words miss ("reimburse" and "reimbursed", "postmortem" and
    "post-mortem"), but it does not understand meaning. Swap in an embedding model here when you have one: the
    rest of the pipeline only needs one score per chunk.
    """

    def __init__(self, docs: list[str], n: int = 3) -> None:
        self.n = n
        counts = [self._grams(d) for d in docs]
        df = Counter(g for c in counts for g in c)
        self.idf = {g: math.log(len(docs) / f) + 1 for g, f in df.items()}
        self.vectors = [self._weigh(c) for c in counts]

    def _grams(self, text: str) -> Counter:
        grams: Counter = Counter()
        for word in terms(text):
            padded = f" {word} "
            grams.update(padded[i : i + self.n] for i in range(len(padded) - self.n + 1))
        return grams

    def _weigh(self, counts: Counter) -> dict[str, float]:
        vec = {g: c * self.idf.get(g, 0.0) for g, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {g: v / norm for g, v in vec.items()}

    def scores(self, query: str) -> list[float]:
        q = self._weigh(self._grams(query))
        return [sum(w * vec.get(g, 0.0) for g, w in q.items()) for vec in self.vectors]


def rank(scores: list[float]) -> list[int]:
    return sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)


def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[int]:
    """Merge rankings by position, not by score: BM25 scores and cosines live on different scales."""
    fused: Counter = Counter()
    for ranking in rankings:
        for position, i in enumerate(ranking):
            fused[i] += 1 / (k + position + 1)
    return [i for i, _ in fused.most_common()]


class Retriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        docs = [c.indexed for c in chunks]
        self.bm25 = BM25(docs)
        self.ngrams = CharNgrams(docs)

    def search(self, query: str, k: int = 5, mode: str = "hybrid") -> list[Chunk]:
        by_words = rank(self.bm25.scores(query))
        by_grams = rank(self.ngrams.scores(query))
        order = {"bm25": by_words, "ngram": by_grams, "hybrid": reciprocal_rank_fusion([by_words, by_grams])}[mode]
        return [self.chunks[i] for i in order[:k]]


def coverage(query: str, text: str) -> float:
    """Share of the question's meaningful words that appear in a chunk: a crude, explainable evidence check."""
    q = set(terms(query))
    return len(q & set(terms(text))) / len(q) if q else 0.0


def extractive_answer(query: str, hits: list[Chunk], threshold: float = 0.4) -> str:
    """Quote the best supported sentences with their citation, or decline when the evidence is too thin."""
    best = max(hits, key=lambda c: coverage(query, c.indexed), default=None)
    if best is None or coverage(query, best.indexed) < threshold:
        closest = ", ".join(c.id for c in hits[:3])
        return f"I could not find this in the documents. Closest sections: {closest}."
    sentences = re.split(r"(?<=[.!?])\s+", best.text)
    picked = sorted(sentences, key=lambda s: coverage(query, s), reverse=True)[:2]
    ordered = [s for s in sentences if s in picked]  # keep the document's own order
    return f"{' '.join(ordered)} [{best.id}]"


def llm_answer(query: str, hits: list[Chunk]) -> str:
    """Ask a model to answer from the retrieved chunks only, citing their ids."""
    from openai import OpenAI  # optional dependency, only for --llm

    model = os.environ.get("RAG_MODEL")
    if not model:
        sys.exit("Set RAG_MODEL to the model name your endpoint serves.")
    sources = "\n\n".join(f"[{c.id}]\n{c.indexed}" for c in hits)
    client = OpenAI(base_url=os.environ.get("OPENAI_BASE_URL"))
    reply = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Answer only from the sources. Cite the id in brackets after each claim. "
                "If the sources do not contain the answer, say you could not find it.",
            },
            {"role": "user", "content": f"Sources:\n{sources}\n\nQuestion: {query}"},
        ],
    )
    return reply.choices[0].message.content or ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a question of the policy documents in ./corpus.")
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=3, help="chunks to retrieve (default 3)")
    parser.add_argument("--mode", choices=["hybrid", "bm25", "ngram"], default="hybrid")
    parser.add_argument("--chunking", choices=["headings", "windows"], default="headings")
    parser.add_argument("--llm", action="store_true", help="answer with a model instead of quoting")
    args = parser.parse_args()

    chunks = load_chunks() if args.chunking == "headings" else load_windows()
    hits = Retriever(chunks).search(args.question, k=args.k, mode=args.mode)
    print(llm_answer(args.question, hits) if args.llm else extractive_answer(args.question, hits))
    print("\nRetrieved:")
    for position, chunk in enumerate(hits, 1):
        print(f"  {position}. {chunk.id}")


if __name__ == "__main__":
    main()
