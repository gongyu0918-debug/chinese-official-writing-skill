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

const REVIEW_PROMPT = `这是交付前复核，不是新任务。请回看本轮用户材料、已加载的 chinese-official-writing 技能和当前草稿，只输出修订后的完整正文。

仅修复以下问题：
1. 删除正文外的过程说明、自评、字数、Markdown 加粗、井号标题、代码围栏和横线包装；普通正文标题保留。
2. 保持用户给出的主体、数字、完整日期和“已完成但材料未附、尚未开展、可安排、比选中、未形成决定”等状态强度。
3. 删除材料未给的具体后续动作、流程、责任、期限、报送承诺和已经取得的成效。
4. 保留由已给事实和常识直接支持的一层一般原因、目的或低强度预期作用；不要因过度保守删掉必要论证，也不要把预期写成既成成效。

不要解释修改过程，只输出最终正文。`

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

    const mode = process.env.COW_OPENCODE_PROBE_MODE ?? "async"
    const markerReady = assistant.includes("OC_D0")
    const reviewReady = mode === "review" && assistant.length > 0
    if (state !== "initial" || (!markerReady && !reviewReady)) {
      if (
        state === "continuing" &&
        (assistant.includes("OC_D1") || (mode === "review" && assistant.length > 0))
      ) {
        states.set(sessionID, "complete")
        logRecord({
          event: mode === "review" ? "review.complete" : "marker.complete",
          sessionID,
          assistantChars: assistant.length,
          assistantSha256: digest(assistant),
        })
      }
      return
    }

    states.set(sessionID, "continuing")
    const request = {
      path: { id: sessionID },
      query: { directory },
      body: {
        parts: [{ type: "text", text: mode === "review" ? REVIEW_PROMPT : "仅输出 OC_D1，不要解释。" }],
      },
    }
    logRecord({ event: "continuation.requested", sessionID, mode })
    if (mode === "scheduled" || mode === "review") {
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
