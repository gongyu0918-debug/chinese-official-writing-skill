# SkillHub dynamic downloads badge result

## Scope

- README badge-only change; no writing rule, package version, Hook, build, license, release, or marketplace mutation.
- The badge reads the public SkillHub `downloads` counter dynamically. It does not display or relabel `installs`.
- The badge and its count link to the public SkillHub detail page: `https://skillhub.cn/skills/chinese-official-writing`.

## Public API snapshot

Read-only GET at `2026-08-11T18:23:27.510Z`:

`https://api.skillhub.cn/api/v1/skills/chinese-official-writing`

```json
{"downloads":37341,"installs":53,"stars":44,"api_slug":"chinese-official-writing"}
```

These values are a time-stamped observation only. README and the contract test do not hard-code any counter value.

## Shields request and response

Request URL:

`https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.skillhub.cn%2Fapi%2Fv1%2Fskills%2Fchinese-official-writing&query=%24.skill.stats.downloads&label=SkillHub%20downloads&color=2f855a&cacheSeconds=3600`

- HTTP status: `200`.
- Content-Type: `image/svg+xml; charset=utf-8`.
- SVG aria-label: `SkillHub downloads: 37341`.
- Response-body SHA-256: `e2e516e2a85e8f8247fa502b0da9b8b0fc7b8365d31fb33906c1b1b63bb14c53`.
- Exact response content snapshot: [`skillhub-download-badge-response-20260812.svg`](skillhub-download-badge-response-20260812.svg). The repository file adds its normal final newline; its file SHA-256 is `a515423cd538c0f8248bbe6ca9c1e6e35338b03777151419cfdf4911d737f7bb`.

## Contract

`tests/test_readme_badges.py` parses the badge URL and locks the public API URL, JSON query `$.skill.stats.downloads`, label, one-hour Shields cache, and SkillHub detail link. It rejects an `installs` query and rejects embedding the observed counts in the badge URL.
