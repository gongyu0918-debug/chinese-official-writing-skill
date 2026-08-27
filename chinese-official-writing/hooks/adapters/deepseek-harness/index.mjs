import { spawn } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { appendFile, mkdir } from 'node:fs/promises'
import { homedir } from 'node:os'
import { dirname, isAbsolute, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'chinese-official-writing-gate-dsh'
export const inject = ['skills']

const PLUGIN_ROOT = dirname(fileURLToPath(import.meta.url))
const SKILL_ROOT = join(PLUGIN_ROOT, 'skills', 'chinese-official-writing')
const SKILL_PATH = join(SKILL_ROOT, 'SKILL.md')
const CORE_PATH = join(SKILL_ROOT, 'hooks', 'gate_stop_hook.py')
const CAPABILITY_PATH = join(PLUGIN_ROOT, 'hook-capability.json')
const DEFAULT_CAPABILITY = 'delivery_review'
const MAX_OUTPUT_BYTES = 1024 * 1024
const MAX_HOST_STOPS = 9
const SUPPORTED_CAPABILITIES = new Set([
  DEFAULT_CAPABILITY,
  'protective_expansion',
  'under_length',
  'over_length',
  'delivery_cleanliness',
  'repetition_cleanup',
])

function digest(value) {
  return createHash('sha256').update(value, 'utf8').digest('hex')
}

function textOf(content) {
  if (!Array.isArray(content)) return ''
  return content
    .filter(block => block?.type === 'text' && typeof block.text === 'string')
    .map(block => block.text)
    .join('')
}

function samePath(left, right) {
  try {
    const normalize = value => {
      const path = resolve(value)
      return process.platform === 'win32' ? path.toLowerCase() : path
    }
    return normalize(left) === normalize(right)
  } catch {
    return false
  }
}

function parseSkill() {
  const raw = readFileSync(SKILL_PATH, 'utf8')
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/)
  if (!match) throw new Error('invalid SKILL.md frontmatter')
  const nameMatch = match[1].match(/^name:\s*(.+)$/m)
  const descriptionMatch = match[1].match(/^description:\s*(.+)$/m)
  if (!nameMatch || !descriptionMatch) throw new Error('missing skill identity')
  return {
    name: nameMatch[1].trim(),
    description: descriptionMatch[1].trim(),
    content: match[2],
  }
}

function selectedCapability() {
  try {
    const value = JSON.parse(readFileSync(CAPABILITY_PATH, 'utf8'))?.capability
    return SUPPORTED_CAPABILITIES.has(value) ? value : DEFAULT_CAPABILITY
  } catch {
    return DEFAULT_CAPABILITY
  }
}

function dataRoot() {
  const configured = process.env.COW_DSH_GATE_DATA
  if (configured && isAbsolute(configured)) return resolve(configured)
  const home = process.env.DSH_HOME
  const harnessHome = home ? resolve(home) : join(homedir(), '.dsh')
  return join(harnessHome, 'plugin-data', 'chinese-official-writing-gate')
}

function pythonCommands() {
  return process.platform === 'win32'
    ? [['py', ['-3']], ['python', []]]
    : [['python3', []], ['python', []]]
}

function runPython(command, prefix, event, capability, root, signal) {
  return new Promise(resolveResult => {
    let stdout = ''
    let settled = false
    const child = spawn(command, [...prefix, CORE_PATH], {
      cwd: event.cwd,
      windowsHide: true,
      env: {
        ...process.env,
        COW_GATE_HOOK_DATA: root,
        COW_GATE_CAPABILITY: capability,
        PLUGIN_ROOT,
      },
      stdio: ['pipe', 'pipe', 'pipe'],
    })
    const finish = result => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      signal?.removeEventListener('abort', abort)
      resolveResult(result)
    }
    const abort = () => {
      child.kill()
      finish({ kind: 'error', code: 'aborted' })
    }
    const timer = setTimeout(() => {
      child.kill()
      finish({ kind: 'error', code: 'timeout' })
    }, 120_000)
    signal?.addEventListener('abort', abort, { once: true })
    child.on('error', error => {
      finish({
        kind: 'error',
        code: error?.code === 'ENOENT' ? 'interpreter_missing' : 'spawn_failed',
      })
    })
    child.stdout.on('data', chunk => {
      if (stdout.length < MAX_OUTPUT_BYTES) stdout += chunk.toString('utf8')
    })
    child.stderr.on('data', () => {})
    child.on('close', code => {
      if (code !== 0) return finish({ kind: 'error', code: 'core_exit' })
      try {
        const value = JSON.parse(stdout)
        if (value?.decision === 'block' && typeof value.reason === 'string') {
          return finish({ kind: 'block', reason: value.reason })
        }
        return finish({ kind: 'allow' })
      } catch {
        return finish({ kind: 'error', code: 'invalid_core_output' })
      }
    })
    child.stdin.end(JSON.stringify(event))
  })
}

