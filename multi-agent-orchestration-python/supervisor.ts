// A supervisor with two specialists over the model's REST API, with no SDK and no agent framework.
//
// The supervisor is a loop your code owns: the model picks the next tool, the code runs it and decides when to stop.
// Each specialist is a tool backed by its own model call with its own instructions, so control comes back to the
// supervisor after every step. A thin typed client like callModel is where an execution layer you own begins.

type ToolCall = { id: string; type: "function"; function: { name: string; arguments: string } };
type Assistant = { role: "assistant"; content: string | null; tool_calls?: ToolCall[] };
type Message = { role: "system" | "user"; content: string } | Assistant | { role: "tool"; tool_call_id: string; content: string };

// On Azure OpenAI, point CHAT_COMPLETIONS_URL at your deployment's chat/completions URL (with its api-version)
// and set AZURE_OPENAI_API_KEY; MODEL is then ignored, because the deployment decides the model.
const CHAT_URL = process.env.CHAT_COMPLETIONS_URL ?? "https://api.openai.com/v1/chat/completions";
const MODEL = process.env.MODEL ?? "gpt-4o-mini";
// A run that needs more than a handful of turns is looping; stop it instead of paying for it.
const MAX_TURNS = 8;

/** One POST to Chat Completions. */
async function callModel(messages: Message[], tools?: object[]): Promise<Assistant> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (process.env.AZURE_OPENAI_API_KEY) headers["api-key"] = process.env.AZURE_OPENAI_API_KEY;
  else headers.authorization = `Bearer ${process.env.OPENAI_API_KEY}`;
  const response = await fetch(CHAT_URL, { method: "POST", headers, body: JSON.stringify({ model: MODEL, messages, tools }) });
  if (!response.ok) throw new Error(`Model call failed: ${response.status} ${await response.text()}`);
  const body = (await response.json()) as { choices: { message: Assistant }[] };
  return body.choices[0].message;
}

function searchDocs(query: string): string {
  // Replace with a real retrieval call. Keep the source IDs so the analysis can cite them.
  return "[doc-12] Evaluate retrieval and generation separately. [doc-31] Keep a golden set of real questions and run it on every change.";
}

/** One model call with its own instructions: all a specialist is, once the framework is gone. */
async function ask(instructions: string, content: string): Promise<string> {
  const reply = await callModel([{ role: "system", content: instructions }, { role: "user", content }]);
  return reply.content ?? "";
}

const specialists: Record<string, { argument: string; run: (value: string) => Promise<string> }> = {
  research: {
    argument: "question",
    run: (question) =>
      ask(
        "You find evidence. From the passages given, return the ones relevant to the question with their source IDs. " +
          "Do not answer the question yourself. If nothing is relevant, say so plainly.",
        `Question: ${question}\n\nPassages:\n${searchDocs(question)}`,
      ),
  },
  analysis: {
    argument: "findings",
    run: (findings) =>
      ask(
        "You turn research findings into a short structured answer: at most three points, each citing a source ID. " +
          "Use only the findings you are given. If they do not support an answer, say what is missing.",
        findings,
      ),
  },
};

const tool = (name: string, description: string, argument: string) => ({
  type: "function",
  function: { name, description, parameters: { type: "object", properties: { [argument]: { type: "string" } }, required: [argument] } },
});
const tools = [
  tool("research", "Find evidence, with source IDs, for a question.", "question"),
  tool("analysis", "Turn research findings into a cited, structured answer.", "findings"),
];

const SUPERVISOR =
  "You coordinate and never answer from your own knowledge. " +
  "First call research with the user's question. Then call analysis with the findings. Return the analysis to the user.";

async function supervise(question: string): Promise<string> {
  const messages: Message[] = [{ role: "system", content: SUPERVISOR }, { role: "user", content: question }];
  for (let turn = 0; turn < MAX_TURNS; turn++) {
    const reply = await callModel(messages, tools);
    if (!reply.tool_calls?.length) return reply.content ?? "";
    messages.push(reply);
    for (const call of reply.tool_calls) {
      // The code, not the model, decides what runs: unknown tools and malformed arguments are refused.
      const specialist = specialists[call.function.name];
      let value: unknown;
      try {
        value = JSON.parse(call.function.arguments)[specialist?.argument ?? ""];
      } catch {
        value = undefined;
      }
      const output = !specialist
        ? `Unknown tool: ${call.function.name}`
        : typeof value !== "string"
          ? `Invalid arguments for ${call.function.name}`
          : await specialist.run(value);
      messages.push({ role: "tool", tool_call_id: call.id, content: output });
    }
  }
  throw new Error(`Stopped after ${MAX_TURNS} turns without an answer.`);
}

console.log(await supervise("What are the best practices for RAG?"));
