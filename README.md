# StackUnseen examples

Small, runnable code behind the posts and maps on [stackunseen.com](https://stackunseen.com). Each folder is one example, short enough to read in one screen. External calls are stubbed with a comment saying what to replace.

| Example | What it shows | On the site |
| --- | --- | --- |
| [`langgraph-supervisor`](langgraph-supervisor) | A supervisor pattern as an explicit LangGraph state graph, with typed state and a retrieval node | [Supervisor graph with LangGraph](https://stackunseen.com/code/langgraph-supervisor) |
| [`multi-agent-orchestration-python`](multi-agent-orchestration-python) | A supervisor that calls two specialists as tools in a loop your code owns, with no agent framework: Python on the OpenAI SDK, TypeScript over the REST API | [Multi-agent orchestration](https://stackunseen.com/code/multi-agent-orchestration-python) |
| [`rag-starter`](rag-starter) | A complete RAG loop with no API key: heading-based chunks, hybrid search, cited answers, and recall at k on a 20-question test set | [RAG starter](https://stackunseen.com/code/rag-starter) |
| [`practice-supervisor-control`](practice-supervisor-control) | Practice: write a supervisor's hand-offs, turn budget and approval gate yourself, checked by six tests, with no API key | [Keep a supervisor in control](https://stackunseen.com/code/practice-supervisor-control) |
## Run them

The commands use `python3`, as on macOS and Linux; on Windows, type `python` instead.

**rag-starter** runs offline with the Python standard library.

```bash
cd rag-starter
python3 rag.py "How much can I spend on a hotel in London?"
python3 evaluate.py
```

**langgraph-supervisor** runs offline; the retrieval step is a stub.

```bash
cd langgraph-supervisor
python3 -m pip install langgraph
python3 graph.py
```

**multi-agent-orchestration-python** calls a model, so it needs an `OPENAI_API_KEY` in your environment (or, for Azure OpenAI, see the comments at the top of each file).

```bash
cd multi-agent-orchestration-python
python3 -m pip install openai
python3 supervisor.py
```

The TypeScript version has no dependencies; it calls the REST API with `fetch`.

```bash
cd multi-agent-orchestration-python
npx tsx supervisor.ts
```

**practice-supervisor-control** is an exercise: fill in the TODOs in `supervisor.py`, then check your work. It needs only Python.

```bash
cd practice-supervisor-control
python3 -m unittest -v
```

## Licence

MIT, see [LICENSE](LICENSE). Copy, adapt and use the code freely, including at work.

## How this repository is made

The examples live in the `examples/` folder of the StackUnseen site, where the site reads them to render each code page, and are published here from that folder. Issues and discussion are welcome on [stackunseen/discussions](https://github.com/stackunseen/discussions).

### For the site (maintainers)

Each folder is named by the artifact slug in `content/artifacts/<slug>.mdx`; the site build fails if a referenced file is missing, and `pnpm check:examples` fails if a file does not parse. An optional `test.sh` in a folder runs in CI from that folder. `pnpm publish:examples` mirrors this folder to github.com/stackunseen/examples as a fresh commit, so the public history carries no site-repo commits.