async function runCore(event, capability, root, signal) {
  try {
    if (!existsSync(CORE_PATH)) return { kind: 'error', code: 'core_missing' }
    for (const [command, prefix] of pythonCommands()) {
      const result = await runPython(command, prefix, event, capability, root, signal)
      if (result.code === 'interpreter_missing') continue
      return result
    }
    return { kind: 'error', code: 'interpreter_missing' }
  } catch {
    return { kind: 'error', code: 'spawn_failed' }
  }
}

function commonEvent(state, event) {
  return {
    ...event,
    session_id: state.sessionId,
    turn_id: state.turnId,
    cwd: state.cwd,
  }
}

async function recordReceipt(root, value) {
  try {
    await mkdir(root, { recursive: true })
    await appendFile(join(root, 'dsh-adapter-receipts.jsonl'), `${JSON.stringify(value)}\n`, 'utf8')
  } catch {
    // Receipt failure must not change the writing result.
  }
}

function latestAssistant(agent, turn) {
  const source = agent?.session?.events
  const events = source && typeof source[Symbol.iterator] === 'function' ? [...source] : []
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index]
    if (
      event?.type === 'assistant/message' &&
      event.data?.turn === turn &&
      event.data?.interrupted !== true
    ) {
      const text = textOf(event.data?.message?.content).trim()
      if (text) return text
    }
  }
  return ''
}

function loadedPackagedSkill(value, skillName) {
  return (
    value?.name === skillName &&
    value?.resourceBase?.kind === 'directory' &&
    samePath(value.resourceBase.path, SKILL_ROOT)
  )
}

function commandForTool(exec, result, skillName) {
  const args = exec?.arguments && typeof exec.arguments === 'object' ? exec.arguments : {}
  if (exec?.name === 'skill') {
    return loadedPackagedSkill(result?.value, skillName) ? SKILL_PATH : null
  }
  if (['read', 'read_file', 'Read', 'ReadFile'].includes(exec?.name)) {
    return args.file_path ?? args.path ?? null
  }
  if (['bash', 'pwsh', 'Bash', 'run_shell_command'].includes(exec?.name)) {
    return args.command ?? args.cmd ?? args.script ?? null
  }
  return null
}

function isPackagedInvocation(messages, skillName) {
  return messages.some(message =>
    message?.source?.kind === 'skill-invocation' && message.source.name === skillName)
}

async function abortState(state, capability, root, reason) {
  return runCore(commonEvent(state, {
    hook_event_name: 'HostAbort',
    abort_reason: reason,
  }), capability, root)
}

function steer(agent, reason) {
  agent.steer(Object.freeze({
    id: randomUUID(),
    role: 'user',
    content: [Object.freeze({ type: 'text', text: reason })],
    source: Object.freeze({ kind: 'plugin', plugin: name }),
  }))
}

