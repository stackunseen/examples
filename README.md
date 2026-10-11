# StackUnseen examples

Small, runnable code behind the posts and maps on [stackunseen.com](https://stackunseen.com). Each folder is one example, short enough to read in one screen. External calls are stubbed with a comment saying what to replace.

| Example | What it shows | On the site |
| --- | --- | --- |
| [`langgraph-supervisor`](langgraph-supervisor) | A supervisor pattern as an explicit LangGraph state graph, with typed state and a retrieval node | [Supervisor graph with LangGraph](https://stackunseen.com/code/langgraph-supervisor) |
| [`multi-agent-orchestration-python`](multi-agent-orchestration-python) | A supervisor that calls specialised agents as tools with the OpenAI Agents SDK, keeping control between steps, in Python and TypeScript | [Multi-agent orchestration](https://stackunseen.com/code/multi-agent-orchestration-python) |
| [`rag-starter`](rag-starter) | A complete RAG loop with no API key: heading-based chunks, hybrid search, cited answers, and recall at k on a 20-question test set | [RAG starter](https://stackunseen.com/code/rag-starter) |

## Run them

**rag-starter** runs offline with the Python standard library.

```bash
cd rag-starter
python rag.py "How much can I spend on a hotel in London?"
python evaluate.py
```

**langgraph-supervisor** runs offline; the retrieval step is a stub.

```bash
cd langgraph-supervisor
pip install langgraph
python graph.py
```

**multi-agent-orchestration-python** calls a model, so it needs an `OPENAI_API_KEY` in your environment.

```bash
cd multi-agent-orchestration-python
pip install openai-agents
python supervisor.py
```

```bash
cd multi-agent-orchestration-python
npm install @openai/agents zod
npx tsx supervisor.ts
```

## Licence

MIT, see [LICENSE](LICENSE). Copy, adapt and use the code freely, including at work.

## How this repository is made

The examples live in the `examples/` folder of the StackUnseen site, where the site reads them to render each code page, and are published here from that folder. Issues and discussion are welcome on [stackunseen/discussions](https://github.com/stackunseen/discussions).

### For the site (maintainers)

Each folder is named by the artifact slug in `content/artifacts/<slug>.mdx`; the site build fails if a referenced file is missing, and `pnpm check:examples` fails if a file does not parse. An optional `test.sh` in a folder runs in CI from that folder. `pnpm publish:examples` mirrors this folder to github.com/stackunseen/examples as a fresh commit, so the public history carries no site-repo commits.
