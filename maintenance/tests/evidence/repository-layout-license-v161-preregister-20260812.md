# Repository layout and MIT cleanup v1.6.1 preregistration

Status: frozen before repository migration.

## User decisions

1. GitHub repository and every package tracked in GitHub use the single root MIT license.
2. Remove `LICENSE-SCOPE.md` and the extra ClawHub-specific license file; do not present the repository as multi-licensed.
3. Remote ClawHub is a separate external release surface and remains silently on its already-published v1.6.0 / platform-required MIT-0. This work must not call ClawHub publish or sync.
4. The GitHub OpenClaw compatibility bundle moves to v1.6.1 / MIT and is maintained with later GitHub versions while continuing to exclude Hook and delivery-gate assets.
5. The GitHub root should show only the repository entry files and the canonical general Agent Skill. Platform packages and engineering/maintenance material move below second-level roots.
6. README shows only the five most recent model-ablation/real-writing entries and points to the internal evidence index for complete history.
7. README adds the later news-message and news-commentary abilities, removes internal release scheduling, and removes the redundant manual-deployment sentence.

## Target root layout

```text
/
  .gitattributes
  .gitignore
  AGENTS.md
  LICENSE
  README.md
  chinese-official-writing/   # canonical general Agent Skill
  packages/                   # platform packages and mirrors
  maintenance/                # tools, tests, evals, docs and package tooling
```

Planned package layout:

```text
packages/
  agent-plugin/
  agent-skills/
  qwen-code/
  hermes/
  openclaw/
  red-skillhub/
```

Planned maintenance layout:

```text
maintenance/
  docs/
  evals/
  tests/
  tools/
  package.json
  package-lock.json
```

## External references checked before implementation

- OpenAI Skills catalog: skill folders contain `SKILL.md` and only necessary agents/references/scripts; repository support material is separate. <https://github.com/openai/skills>
- OpenAI Plugins `writing-skills`: keeps a flat skill namespace and places heavy references/tools below each skill. <https://github.com/openai/plugins/blob/main/plugins/superpowers/skills/writing-skills/SKILL.md>
- A single-skill OpenClaw repository with a compact public root (`SKILL.md`, references and README files): <https://github.com/win4r/OpenClaw-Skill>
- OpenClaw Agent Skills catalog: skills live below `skills/<name>/`, while repository-level validation scripts stay outside skill folders. <https://github.com/openclaw/agent-skills>
- ClawHub skill format: remote ClawHub skills are distributed under the platform MIT-0 rule and do not support per-skill license override. <https://docs.openclaw.ai/clawhub/skill-format>

No third-party code, prompt, regular expression or template is copied.

## Hard boundaries

- No change to the canonical writing rules or their behavior.
- Preserve Git history with tracked moves.
- Do not rewrite historical evidence merely to replace old path strings or past release facts.
- Update current README/index links, build scripts, tests, package paths and plugin manifests to the new layout.
- Keep remote ClawHub at v1.6.0; do not run publish, sync or any other mutation against it.
- Do not publish SkillHub or Red SkillHub in this task.
- Before delivery: full unit discovery, Promptfoo stub smoke, deterministic ablation, quick validation, plugin/package validation, repeated sync idempotence, link/path audit, license audit and `git diff --check`.
