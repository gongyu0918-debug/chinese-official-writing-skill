// Mock host services, real packaged adapter, frozen core terminal response.
import fs from 'node:fs'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
const [host, companion, data, draftFile] = process.argv.slice(2)
const draft = fs.readFileSync(draftFile, 'utf8')
const messages = []
const steers = []
const cancels = []
const logs = []
const toasts = []
const signal = new AbortController().signal
if (host === 'deepseek-harness') {
  process.env.COW_DSH_GATE_DATA = data
  const { apply } = await import(pathToFileURL(path.join(companion, 'index.mjs')).href)
  const handlers = new Map()
  let skill
  apply({
    skills: { register(value) { skill = value; return () => {} }, async get() { return skill } },
    effect(factory) { factory() },
    on(event, handler) { handlers.set(event, handler) },
  })
  const agent = {
    session: { header: { id: 'real-d0-protocol', cwd: companion }, events: messages },
    steer(value) { steers.push(value) },
    cancel(cause, options) { cancels.push({ cause, options }) },
  }
  const user = { role: 'user', content: [{ type: 'text', text: '请起草整改方案。' }], source: { kind: 'user' } }
  await handlers.get('agent/pre-step')({ agent, turn: 1, messages: [user], signal }, async () => ({ kind: 'enter', messages: [user] }))
  messages.push({ type: 'assistant/message', data: { turn: 1, message: { content: [{ type: 'text', text: draft }] } } })
  await handlers.get('agent/turn-stopping')({ agent, turn: 1, signal })
  await handlers.get('agent/turn-stopping')({ agent, turn: 1, signal })
  const receipts = fs.readFileSync(path.join(data, 'dsh-adapter-receipts.jsonl'), 'utf8').trim().split('\n').map(JSON.parse)
  console.log(JSON.stringify({ host, scope: 'MOCK_HOST_PROTOCOL_NOT_NATIVE', steers, cancels, receipts }))
} else {
  process.env.COW_OPENCODE_GATE_DATA = data
  process.env.COW_OPENCODE_GATE_DELAY_MS = '0'
  const plugin = pathToFileURL(path.join(companion, '.opencode/plugins/chinese-official-writing-gate.js')).href
  const skill = path.join(companion, '.opencode/skills/chinese-official-writing')
  messages.push({ info: { id: 'user-1', role: 'user' }, parts: [{ type: 'text', text: '请起草整改方案。' }] })
  messages.push({ info: { id: 'assistant-1', role: 'assistant' }, parts: [
    { type: 'tool', tool: 'skill', state: { status: 'completed', input: { name: 'chinese-official-writing' }, metadata: { dir: skill } } },
    { type: 'text', text: draft },
  ] })
  const client = {
    app: { async log(value) { logs.push(value) } },
    tui: { async showToast(value) { toasts.push(value) } },
    session: { async messages() { return { data: messages } }, async prompt(value) { steers.push(value) }, async abort(value) { cancels.push(value); return { data: true } } },
  }
  const { ChineseOfficialWritingGate } = await import(plugin)
  const hook = await ChineseOfficialWritingGate({ client, directory: companion })
  const event = { event: { type: 'session.idle', properties: { sessionID: 'real-d0-protocol' } } }
  await hook.event(event)
  await hook.event(event)
  const restarted = await import(plugin + '?restart=1')
  await (await restarted.ChineseOfficialWritingGate({ client, directory: companion })).event(event)
  await new Promise(resolve => setTimeout(resolve, 40))
  console.log(JSON.stringify({ host, scope: 'MOCK_HOST_PROTOCOL_NOT_NATIVE', steers, cancels, logs, toasts }))
}
