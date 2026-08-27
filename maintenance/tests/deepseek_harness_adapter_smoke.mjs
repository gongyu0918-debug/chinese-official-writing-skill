import { readFile } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const companion = resolve(process.argv[2])
const gateData = resolve(process.argv[3])
process.env.COW_DSH_GATE_DATA = gateData

const plugin = await import(pathToFileURL(join(companion, 'index.mjs')).href)
const handlers = new Map()
const cleanups = []
let registeredSkill = null

const ctx = {
  skills: {
    register(skill) {
      registeredSkill = skill
      return () => { registeredSkill = null }
    },
    async get(name) {
      return registeredSkill?.name === name ? registeredSkill : undefined
    },
  },
  effect(factory) {
    const cleanup = factory()
    if (typeof cleanup === 'function') cleanups.push(cleanup)
    return cleanup
  },
  on(name, handler) {
    handlers.set(name, handler)
    return () => handlers.delete(name)
  },
}

plugin.apply(ctx)

function message(text, source = { kind: 'user' }) {
  return { role: 'user', content: [{ type: 'text', text }], source }
}

function agent(id) {
  const steers = []
  return {
    session: { header: { id, cwd: companion }, events: [] },
    steers,
    steer(value) { steers.push(value) },
  }
}

function assistant(target, turn, text) {
  target.session.events.push({
    type: 'assistant/message',
    data: {
      turn,
      interrupted: false,
      message: { role: 'assistant', content: [{ type: 'text', text }] },
    },
  })
}

async function start(target, turn, prompt) {
  const user = message(prompt)
  return handlers.get('agent/pre-step')(
    { agent: target, messages: [user], turn, step: 1, signal: new AbortController().signal },
    async () => ({ kind: 'enter', messages: [user] }),
  )
}

async function loadSkill(target) {
  return handlers.get('tools/post-execute')(
    {
      agent: target,
      name: 'skill',
      arguments: { name: 'chinese-official-writing' },
      signal: new AbortController().signal,
    },
    {
      isError: false,
      value: {
        name: registeredSkill.name,
        resourceBase: registeredSkill.resourceBase,
        content: registeredSkill.content,
      },
      content: [],
    },
    async () => ({ kind: 'accept' }),
  )
}

async function stop(target, turn) {
  await handlers.get('agent/turn-stopping')({
    agent: target,
    turn,
    signal: new AbortController().signal,
  })
}

const d0 = '情况报告\n\n测试工作已完成。'
const live = agent('session-smoke-live')
await start(live, 1, '请使用 chinese-official-writing 技能起草一份情况报告。')
await loadSkill(live)
assistant(live, 1, d0)
await stop(live, 1)
const firstBlocked = live.steers.length === 1
assistant(live, 1, d0)
await stop(live, 1)
const terminalAllowed = live.steers.length === 1

const external = agent('session-smoke-external')
await start(external, 1, '请起草一份情况报告。')
await handlers.get('tools/post-execute')(
  {
    agent: external,
    name: 'skill',
    arguments: { name: 'chinese-official-writing' },
    signal: new AbortController().signal,
  },
  {
    isError: false,
    value: {
      name: 'chinese-official-writing',
      resourceBase: { kind: 'directory', path: join(companion, 'external-skill') },
      content: 'external',
    },
    content: [],
  },
  async () => ({ kind: 'accept' }),
)
assistant(external, 1, d0)
await stop(external, 1)
const externalSkillRejected = external.steers.length === 0

const changed = agent('session-smoke-turn-change')
await start(changed, 1, '请起草包含内部编号R-17的情况报告。')
await loadSkill(changed)
await start(changed, 2, '请起草另一份情况报告。')

for (const cleanup of cleanups.reverse()) await cleanup()

const liveRecord = JSON.parse(await readFile(
  join(gateData, 'candidate-ai-gate-hook', 'session-smoke-live', 'dsh-1-54a10ef2d0a2bc12.json'),
  'utf8',
).catch(async () => {
  const { readdir } = await import('node:fs/promises')
  const directory = join(gateData, 'candidate-ai-gate-hook', 'session-smoke-live')
  const [record] = await readdir(directory)
  return readFile(join(directory, record), 'utf8')
}))
const changedDirectory = join(gateData, 'candidate-ai-gate-hook', 'session-smoke-turn-change')
const { readdir } = await import('node:fs/promises')
const changedRecords = await readdir(changedDirectory)
const changedValues = await Promise.all(changedRecords
  .filter(name => name.endsWith('.json'))
  .map(name => readFile(join(changedDirectory, name), 'utf8').then(JSON.parse)))

console.log(JSON.stringify({
  firstBlocked,
  terminalAllowed,
  rawRetained: JSON.stringify(liveRecord).includes('测试工作已完成'),
  redacted: liveRecord.data_retention_state === 'raw_turn_data_redacted',
  externalSkillRejected,
  turnChangeRedacted: changedValues.every(value => value.data_retention_state === 'raw_turn_data_redacted'),
}))
