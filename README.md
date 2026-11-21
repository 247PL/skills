# 247PL Agent Skills

Open-source AI agent skills maintained by **247PL**, built on the open `SKILL.md` standard. Compatible with **Claude Code**, **Codex**, **Hermes Agent**, **Antigravity**, **Cursor**, **OpenCode**, and any other `SKILL.md`-compatible agent.

## Available Skills

### Web
| Skill | Description | Install |
| :--- | :--- | :--- |
| **[`website-qa-audit`](./skills/website-qa-audit/)** | Live real-browser QA, UX/UI, visual, copywriting, legal/contact, and technical/SEO audit across desktop, laptop/tablet, and mobile viewports (`quick`, `deep`, `re-audit` + optional Performance, WCAG, GDPR, and Passive Security modules). | `npx skills add 247PL/skills --skill website-qa-audit` |

### Video
*(Coming soon)*

### Graphics
*(Coming soon)*

## Installation

### Using `skills` CLI (Recommended)

Install a single skill:
```bash
npx skills add 247PL/skills --skill website-qa-audit
```

Or install all skills from this repository:
```bash
npx skills add 247PL/skills
```

### Manual Installation

Clone this repository and link or copy `skills/<skill-name>` into your agent's skills directory:

| Agent | Global Path | Workspace / Project Path |
| :--- | :--- | :--- |
| **Universal / Cross-Agent** | `~/.agents/skills/<skill>` | `<project>/.agents/skills/<skill>` |
| **Claude Code** | `~/.claude/skills/<skill>` | `<project>/.claude/skills/<skill>` |
| **Codex** | `~/.codex/skills/<skill>` | `<project>/.codex/skills/<skill>` |
| **Hermes Agent** | `~/.hermes/skills/<skill>` | *or add `<repo>/skills` under `skills.external_dirs` in `~/.hermes/config.yaml`* |
| **Antigravity** | `~/.gemini/config/skills/<skill>` | `<project>/.agents/skills/<skill>` |
| **Cursor** | `~/.cursor/skills/<skill>` | `<project>/.cursor/skills/<skill>` |
| **OpenCode** | `~/.agents/skills/<skill>` | `<project>/.agents/skills/<skill>` |

## Repository Structure

```text
skills/
├── website-qa-audit/
│   ├── SKILL.md
│   ├── references/
│   ├── templates/
│   └── examples/
└── ...
```

## Contributing

Issues and pull requests are welcome.

## License

MIT
