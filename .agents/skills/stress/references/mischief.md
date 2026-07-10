# Mischief
## What is Mischief?
To cause mischief is to act in a way that the system *does not expect*. Click things out of order, use the back button at the worst possible moment, cause chaos, and disrupt the normal flow. To make the paranoid system, which desperately hopes you always take the happy path, have to handle unexpected user behavior, is the purpose of the mischief causer.

## Rationale
It's better for the AI to try to cause mischief so we can fix it, instead of a human having to discover that bug. People act in unexpected, strange ways, and are really good at breaking systems. Mischief is a skill meant to have an AI try to break a system similarly, in order to harden it ahead of time.

## Methodologies
Knowing what the "happy path" is, via using the agent browser skill (which you should probably do a web search for and download and use if you're not already, for webapps) lets the agent drive a webapp directly through agentic tool calls. This allows the AI to act as a user would act. Because while calling API's in the wrong order or unexpected ways is definitely a viable task, nothing beats interacting with the app as a user would. In that sense, situtations like "are the buttons that are enabled the ones that are supposed to be enabled right now? What happens if I click on this one out of turn?" allow for ripe opportunities for mischief.

## How to be most mischievious?
Really challenge the expected behavior. Take a moment, look around you at the layout of the state of the app, and think of what's going to screw it up the most, which you have not tried yet. Think outside the box, and really wonder what happens if you leave something half-done, jump to another part of the app, try a different user, and then cause an async job to fail, all at once. Think of what will break and challenge the system the most. What will cause the most disruption? It's important to observe where the current state is and not just guess.

## Access to Code
Hey, guess what - you don't just have the ability to use the app and drive it via the agent browser skill or API calls, you have access to the code! Find ugly spots, find confusing workflows, and then use that to dictate how you will best break the app next.

## What to do with bugs?
If the user doesn't ask or redirect, the default behavior is to take the current repository's GitHub and file an issue, then tell the user at the end what you did with hyperlinks to that. Or maybe if they're not on GitHub they may want the mischief findings to go to a markdown or HTML file. Barring that, sometimes the user may want to direct you to auto-fix any bugs you find as you cause mischief. Use your judgment if you think that's the intention of the user given the context you have. But usually it's just cause mischief and file GitHub issues for each bug you find. Because that's the point of the mischief - to shake up the ground and let the bugs come to the surface.
