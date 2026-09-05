// Installed DSH AgentLoop; only the LLM adapter and Skill registry are fixtures.
// No host profile, credentials, network tools, or model service is loaded.
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
const [companion, output, draftFile] = process.argv.slice(2).map(value => path.resolve(value))
const installed = 'C:/Users/admin/AppData/Roaming/npm/node_modules/@deepseek-ai/dsh/package.json'
const require = createRequire(installed)
const load = name => import(pathToFileURL(require.resolve(name)).href)
const { Context } = await load('@deepseek-ai/cordis')
const { default: LlmRuntime, LlmAdapter, createUserMessage } = await load('@deepseek-ai/dsh-llm')
const { default: SessionStore, SessionId } = await load('@deepseek-ai/dsh-session')
const { default: SystemPrompt } = await load('@deepseek-ai/dsh-system-prompt')
const { default: ToolRuntime } = await load('@deepseek-ai/dsh-tools')
const { default: AgentRegistry } = await load('@deepseek-ai/dsh-agent')
const { default: AgentLoop } = await load('@deepseek-ai/dsh-agent-loop')
const { default: SessionProjectionRegistry } = await load('@deepseek-ai/dsh-session-projection')
const draft = fs.readFileSync(draftFile, 'utf8')
const keepQueued = process.argv[5] === 'queue'
let requests = 0
class MockAdapter extends LlmAdapter {
  async resolveModel(provider, model) { return { provider, id: model, name: model } }
  async *stream() {
    if (++requests !== 1) throw new Error('unexpected second MockAdapter request')
    yield { type: 'block-start', index: 0, blockType: 'text' }
    yield { type: 'text-delta', index: 0, text: draft }
    yield { type: 'block-end', index: 0, block: { type: 'text', text: draft } }
    yield { type: 'finish', reason: { kind: 'stop' } }
  }
}
const ctx = new Context()
for (const plugin of [LlmRuntime, SessionStore, SessionProjectionRegistry, SystemPrompt, ToolRuntime, AgentRegistry]) await ctx.plugin(plugin)
await ctx.plugin(AgentLoop, { agents: [] })
ctx.llm.registerAdapter(['mock'], new MockAdapter())
if (keepQueued) {
  ctx.on('agent/turn-stopping', ({ agent }) => {
    agent.followup(createUserMessage({ content: [{ type: 'text', text: '用户已排队的下一项独立请求' }], source: { kind: 'user' } }))
  })
}
process.env.COW_DSH_GATE_DATA = path.join(output, 'gate-data')
const { apply } = await import(pathToFileURL(path.join(companion, 'index.mjs')).href)
let skill
apply({
  skills: { register(value) { skill = value; return () => {} }, async get() { return skill } },
  on: ctx.on.bind(ctx), effect: ctx.effect.bind(ctx),
})
const agent = await ctx.agentLoop.create(SessionId('frozen-real-d0'), { provider: 'mock', model: 'mock' }, { cwd: companion })
agent.followup(createUserMessage({ content: [{ type: 'text', text: '请起草整改方案。' }], source: { kind: 'user' } }))
await agent.whenIdle()
const events = [...agent.session.events]
const terminal = events.filter(event => event.type === 'turn/end').map(event => event.data.reason)
fs.mkdirSync(output, { recursive: true })
fs.writeFileSync(path.join(output, 'session-events.json'), JSON.stringify(events, null, 2) + '\n')
const result = {
  scope: 'INSTALLED_DSH_AGENT_LOOP_WITH_MOCK_ADAPTER_NOT_NATIVE_CLI_OR_MODEL',
  version: JSON.parse(fs.readFileSync(installed, 'utf8')).version,
  model_calls: 0, mock_requests: requests,
  d0_sha256: crypto.createHash('sha256').update(draft, 'utf8').digest('hex'),
  terminal,
  queued_after_abort: [...agent.inbox.nextTurn],
}
fs.writeFileSync(path.join(output, 'result.json'), JSON.stringify(result, null, 2) + '\n')
console.log(JSON.stringify(result))
await ctx.fiber.dispose()
