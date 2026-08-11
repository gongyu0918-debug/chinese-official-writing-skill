# Claude Code third-party gateway Hook smoke v1.6.2 preregistration

## Official contract and local probe

- Claude Code official gateway contract: <https://code.claude.com/docs/en/llm-gateway>
- Claude Code model configuration: <https://code.claude.com/docs/en/model-config>
- Claude plugin path/data substitutions: <https://code.claude.com/docs/en/plugins-reference>
- The gateway must expose Anthropic Messages `/v1/messages` and `/v1/messages/count_tokens` or a documented Bedrock/Vertex equivalent.
- Local `http://127.0.0.1:10100` returned `200` for both Anthropic POST probes with `ollama-cloud/deepseek-v4-flash:0731`. The earlier GET `404` is not used as a protocol verdict because these are POST endpoints.

## Fixed candidate and isolated invocation

- Candidate: `0cbb3a39` on `codex/v1602-integration`.
- Claude Code: `2.1.195`.
- Plugin: `chinese-official-writing/hooks/claude-code`.
- Gateway environment is process-local only: `ANTHROPIC_BASE_URL=http://127.0.0.1:10100`, a non-secret local probe token, the Ollama Cloud DeepSeek V4 Flash 0731 model ID, and `--effort max`.
- Use a temporary `CLAUDE_CONFIG_DIR`, empty setting sources, `--no-session-persistence`, the `Read` tool only, and a public deterministic probe. Do not log in, read or copy user credentials, write user/project/global settings, install the plugin, or bypass permissions.
- The probe asks the model to read the canonical `SKILL.md` and initially emit a known delivery-metadata line so the real `UserPromptSubmit -> PostToolUse:Read -> Stop` chain can be observed.

## Evidence and interpretation

- Save the raw stream, stderr, temporary plugin data inventory, event sequence, return code, model binding, and D0/D1/final hashes. Redact or omit local memory paths from committed raw evidence.
- One actual request, first final, zero retry. A parser or protocol failure is retained and not replaced in the same run.
- Registration-only evidence is not a Stop pass. A lifecycle pass requires a real `Read`, a real `Stop`, an adapter/core transaction under the temporary plugin data root, and a terminal allow or bounded block/continue result.
- Stop if Claude Code falls back to first-party auth, the gateway model differs, the plugin writes outside the temporary config/data root, or the Hook state cannot be bound to the same session and turn.
