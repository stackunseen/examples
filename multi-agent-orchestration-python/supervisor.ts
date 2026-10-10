import { Agent, run, tool } from "@openai/agents";
import { z } from "zod";

const searchDocs = tool({
  name: "search_docs",
  description: "Search internal documentation.",
  parameters: z.object({ query: z.string() }),
  execute: async () => "Found relevant documentation...",
});

const researchAgent = new Agent({
  name: "ResearchAgent",
  instructions: "Find relevant information using available tools.",
  tools: [searchDocs],
});

const analysisAgent = new Agent({
  name: "AnalysisAgent",
  instructions: "Analyze findings and provide structured insights.",
});

const supervisor = new Agent({
  name: "Supervisor",
  instructions: "Coordinate the workflow between agents.",
  handoffs: [researchAgent, analysisAgent],
});

const result = await run(supervisor, "What are the best practices for RAG?");
console.log(result.finalOutput);