export function apply(ctx) {
  const capability = selectedCapability()
  const root = dataRoot()
  const skill = parseSkill()
  const states = new Map()

  const disposeSkill = ctx.skills.register({
    ...skill,
    source: 'runtime',
    path: SKILL_PATH,
    resourceBase: { kind: 'directory', path: SKILL_ROOT },
  })
  ctx.effect(() => disposeSkill, 'chinese-official-writing-gate-dsh: skill')

  ctx.on('agent/pre-step', async ({ agent, messages, turn, signal }, next) => {
    const decision = await next()
    if (decision?.kind === 'reject' || !Array.isArray(messages) || messages.length === 0) {
      return decision
    }
    const current = states.get(agent)
    if (current?.turn === turn) return decision
    if (current) await abortState(current, capability, root, 'turn_changed')

    const prompt = messages
      .filter(message => message?.source?.kind === 'user')
      .map(message => textOf(message.content))
      .join('\n')
      .trim()
    if (!prompt) return decision
    const state = {
      sessionId: String(agent.session.header.id),
      turn,
      turnId: `dsh-${turn}-${digest(prompt).slice(0, 16)}`,
      cwd: String(agent.session.header.cwd),
      stopCount: 0,
      originalDraft: null,
      fallbackPending: false,
    }
    states.set(agent, state)
    const submitted = await runCore(commonEvent(state, {
      hook_event_name: 'UserPromptSubmit',
      prompt,
    }), capability, root, signal)
    if (submitted.kind === 'error') {
      await abortState(state, capability, root, 'adapter_failure')
      states.delete(agent)
      return decision
    }

    const effectiveMessages = decision?.kind === 'enter' ? decision.messages : messages
    if (isPackagedInvocation(effectiveMessages, skill.name)) {
      let loaded
      try {
        loaded = await ctx.skills.get(skill.name, {
          cwd: state.cwd,
          signal,
          scope: agent,
        })
      } catch {
        await abortState(state, capability, root, 'adapter_failure')
        states.delete(agent)
        return decision
      }
      if (loadedPackagedSkill(loaded, skill.name)) {
        await runCore(commonEvent(state, {
          hook_event_name: 'PostToolUse',
          tool_input: { command: SKILL_PATH },
          tool_response: { is_error: false },
        }), capability, root, signal)
      }
    }
    return decision
  })

  ctx.on('tools/post-execute', async (exec, result, next) => {
    const state = exec?.agent ? states.get(exec.agent) : null
    const command = state ? commandForTool(exec, result, skill.name) : null
    if (state && typeof command === 'string' && command) {
      await runCore(commonEvent(state, {
        hook_event_name: 'PostToolUse',
        tool_input: { command },
        tool_response: { is_error: result?.isError === true },
      }), capability, root, exec.signal)
    }
    return next()
  })

  ctx.on('agent/turn-stopping', async ({ agent, turn, signal }) => {
    const state = states.get(agent)
    if (!state || state.turn !== turn) return
    const draft = latestAssistant(agent, turn)
    if (!draft) {
      await abortState(state, capability, root, 'adapter_failure')
      states.delete(agent)
      return
    }
    if (state.originalDraft === null) state.originalDraft = draft
    const stopPosition = state.stopCount
    state.stopCount += 1

    if (state.fallbackPending) {
      await recordReceipt(root, {
        session_id: state.sessionId,
        turn_id: state.turnId,
        turn,
        stop_position: stopPosition,
        draft_sha256: digest(draft),
        decision: digest(draft) === digest(state.originalDraft) ? 'allow_d0_fallback' : 'allow_fallback_mismatch',
      })
      states.delete(agent)
      return
    }

    const outcome = await runCore(commonEvent(state, {
      hook_event_name: 'Stop',
      stop_hook_active: stopPosition > 0,
      last_assistant_message: draft,
    }), capability, root, signal)
    await recordReceipt(root, {
      session_id: state.sessionId,
      turn_id: state.turnId,
      turn,
      stop_position: stopPosition,
      draft_sha256: digest(draft),
      decision: outcome.kind === 'block' ? 'block' : outcome.kind === 'allow' ? 'allow' : 'core_error',
      ...(outcome.kind === 'error' ? { error_code: outcome.code } : {}),
    })

    if (outcome.kind === 'block' && stopPosition < MAX_HOST_STOPS) {
      steer(agent, outcome.reason)
      return
    }
    if (outcome.kind === 'allow') {
      states.delete(agent)
      return
    }

    await abortState(state, capability, root, 'adapter_failure')
    if (stopPosition === 0 || draft === state.originalDraft) {
      states.delete(agent)
      return
    }
    state.fallbackPending = true
    steer(
      agent,
      `DeepSeek Harness 交付适配已安全回退。请逐字输出下列 D0，不要调用工具、不要加说明：\n${state.originalDraft}`,
    )
  })

  ctx.on('agent/disposed', ({ agent }) => {
    const state = states.get(agent)
    if (!state) return
    states.delete(agent)
    void abortState(state, capability, root, 'adapter_failure').catch(() => {})
  })

  ctx.effect(() => async () => {
    const pending = [...states.values()]
    states.clear()
    await Promise.allSettled(
      pending.map(state => abortState(state, capability, root, 'adapter_failure')),
    )
  }, 'chinese-official-writing-gate-dsh: active turns')
}
