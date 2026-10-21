# sstack

Personal Claude Code skills, packed as one plugin.

| Skill | Use |
|---|---|
| `sstack:viz` | House style for chart pages: self-explaining static SVG, structured hovers. |

## Install

```sh
claude plugin marketplace add Sparshith/sstack
claude plugin install sstack@sstack
```

After an edit, run `claude plugin marketplace update sstack` and restart the session.

## Add a skill

Make `plugins/sstack/skills/<name>/SKILL.md` with `name` and `description` frontmatter. Put files the skill uses next to it. Bump `version` in both JSON manifests.
