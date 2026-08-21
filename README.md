# llm-public-utils

A collection of agent skills, utility scripts, and experiments for LLM-assisted development workflows.

## Installation

Clone the skills repository (only once):

```bash
cd my_code_dir/
git clone https://github.com/Theta-Tech-AI/llm-public-utils.git
```

## Install a skill into a project

From your project directory, add one skill at a time. For example, to install the `linear-issues` skill:

```bash
# Go to your project
cd my_code_dir/my_project_repo/

# Add a skill from your local clone
npx skills add ../llm-public-utils --skill linear-issues \
    -y \
    -a cursor \
    -a claude-code \
    -a codex
```

Substitute `linear-issues` for any skill in the table below (e.g. `--skill deslop`, `--skill stress`).

Alternatively, you can copy or symlink directories from `.agents/skills/` into your agent harness skills path (e.g. `~/.agents/skills/` or `.cursor/skills/`).

## Update skills later

```bash
cd my_code_dir/my_project_repo/

# Pull the latest skills
git -C ../llm-public-utils pull

# Reinstall/update them in this project
npx skills update -y
```

## Running

In Claude Code:

```bash
cd my_code_dir/my_project_repo/
claude
```

Then from within Claude Code:

```
> /linear-issues
```

In Codex:

```bash
cd my_code_dir/my_project_repo/
codex
```

Then from within Codex:

```
> $linear-issues
```

Or from OpenCode:

```bash
cd my_code_dir/my_project_repo/
opencode
```

Then from within OpenCode:

```
> Run the linear-issues skill from the .agents/skills folder.
```

Each skill directory contains a `SKILL.md` with instructions. Some include bundled assets (scripts, prompt templates).

## Skills

| Skill | Description |
|-------|-------------|
| [linear-issues](.agents/skills/linear-issues/) | Linear issue lifecycle: create, start, continue, stop, close — with honest statuses and heavy commenting |
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

## Scripts

Personal machine utilities — not agent skills:

- `scripts/launch_cursor.sh` — launch Cursor IDE
- `scripts/statusline-command.sh` — Claude Code statusline snippet

## Experiments

- `experiments/improvement.md` — self-modifying documentation experiment

## License

See [LICENSE](LICENSE).