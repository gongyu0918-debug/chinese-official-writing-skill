import fs from "node:fs"
import path from "node:path"
import { pathToFileURL } from "node:url"

const [companionRoot, dataRoot, mode = "interactive"] = process.argv.slice(2)
if (!companionRoot || !dataRoot) throw new Error("usage: opencode_adapter_smoke.mjs COMPANION DATA [MODE]")

process.env.COW_OPENCODE_GATE_DATA = dataRoot
process.env.COW_OPENCODE_GATE_DELAY_MS ||= "0"

const pluginPath = path.join(
  companionRoot,
  ".opencode",
  "plugins",
  "chinese-official-writing-gate.js",
)
const skillRoot = path.join(
  companionRoot,
  ".opencode",
  "skills",
  "chinese-official-writing",
)
const pluginURL = pathToFileURL(pluginPath)
const { ChineseOfficialWritingGate } = await import(pluginURL.href)

const originalPrompt = "请起草一份情况报告，只输出正文。"
const draft = "情况报告\n\n测试工作已完成。"
const messages = [
  {
    info: { id: "msg-user-1", role: "user" },
    parts: [{ type: "text", text: originalPrompt }],
  },
  {
    info: { id: "msg-assistant-1", role: "assistant" },
    parts: [
      {
        type: "tool",
        tool: "skill",
        callID: "call-skill-1",
        state: {
          status: "completed",
          input: { name: "chinese-official-writing" },
          metadata: {
            dir: mode === "stale-skill" ? path.join(companionRoot, "stale-skill") : skillRoot,
          },
        },
      },
      { type: "text", text: draft },
    ],
  },
]
const prompts = []
const logs = []
let releaseDispatch = null
const dispatchBarrier = mode === "dispatch-reload"
  ? new Promise((resolve) => {
      releaseDispatch = resolve
    })
  : null
function retainedText() {
  const retained = []
  function collect(directory) {
    if (!fs.existsSync(directory)) return
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const current = path.join(directory, entry.name)
      if (entry.isDirectory()) collect(current)
      else retained.push(fs.readFileSync(current, "utf8"))
    }
  }
  collect(dataRoot)
  return retained.join("\n")
}

function assertRawRedacted() {
  const serialized = retainedText()
  if (serialized.includes(originalPrompt) || serialized.includes(draft)) {
    throw new Error("terminal receipt retained raw request or draft")
  }
}

const client = {
  app: {
    log: async (request) => {
      logs.push(request)
    },
  },
  session: {
    messages: async () => ({ data: messages }),
    prompt: async (request) => {
      const text = request.body.parts[0].text
      prompts.push(text)
      if (dispatchBarrier) await dispatchBarrier
      messages.push({
        info: { id: `msg-user-internal-${prompts.length}`, role: "user" },
        parts: [{ type: "text", text }],
      })
      const marker = "请将下列终稿逐字作为整条最终回复，不要调用工具、不要加说明：\n"
      if (!text.includes(marker)) throw new Error("clean smoke did not reach exact-output emit")
      messages.push({
        info: { id: `msg-assistant-final-${prompts.length}`, role: "assistant" },
        parts: [{ type: "text", text: text.slice(text.indexOf(marker) + marker.length) }],
      })
    },
  },
}

const hook = await ChineseOfficialWritingGate({ client, directory: companionRoot })
await hook.event({ event: { type: "session.idle", properties: { sessionID: "session-1" } } })

if (mode === "stale-skill") {
  if (prompts.length !== 0) throw new Error("a same-name external skill armed the project gate")
  assertRawRedacted()
  if (!logs.some((entry) => entry?.body?.message?.includes("same-name external skill"))) {
    throw new Error("missing same-name skill collision warning")
  }
  process.stdout.write(
    JSON.stringify({ mode, prompts: prompts.length, rawRetained: false, staleSkillRejected: true }) + "\n",
  )
  process.exit(0)
}

