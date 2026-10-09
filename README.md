# llm-public-utils

A collection of agent skills, utility scripts, and experiments for LLM-assisted development workflows. Skills are installed with [`npx skills`](https://github.com/vercel-labs/skills) — GitHub is the registry, so a **public repo needs no clone**: there is nothing to clone, pull, or keep beside your project. The installer fetches from `Theta-Tech-AI/llm-public-utils` directly and records what it took.

## Installing skills

*Note: Run all these from your project repository directory.*

List all available skills:

```bash
npx skills add Theta-Tech-AI/llm-public-utils --list
```

Add all the skills to your project:

```bash
npx skills add Theta-Tech-AI/llm-public-utils -y --skill '*'
```

Add a specific skill to your project (e.g. the "*deslop*" skill):

```bash
npx skills add Theta-Tech-AI/llm-public-utils -y --skill deslop
```

Then restart your agent harness, and it should automatically pick up any installed skills. For instance, you should be able to run `/deslop` in Claude Code, or `$deslop` in Codex afterwards.

## Updating skills

From your project repo directory:

```bash
# Re-fetch every installed skill from the repo it came from
npx skills update -y

# …or just one of them
npx skills update deslop -y

# Show what is currently installed
npx skills list
```

No clone and no `git pull` — the installer reads `skills-lock.json` and refreshes each skill from its
recorded source, so this picks up whatever has landed upstream.

## Skills


| Skill                                                              | Description                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [linear-issues](.agents/skills/linear-issues/)                     | Linear issue lifecycle: create, start, continue, stop, close — with honest statuses and heavy commenting                                                                                                                                                            |
| [perf](.agents/skills/perf/)                                       | Measure performance before and after a change — frontend rendering, frames and FPS over the Chrome DevTools Protocol, backend timing from`perf_counter()` and timestamped logs, deploy markers, budgets and the regression ledger. Never assume a change was faster |
| [deslop](.agents/skills/deslop/)                                   | Code quality analysis and refactoring against a library of 50+ coding principles — scoped passes and whole-codebase simplification campaigns, with measurement — and the procedure for extending that library                                                      |
| [stress](.agents/skills/stress/)                                   | Stress-test apps via browser/API — confirm reliability, comb happy paths, cause mischief, hunt bugs                                                                                                                                                                 |
| [shatter](.agents/skills/shatter/)                                 | Split large files into focused, single-responsibility pieces                                                                                                                                                                                                         |
| [smelt](.agents/skills/smelt/)                                     | Separate upstream metal from project-specific overlay slag                                                                                                                                                                                                           |
| [cleanup](.agents/skills/cleanup/)                                 | Repo housekeeping — branch sync, deploy health, doc triage                                                                                                                                                                                                          |
| [local-dev](.agents/skills/local-dev/)                             | Bring up a local/hybrid dev stack for fast iteration                                                                                                                                                                                                                 |
| [reformat-academic-paper](.agents/skills/reformat-academic-paper/) | Reformat academic papers with exact text preservation                                                                                                                                                                                                                |
| [pubmed-search](.agents/skills/pubmed-search/)                     | Search PubMed and display structured paper metadata                                                                                                                                                                                                                  |
| [code-planner](.agents/skills/code-planner/)                       | Break complex tasks into actionable planning documents                                                                                                                                                                                                               |
| [critique-writing](.agents/skills/critique-writing/)               | Harsh, multi-perspective writing critique                                                                                                                                                                                                                            |
| [text-compression](.agents/skills/text-compression/)               | Iteratively compress text while preserving meaning                                                                                                                                                                                                                   |
| [gpt4-coding-style](.agents/skills/gpt4-coding-style/)             | Concise, DRY, modular Python coding preferences                                                                                                                                                                                                                      |

## Scripts

Personal machine utilities — not agent skills:

- `scripts/launch_cursor.sh` — launch Cursor IDE
- `scripts/statusline-command.sh` — Claude Code statusline snippet

## Experiments

- `experiments/improvement.md` — self-modifying documentation experiment

## License

See [LICENSE](LICENSE).
