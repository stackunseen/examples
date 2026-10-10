// A supervisor with two specialists, using the OpenAI Agents SDK for TypeScript.
//
// The supervisor keeps control and calls each specialist as a tool: research first, then analysis, then it decides
// what the user sees. A handoff would pass control to the specialist and never come back.
import { Agent, run, tool } from "@openai/agents";
import { z } from "zod";

const searchDocs = tool({
  name: "search_docs",
  description: "Search internal documentation and return passages with their source IDs.",
  parameters: z.object({ query: z.string() }),
  // Replace with a real retrieval call. Keep the source IDs so the analysis can cite them.
  execute: async () =>
    "[doc-12] Evaluate retrieval and generation separately. [doc-31] Keep a golden set of real questions and run it on every change.",
});

const researchAgent = new Agent({
  name: "ResearchAgent",
  instructions:
    "You find evidence. Call search_docs with the question and return the relevant passages with their source IDs. " +
    "Do not answer the question yourself. If nothing relevant comes back, say so plainly.",
  tools: [searchDocs],
});

const analysisAgent = new Agent({
  name: "AnalysisAgent",
  instructions:
    "You turn research findings into a short structured answer: at most three points, each citing a source ID. " +
    "Use only the findings you are given. If they do not support an answer, say what is missing.",
});

const supervisor = new Agent({
  name: "Supervisor",
  instructions:
    "You coordinate and never answer from your own knowledge. " +
    "First call research with the user's question. Then call analysis with the findings. Return the analysis to the user.",
  tools: [
    researchAgent.asTool({ toolName: "research", toolDescription: "Find evidence, with source IDs, for a question." }),
    analysisAgent.asTool({ toolName: "analysis", toolDescription: "Turn research findings into a cited, structured answer." }),
  ],
});

// A run that needs more than a handful of turns is looping; stop it instead of paying for it.
const result = await run(supervisor, "What are the best practices for RAG?", { maxTurns: 8 });
console.log(result.finalOutput);
