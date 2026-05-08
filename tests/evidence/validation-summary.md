# Validation Summary

Date: 2026-05-08

This file records anonymized validation results for the `official-writing` skill. It does not include raw prompts, raw generated official documents, user project materials, private company information, or identifiable internal data.

## Structural Validation

- Skill folder structure validation: passed.
- Required `SKILL.md` frontmatter validation: passed.
- `prose_lint.py` syntax compilation: passed.
- Script can scan plain text, Markdown, stdin, and DOCX content.

## Lint Coverage

The lint helper detects:

- paired-summary frames such as "not X but Y" style structures in Chinese,
- side-commentary and teaching voice,
- casual phrases unsuitable for formal documents,
- repeated template expressions,
- vague AI-compute claims such as "advanced computing power" without measurable indicators.

The script reports findings only and does not rewrite user text.
