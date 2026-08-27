import crypto from "node:crypto"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import { spawnSync } from "node:child_process"
import { fileURLToPath } from "node:url"

const PLUGIN_FILE = fileURLToPath(import.meta.url)
const OPENCODE_ROOT = path.resolve(path.dirname(PLUGIN_FILE), "..")
const SKILL_ROOT = path.join(OPENCODE_ROOT, "skills", "chinese-official-writing")
const CORE_PATH = path.join(SKILL_ROOT, "hooks", "gate_stop_hook.py")
const CAPABILITY_PATH = path.join(OPENCODE_ROOT, "hook-capability.json")
const INTERNAL_PREFIX = "[chinese-official-writing Hook internal continuation]\n"
const DEFAULT_CAPABILITY = "delivery_review"
const MAX_HOST_CONTINUATIONS = 8
const DEFAULT_DELAY_MS = 1200
const SAFE_KEY_MAX_LENGTH = 120
const SUPPORTED_CAPABILITIES = new Set([
  DEFAULT_CAPABILITY,
  "protective_expansion",
  "under_length",
  "over_length",
  "delivery_cleanliness",
  "repetition_cleanup",
])

const sessionStates = new Map()

function digest(value) {
  return crypto.createHash("sha256").update(value, "utf8").digest("hex")
}

function safeKey(value) {
  const cleaned = value.replace(/[^A-Za-z0-9_.-]+/g, "_").replace(/^[._]+|[._]+$/g, "")
  return cleaned.slice(0, SAFE_KEY_MAX_LENGTH) || "session"
}

function messageList(result) {
  if (Array.isArray(result)) return result
  if (Array.isArray(result?.data)) return result.data
  return []
}

function messageText(message) {
  return (message?.parts ?? [])
    .filter((part) => part?.type === "text" && typeof part.text === "string")
    .map((part) => part.text)
    .join("")
}

function messageID(message) {
  return message?.info?.id ?? message?.id ?? message?.messageID ?? ""
}

function latestExternalUser(messages) {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index]
    if (message?.info?.role !== "user") continue
    const text = messageText(message)
    if (!text || text.startsWith(INTERNAL_PREFIX)) continue
    return { index, id: messageID(message) || digest(text), text }
  }
  return null
}

function latestAssistant(messages, afterIndex) {
  for (let index = messages.length - 1; index > afterIndex; index -= 1) {
    const message = messages[index]
    if (message?.info?.role !== "assistant") continue
    const text = messageText(message)
    if (text) return { index, id: messageID(message) || digest(text), text }
  }
  return null
}

function latestInternalContinuationIndex(messages, afterIndex) {
  for (let index = messages.length - 1; index > afterIndex; index -= 1) {
    const message = messages[index]
    if (
      message?.info?.role === "user" &&
      messageText(message).startsWith(INTERNAL_PREFIX)
    ) {
      return index
    }
  }
  return -1
}

function internalContinuationCount(messages, afterIndex) {
  return messages.slice(afterIndex + 1).filter(
    (message) =>
      message?.info?.role === "user" && messageText(message).startsWith(INTERNAL_PREFIX),
  ).length
}

function samePath(left, right) {
  try {
    const normalize = (value) => {
      const resolved = path.resolve(value)
      return process.platform === "win32" ? resolved.toLowerCase() : resolved
    }
    return normalize(left) === normalize(right)
  } catch {
    return false
  }
}

function capability() {
  try {
    const value = JSON.parse(fs.readFileSync(CAPABILITY_PATH, "utf8"))?.capability
    return SUPPORTED_CAPABILITIES.has(value) ? value : DEFAULT_CAPABILITY
  } catch {
    return DEFAULT_CAPABILITY
  }
}

function gateDataRoot() {
  const configured = process.env.COW_OPENCODE_GATE_DATA
  if (configured) return path.resolve(configured)

  const database = process.env.OPENCODE_DB
  if (database && database !== ":memory:" && path.isAbsolute(database)) {
    return path.join(path.dirname(database), "chinese-official-writing-gate")
  }

  const base =
    process.env.XDG_DATA_HOME ||
    (process.platform === "win32"
      ? process.env.LOCALAPPDATA
      : path.join(os.homedir(), ".local", "share"))
  return path.join(base || os.tmpdir(), "opencode", "chinese-official-writing-gate")
}

