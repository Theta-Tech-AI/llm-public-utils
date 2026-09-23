# llm-public-utils

A collection of agent skills, utility scripts, and experiments for LLM-assisted development workflows.

Skills are installed with [`npx skills`](https://github.com/vercel-labs/skills) — GitHub is the registry,
so a **public repo needs no clone**: there is nothing to clone, pull, or keep beside your project. The
installer fetches from `Theta-Tech-AI/llm-public-utils` directly and records what it took.

## Prerequisites

- **Node.js 22.20+** (for `npx`)
- At least one supported agent harness — Claude Code, Codex, Cursor, OpenCode, and others

## Install a skill into a project

From your project directory, add one skill at a time. For example, to install the `linear-issues` skill:

```bash
cd my_project_repo/

npx skills add Theta-Tech-AI/llm-public-utils --skill linear-issues \
    -y \
    -a cursor \
    -a claude-code \
    -a codex
```

Substitute `linear-issues` for any skill in the table below (e.g. `--skill deslop`, `--skill stress`).
Repeat the flag to install several at once (`--skill deslop --skill stress`), or use `--skill '*'` for
every skill in the repo. Add `-g` to install at user level instead of into the current project, and
`--copy` if you want real files rather than symlinks into the agent directories.

To see what the repo offers without installing anything:

```bash
npx skills add Theta-Tech-AI/llm-public-utils --list
```

### What lands in your project

When one of the agents you name reads the shared `.agents/skills/` location — Cursor and Codex do, and
Claude Code is given a link into it — the install looks like this:

```
<project>/.agents/skills/<skill>/      # the skill itself: SKILL.md + references/
<project>/skills-lock.json             # one entry per skill: source + computedHash
<project>/.claude/skills/<skill>       # a symlink into the shared store, per agent you named
```

Name only a single agent that keeps its own private directory — Claude Code on its own — and there is no
shared store to link into, so the skill is **copied** into that agent's directory instead. `--copy` forces
that behaviour for any agent, and `-g` moves the whole thing to user level rather than the project.

`skills-lock.json` is what pins the install — `"source": "Theta-Tech-AI/llm-public-utils"` plus the
`computedHash` of the skill as it was fetched. Commit it alongside your code, and
`npx skills experimental_install` restores the same set on another machine.

## Update skills later

```bash
cd my_project_repo/

# Re-fetch every installed skill from the repo it came from
npx skills update -y

# Show what is currently installed
npx skills list
```

No clone and no `git pull` — the installer reads `skills-lock.json` and refreshes each skill from its
recorded source, so this picks up whatever has landed upstream.

## Working on a skill in this repo

Contributing is the one case that needs a clone:

```bash
git clone https://github.com/Theta-Tech-AI/llm-public-utils.git
cd my_project_repo/

# Install from your local checkout instead of GitHub
npx skills add ../llm-public-utils --skill deslop -y -a cursor -a claude-code -a codex
```

Two differences are worth knowing when installing from a path rather than from GitHub:

- the CLI **copies** the skill into your agent's directory instead of keeping `.agents/skills/` and
  symlinking — so **re-run the command after each edit** to pick the change up;
- the `skills-lock.json` entry records the path you passed (`"sourceType": "local"`), which is fine
  locally but is not something to commit. Once your change is merged upstream, re-run the same command
  against `Theta-Tech-AI/llm-public-utils` to pin the project back to the published copy.

## Running

In Claude Code:

```bash
cd my_project_repo/
claude
```

Then from within Claude Code:

```
> /linear-issues
```

In Codex:

```bash
cd my_project_repo/
codex
```

Then from within Codex:

```
> $linear-issues
```

Or from OpenCode:

```bash
cd my_project_repo/
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
| [deslop](.agents/skills/deslop/) | Code quality analysis and refactoring against a library of 50+ coding principles — scoped passes and whole-codebase simplification campaigns, with measurement — and the procedure for extending that library |
| [stress](.agents/skills/stress/) | Stress-test apps via browser/API — confirm reliability, comb happy paths, cause mischief, hunt bugs |
| [shatter](.agents/skills/shatter/) | Split large files into focused, single-responsibility pieces |
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
