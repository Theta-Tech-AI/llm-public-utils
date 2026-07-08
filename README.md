# llm-public-utils

A collection of agent skills, utility scripts, and experiments for LLM-assisted development workflows.

## Skills

Install skills by copying or symlinking directories from `.agents/skills/` into your agent harness skills path (e.g. `~/.agents/skills/` or `.cursor/skills/`).

| Skill | Description |
|-------|-------------|
| [deslop](.agents/skills/deslop/) | Code quality analysis against coding principles |
| [shatter](.agents/skills/shatter/) | Split large files into focused, single-responsibility pieces |
| [addtodeslop](.agents/skills/addtodeslop/) | Research and merge new principles into deslop |
| [smelt](.agents/skills/smelt/) | Separate upstream metal from project-specific overlay slag |
| [cleanup](.agents/skills/cleanup/) | Repo housekeeping — branch sync, deploy health, doc triage |
| [local-dev](.agents/skills/local-dev/) | Bring up a local/hybrid dev stack for fast iteration |
| [reformat-academic-paper](.agents/skills/reformat-academic-paper/) | Reformat academic papers with exact text preservation |
| [pubmed-search](.agents/skills/pubmed-search/) | Search PubMed and display structured paper metadata |
| [code-planner](.agents/skills/code-planner/) | Break complex tasks into actionable planning documents |
| [critique-writing](.agents/skills/critique-writing/) | Harsh, multi-perspective writing critique |
| [text-compression](.agents/skills/text-compression/) | Iteratively compress text while preserving meaning |
| [gpt4-coding-style](.agents/skills/gpt4-coding-style/) | Concise, DRY, modular Python coding preferences |

Each skill directory contains a `SKILL.md` with instructions. Some include bundled assets (scripts, prompt templates).

## Scripts

Personal machine utilities — not agent skills:

- `scripts/launch_cursor.sh` — launch Cursor IDE
- `scripts/statusline-command.sh` — Claude Code statusline snippet

## Experiments

- `experiments/improvement.md` — self-modifying documentation experiment

## License

See [LICENSE](LICENSE).
