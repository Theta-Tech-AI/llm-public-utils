Read the following references:
- comb.md - How to go through the happy path with the app and try to find subtle "knots".
- mischief.md - Cause as much trouble as you can with the app to find and file issues.
- bug-hunter.md - Hunt for bugs in the code.

All these talk about documenting the issues via GitHub issues or markdown or html artifact files when done. The user can choose to auto-fix some issues in addition to, or instead of, filing them. But the default is just to file issues if there's a GitHub and you have permission to file issues (do a smoke test by filing an issue then deleting it).

But these 3 files (mischief, combing, and bug-hunter) form the core of stress testing apps, particularly webapps. We should probably add a load.md file at some point for stress testing scale, but for now this stress testing skill is about stress testing the app's functionality.

The agent is instruction to read these files, make sure you can get set up with testing the app (authentication might be in environment variables, other markdown files, or maybe there's instructions to bypass it or use a local setup), and then start using it and deciding if you want to cause mischief, comb through the happy path, hunt for bugs, or maybe do all 3!

Your decisions.

Your job is to stress the system to unearth and eventually fix bugs before the user has to experience them.
