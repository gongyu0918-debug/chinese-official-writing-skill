# SkillHub downloads badge result

## Scope

- README badge-only change; no writing rule, package version, Hook, build, license, release, or marketplace mutation.
- The final badge shows the conservative static downloads floor `37k+`. It does not display or relabel `installs` and has no runtime dependency on the SkillHub JSON API.
- The badge and its count link to the public SkillHub detail page: `https://skillhub.cn/skills/chinese-official-writing`.

## Public API snapshot

Read-only GET at `2026-08-11T18:23:27.510Z`:

`https://api.skillhub.cn/api/v1/skills/chinese-official-writing`

```json
{"downloads":37341,"installs":53,"stars":44,"api_slug":"chinese-official-writing"}
```

These values are a time-stamped observation. They establish that the conservative `37k+` floor was already met.

## Rejected dynamic attempt

Request URL:

`https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.skillhub.cn%2Fapi%2Fv1%2Fskills%2Fchinese-official-writing&query=%24.skill.stats.downloads&label=SkillHub%20downloads&color=2f855a&cacheSeconds=3600`

- HTTP status: `200`.
- Content-Type: `image/svg+xml; charset=utf-8`.
- SVG aria-label: `SkillHub downloads: 37341`.
- Response-body SHA-256: `e2e516e2a85e8f8247fa502b0da9b8b0fc7b8365d31fb33906c1b1b63bb14c53`.
- Exact successful response content snapshot: [`skillhub-download-badge-response-20260812.svg`](skillhub-download-badge-response-20260812.svg). The repository file adds its normal final newline; its file SHA-256 is `a515423cd538c0f8248bbe6ca9c1e6e35338b03777151419cfdf4911d737f7bb`.

This initial response proved that the query could work once; it did not prove stable badge delivery. During final main-thread verification, the public API had advanced to `downloads=37346`, but the same Shields dynamic URL returned HTTP 200 with `aria-label="SkillHub downloads: inaccessible"`. The dynamic candidate was therefore rejected and is not present in final README.

## Final static badge

`https://img.shields.io/badge/SkillHub%20downloads-37k%2B-2f855a`

The final badge deliberately states only the verified lower bound. It remains linked to the SkillHub detail page, while readers can use that page for the current exact count.

## Contract

`tests/test_readme_badges.py` locks the encoded static `37k+` badge URL and SkillHub detail link. It rejects a `dynamic/json` dependency, an `inaccessible` label, and an installs label. The test is offline and does not turn an external service response into a repository test dependency.