function hasTerminalReceipt(sessionID, turnID) {
  const receipt = path.join(
    gateDataRoot(),
    "candidate-ai-gate-hook",
    safeKey(sessionID),
    `${safeKey(turnID)}.json`,
  )
  try {
    return JSON.parse(fs.readFileSync(receipt, "utf8"))?.data_retention_state ===
      "raw_turn_data_redacted"
  } catch {
    return false
  }
}

function adapterStatePath(sessionID, turnID) {
  return path.join(
    gateDataRoot(),
    "opencode-adapter-state",
    safeKey(sessionID),
    `${safeKey(turnID)}.json`,
  )
}

function readAdapterState(sessionID, turnID) {
  const target = adapterStatePath(sessionID, turnID)
  try {
    const value = JSON.parse(fs.readFileSync(target, "utf8"))
    return value && typeof value === "object"
      ? value
      : { phase: "corrupt", processedKey: null }
  } catch {
    try {
      if (fs.statSync(target).isFile()) return { phase: "corrupt", processedKey: null }
    } catch {
      // Missing state is the ordinary first-cycle case.
    }
    return null
  }
}

function writeAdapterState(sessionID, turnID, value) {
  const target = adapterStatePath(sessionID, turnID)
  const temporary = `${target}.${process.pid}.${crypto.randomBytes(6).toString("hex")}.tmp`
  try {
    fs.mkdirSync(path.dirname(target), { recursive: true })
    fs.writeFileSync(temporary, JSON.stringify(value) + "\n", {
      encoding: "utf8",
      flag: "wx",
    })
    fs.renameSync(temporary, target)
    return true
  } catch {
    try {
      fs.unlinkSync(temporary)
    } catch {
      // A missing temporary file needs no cleanup.
    }
    return false
  }
}

function clearAdapterState(sessionID, turnID, processedKey = null) {
  const target = adapterStatePath(sessionID, turnID)
  if (processedKey !== null && readAdapterState(sessionID, turnID)?.processedKey !== processedKey) {
    return false
  }
  try {
    fs.unlinkSync(target)
    return true
  } catch (error) {
    return error?.code === "ENOENT"
  }
}

function pythonCommands() {
  if (process.platform === "win32") {
    return [
      ["py", ["-3"]],
      ["python", []],
    ]
  }
  return [
    ["python3", []],
    ["python", []],
  ]
}

function runCore(event, selectedCapability, directory) {
  if (!fs.existsSync(CORE_PATH)) return null
  const environment = {
    ...process.env,
    COW_GATE_HOOK_DATA: gateDataRoot(),
    COW_GATE_CAPABILITY: selectedCapability,
    PLUGIN_ROOT: OPENCODE_ROOT,
  }
  for (const [command, prefix] of pythonCommands()) {
    const result = spawnSync(command, [...prefix, CORE_PATH], {
      cwd: directory,
      encoding: "utf8",
      env: environment,
      input: JSON.stringify(event),
      maxBuffer: 2 * 1024 * 1024,
      timeout: 120_000,
      windowsHide: true,
    })
    if (result.error?.code === "ENOENT") continue
    if (result.error || result.status !== 0) return null
    try {
      const value = JSON.parse((result.stdout ?? "").trim())
      return value && typeof value === "object" ? value : null
    } catch {
      return null
    }
  }
  return null
}

function abortTurn(common, selectedCapability, directory, reason, processedKey) {
  const result = runCore(
    { ...common, hook_event_name: "HostAbort", abort_reason: reason },
    selectedCapability,
    directory,
  )
  if (result) {
    clearAdapterState(common.session_id, common.turn_id, processedKey)
    return true
  }
  writeAdapterState(common.session_id, common.turn_id, {
    phase: "abort_failed",
    processedKey,
  })
  return false
}

function toolCommand(part) {
  if (part?.type !== "tool" || part?.state?.status !== "completed") return null
  const input = part.state.input ?? {}
  if (part.tool === "skill") {
    const loadedRoot = part.state.metadata?.dir
    if (input.name !== "chinese-official-writing" || !samePath(loadedRoot, SKILL_ROOT)) {
      return { localSkill: false, staleSkill: input.name === "chinese-official-writing" }
    }
    return {
      command: `Get-Content "${path.join(SKILL_ROOT, "SKILL.md")}"`,
      localSkill: true,
      staleSkill: false,
    }
  }
  if (part.tool === "read") {
    const filePath = input.filePath ?? input.path
    if (typeof filePath === "string" && filePath) {
      return { command: `Get-Content "${filePath}"`, localSkill: false, staleSkill: false }
    }
  }
  if (part.tool === "bash") {
    const command = input.command ?? input.cmd
    if (typeof command === "string" && command) {
      return { command, localSkill: false, staleSkill: false }
    }
  }
  return null
}