if (mode === "dispatch-reload") {
  for (let attempt = 0; attempt < 50 && prompts.length === 0; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 10))
  }
  if (prompts.length !== 1) throw new Error("the original module did not start one prompt dispatch")
  const restartedModule = await import(`${pluginURL.href}?dispatch-reload=1`)
  const restartedHook = await restartedModule.ChineseOfficialWritingGate({
    client,
    directory: companionRoot,
  })
  await restartedHook.event({
    event: { type: "session.idle", properties: { sessionID: "session-1" } },
  })
  if (prompts.length !== 1) throw new Error("a reloaded module duplicated an in-flight dispatch")
  releaseDispatch()
  await new Promise((resolve) => setTimeout(resolve, 100))
  await restartedHook.event({
    event: { type: "session.idle", properties: { sessionID: "session-1" } },
  })
  await new Promise((resolve) => setTimeout(resolve, 100))
  if (prompts.length !== 1) throw new Error("the dispatch reload path created an extra prompt")
  assertRawRedacted()
  if (!logs.some((entry) => entry?.body?.message?.includes("already dispatching"))) {
    throw new Error("missing in-flight dispatch ownership log")
  }
  process.stdout.write(
    JSON.stringify({ mode, prompts: prompts.length, rawRetained: false, singleOwner: true }) + "\n",
  )
  process.exit(0)
}

if (mode === "restart-pending") {
  const restartedModule = await import(`${pluginURL.href}?restart-pending=1`)
  const restartedHook = await restartedModule.ChineseOfficialWritingGate({
    client,
    directory: companionRoot,
  })
  await restartedHook.event({
    event: { type: "session.idle", properties: { sessionID: "session-1" } },
  })
  await new Promise((resolve) => setTimeout(resolve, 400))
  if (prompts.length !== 0) throw new Error("a restarted pending cycle dispatched a duplicate prompt")
  assertRawRedacted()
  if (!logs.some((entry) => entry?.body?.message?.includes("was not replayed"))) {
    throw new Error("missing pending replay cancellation log")
  }
  process.stdout.write(
    JSON.stringify({ mode, prompts: prompts.length, rawRetained: false, pendingReplayAborted: true }) + "\n",
  )
  process.exit(0)
}

if (mode === "turn-changed") {
  messages.push({
    info: { id: "msg-user-2", role: "user" },
    parts: [{ type: "text", text: "请改为起草另一份通知。" }],
  })
  await new Promise((resolve) => setTimeout(resolve, 400))
  if (prompts.length !== 0) throw new Error("an old turn continuation entered a new user task")
  assertRawRedacted()
  if (!logs.some((entry) => entry?.body?.message?.includes("session changed"))) {
    throw new Error("missing changed-turn cancellation log")
  }
  process.stdout.write(
    JSON.stringify({ mode, prompts: prompts.length, rawRetained: false, turnBound: true }) + "\n",
  )
  process.exit(0)
}

await new Promise((resolve) => setTimeout(resolve, 400))

if (mode === "run") {
  if (prompts.length !== 0) throw new Error("headless run must not request a continuation")
  process.stdout.write(JSON.stringify({ mode, prompts: prompts.length, logs: logs.length }) + "\n")
  process.exit(0)
}

if (prompts.length !== 1) throw new Error(`expected one continuation, got ${prompts.length}`)
await hook.event({ event: { type: "session.idle", properties: { sessionID: "session-1" } } })
await new Promise((resolve) => setTimeout(resolve, 200))
if (prompts.length !== 1) throw new Error("terminal echo must not create another continuation")
assertRawRedacted()
if (!logs.some((entry) => entry?.body?.message === "shared gate reached a terminal allow")) {
  throw new Error("missing terminal allow log")
}

const restartedModule = await import(`${pluginURL.href}?restart=1`)
const restartedHook = await restartedModule.ChineseOfficialWritingGate({
  client,
  directory: companionRoot,
})
await restartedHook.event({
  event: { type: "session.idle", properties: { sessionID: "session-1" } },
})
await new Promise((resolve) => setTimeout(resolve, 200))
if (prompts.length !== 1) throw new Error("a restarted adapter replayed a terminal turn")

process.stdout.write(
  JSON.stringify({
    mode,
    prompts: prompts.length,
    logs: logs.length,
    rawRetained: false,
    restartReplayBlocked: true,
  }) + "\n",
)
