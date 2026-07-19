# llm-public-utils

A collection of agent skills, utility scripts, and experiments for LLM-assisted development workflows.

## Skills

Install skills by using the skills package:

```bash
# go into a project
cd my_code_dir/my_project_repo/

# install a skill, e.g. /deslop
npx skills add Theta-Tech-AI/llm-public-utils --skill deslop -y -a cursor -a claude-code -a codex

# or install the /stress skill
npx skills add Theta-Tech-AI/llm-public-utils --skill stress -y -a cursor -a claude-code -a codex
```

Then you can update the skill later:

```bash
# go into a project
cd my_code_dir/my_project_repo/

# update installed skills
npx skills update -y
```


Alternatively, you can copy or symlinking directories from `.agents/skills/` into your agent harness skills path (e.g. `~/.agents/skills/` or `.cursor/skills/`).

| Skill | Description |
|-------|-------------|
| [deslop](.agents/skills/deslop/) | Code quality analysis and refactoring against a library of coding principles |
| [stress](.agents/skills/stress/) | Stress-test apps via browser/API — confirm reliability, comb happy paths, cause mischief, hunt bugs |
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
