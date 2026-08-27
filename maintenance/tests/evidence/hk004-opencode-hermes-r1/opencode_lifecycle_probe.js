import crypto from "node:crypto"
import fs from "node:fs"
import path from "node:path"

const states = new Map()

function digest(text) {
  return crypto.createHash("sha256").update(text, "utf8").digest("hex")
}

function logRecord(record) {
  const root = process.env.COW_OPENCODE_PROBE_DIR
  if (!root) return
  fs.mkdirSync(root, { recursive: true })
  fs.appendFileSync(
    path.join(root, "events.jsonl"),
    JSON.stringify({ at: new Date().toISOString(), ...record }) + "\n",
    "utf8",
  )
}

function messageList(result) {
  if (Array.isArray(result)) return result
  if (Array.isArray(result?.data)) return result.data
  return []
}

function latestAssistantText(messages) {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const item = messages[index]
    if (item?.info?.role !== "assistant") continue
    const text = (item.parts ?? [])
      .filter((part) => part?.type === "text" && typeof part.text === "string")
      .map((part) => part.text)
      .join("")
    if (text) return text
  }
  return ""
}

export const ChineseOfficialWritingLifecycleProbe = async ({ client, directory }) => ({
  event: async ({ event }) => {
    if (event?.type !== "session.idle") return
    const sessionID = event.properties?.sessionID
    if (!sessionID) return

    const messagesResult = await client.session.messages({
      path: { id: sessionID },
      query: { directory },
    })
    const messages = messageList(messagesResult)
    const assistant = latestAssistantText(messages)
    const state = states.get(sessionID) ?? "initial"
    logRecord({
      event: "session.idle",
      sessionID,
      state,
      messageCount: messages.length,
      assistantChars: assistant.length,
      assistantSha256: digest(assistant),
      hasD0: assistant.includes("OC_D0"),
      hasD1: assistant.includes("OC_D1"),
    })

    if (state !== "initial" || !assistant.includes("OC_D0")) {
      if (state === "continuing" && assistant.includes("OC_D1")) {
        states.set(sessionID, "complete")
      }
      return
    }

    states.set(sessionID, "continuing")
    const request = {
      path: { id: sessionID },
      query: { directory },
      body: {
        parts: [{ type: "text", text: "仅输出 OC_D1，不要解释。" }],
      },
    }
    const mode = process.env.COW_OPENCODE_PROBE_MODE ?? "async"
    logRecord({ event: "continuation.requested", sessionID, mode })
    if (mode === "scheduled") {
      const delayMs = Number(process.env.COW_OPENCODE_PROBE_DELAY_MS ?? "1200")
      setTimeout(async () => {
        logRecord({ event: "continuation.dispatched", sessionID, mode, delayMs })
        try {
          await client.session.prompt(request)
          logRecord({ event: "continuation.resolved", sessionID, mode })
        } catch (error) {
          logRecord({
            event: "continuation.failed",
            sessionID,
            mode,
            error: error instanceof Error ? error.message : String(error),
          })
        }
      }, delayMs)
      return
    }
    if (mode === "sync") {
      await client.session.prompt(request)
    } else {
      await client.session.promptAsync(request)
    }
  },
})