async function log(client, level, message, extra = {}) {
  try {
    await client.app.log({
      body: { service: "chinese-official-writing-gate", level, message, extra },
    })
  } catch {
    // Logging must never change delivery behavior.
  }
}

function isHeadlessRun() {
  return process.argv.slice(2).some((value) => value === "run")
}

function delayMs() {
  const value = Number(process.env.COW_OPENCODE_GATE_DELAY_MS ?? DEFAULT_DELAY_MS)
  return Number.isFinite(value) && value >= 0 ? value : DEFAULT_DELAY_MS
}

async function handleIdle({ client, directory, event }) {
  const sessionID = event?.properties?.sessionID
  if (!sessionID || isHeadlessRun()) return

  const result = await client.session.messages({
    path: { id: sessionID },
    query: { directory },
  })
  const messages = messageList(result)
  const external = latestExternalUser(messages)
  if (!external) return
  const turnID = `opencode-${digest(external.id).slice(0, 24)}`
  const common = { session_id: sessionID, turn_id: turnID, cwd: directory }
  const selectedCapability = capability()
  const assistant = latestAssistant(messages, external.index)
  if (!assistant) return
  const latestInternalIndex = latestInternalContinuationIndex(messages, external.index)
  if (latestInternalIndex > assistant.index) {
    const pending = readAdapterState(sessionID, turnID)
    if (pending) {
      abortTurn(
        common,
        selectedCapability,
        directory,
        "continuation_failed",
        pending.processedKey,
      )
      await log(client, "error", "internal continuation ended without an assistant reply")
    }
    return
  }

  let state = sessionStates.get(sessionID)
  if (!state || state.externalID !== external.id) {
    state = { externalID: external.id, terminal: false, lastProcessed: "", staleWarned: false }
    sessionStates.set(sessionID, state)
  }
  if (state.terminal) return

  const continuationCount = internalContinuationCount(messages, external.index)
  const processedKey = `${continuationCount}:${assistant.id}:${digest(assistant.text)}`
  if (state.lastProcessed === processedKey) return
  state.lastProcessed = processedKey

  if (hasTerminalReceipt(sessionID, turnID)) {
    clearAdapterState(sessionID, turnID)
    state.terminal = true
    await log(client, "info", "terminal receipt already exists; skipping a replayed idle", {
      capability: selectedCapability,
      continuationCount,
    })
    return
  }
  const pending = readAdapterState(sessionID, turnID)
  if (
    pending &&
    (
      pending.processedKey === processedKey ||
      pending.phase === "abort_failed" ||
      pending.phase === "corrupt"
    )
  ) {
    const aborted = abortTurn(
      common,
      selectedCapability,
      directory,
      "pending_replay",
      pending.processedKey,
    )
    state.terminal = true
    await log(
      client,
      aborted ? "warn" : "error",
      "unfinished adapter cycle was not replayed after a module restart",
      { capability: selectedCapability, continuationCount, redacted: aborted },
    )
    return
  }
  if (!runCore({ ...common, hook_event_name: "UserPromptSubmit", prompt: external.text }, selectedCapability, directory)) {
    abortTurn(common, selectedCapability, directory, "adapter_failure", processedKey)
    state.terminal = true
    await log(client, "error", "shared gate core unavailable; leaving the current draft unchanged")
    return
  }

  let localSkillSeen = false
  let staleSkillSeen = false
  for (const message of messages.slice(external.index + 1)) {
    for (const part of message?.parts ?? []) {
      const mapped = toolCommand(part)
      if (!mapped) continue
      localSkillSeen ||= mapped.localSkill
      staleSkillSeen ||= mapped.staleSkill
      if (!mapped.command) continue
      runCore(
        {
          ...common,
          hook_event_name: "PostToolUse",
          tool_input: { command: mapped.command },
          tool_response: { exit_code: 0 },
        },
        selectedCapability,
        directory,
      )
    }
  }

  if (!localSkillSeen) {
    abortTurn(common, selectedCapability, directory, "skill_not_loaded", processedKey)
    state.terminal = true
    if (staleSkillSeen && !state.staleWarned) {
      state.staleWarned = true
      await log(
        client,
        "warn",
        "same-name external skill won discovery; OpenCode gate did not arm",
        { packagedSkillSha256: digest(fs.readFileSync(path.join(SKILL_ROOT, "SKILL.md"), "utf8")) },
      )
    }
    return
  }

  if (!writeAdapterState(sessionID, turnID, {
    phase: "evaluating",
    processedKey,
    continuationCount,
  })) {
    abortTurn(common, selectedCapability, directory, "adapter_failure", processedKey)
    state.terminal = true
    await log(client, "error", "adapter state could not be persisted; leaving D0 unchanged")
    return
  }
  const response = runCore(
    {
      ...common,
      hook_event_name: "Stop",
      stop_hook_active: continuationCount > 0,
      last_assistant_message: assistant.text,
    },
    selectedCapability,
    directory,
  )
  if (!response) {
    abortTurn(common, selectedCapability, directory, "adapter_failure", processedKey)
    state.terminal = true
    await log(client, "error", "shared gate call failed; leaving the current draft unchanged")
    return
  }
  if (response.decision !== "block" || typeof response.reason !== "string") {
    clearAdapterState(sessionID, turnID, processedKey)
    state.terminal = true
    await log(client, "info", "shared gate reached a terminal allow", {
      capability: selectedCapability,
      continuationCount,
      outputSha256: digest(assistant.text),
    })
    return
  }
  if (continuationCount >= MAX_HOST_CONTINUATIONS) {
    abortTurn(common, selectedCapability, directory, "host_ceiling", processedKey)
    state.terminal = true
    await log(client, "error", "OpenCode host continuation ceiling reached", {
      capability: selectedCapability,
      continuationCount,
    })
    return
  }

  if (!writeAdapterState(sessionID, turnID, {
    phase: "pending_prompt",
    processedKey,
    continuationCount,
  })) {
    abortTurn(common, selectedCapability, directory, "adapter_failure", processedKey)
    state.terminal = true
    await log(client, "error", "pending continuation could not be persisted; leaving D0 unchanged")
    return
  }

  setTimeout(async () => {
    try {
      const pendingPrompt = readAdapterState(sessionID, turnID)
      if (pendingPrompt?.phase === "corrupt") {
        abortTurn(common, selectedCapability, directory, "adapter_failure", null)
        await log(client, "error", "corrupt adapter state cancelled the pending continuation")
        return
      }
      if (
        pendingPrompt?.phase !== "pending_prompt" ||
        pendingPrompt.processedKey !== processedKey
      ) {
        return
      }
      const currentResult = await client.session.messages({
        path: { id: sessionID },
        query: { directory },
      })
      const currentMessages = messageList(currentResult)
      const currentExternal = latestExternalUser(currentMessages)
      const currentAssistant = currentExternal
        ? latestAssistant(currentMessages, currentExternal.index)
        : null
      const currentContinuationCount = currentExternal
        ? internalContinuationCount(currentMessages, currentExternal.index)
        : -1
      const currentProcessedKey = currentAssistant
        ? `${currentContinuationCount}:${currentAssistant.id}:${digest(currentAssistant.text)}`
        : ""
      if (
        currentExternal?.id !== external.id ||
        currentProcessedKey !== processedKey
      ) {
        const aborted = abortTurn(
          common,
          selectedCapability,
          directory,
          "turn_changed",
          processedKey,
        )
        await log(client, aborted ? "warn" : "error", "delayed continuation was cancelled because the session changed", {
          capability: selectedCapability,
          redacted: aborted,
        })
        return
      }
      if (!writeAdapterState(sessionID, turnID, {
        phase: "prompt_dispatching",
        processedKey,
        continuationCount,
      })) {
        abortTurn(common, selectedCapability, directory, "adapter_failure", processedKey)
        await log(client, "error", "continuation dispatch state could not be persisted")
        return
      }
      await client.session.prompt({
        path: { id: sessionID },
        query: { directory },
        body: { parts: [{ type: "text", text: INTERNAL_PREFIX + response.reason }] },
      })
      clearAdapterState(sessionID, turnID, processedKey)
    } catch (error) {
      abortTurn(common, selectedCapability, directory, "continuation_failed", processedKey)
      await log(client, "error", "OpenCode continuation failed", {
        error: error instanceof Error ? error.message : String(error),
      })
    }
  }, delayMs())
}

export const ChineseOfficialWritingGate = async ({ client, directory }) => ({
  event: async ({ event }) => {
    if (event?.type !== "session.idle") return
    try {
      await handleIdle({ client, directory, event })
    } catch (error) {
      await log(client, "error", "OpenCode adapter failed open", {
        error: error instanceof Error ? error.message : String(error),
      })
    }
  },
})
