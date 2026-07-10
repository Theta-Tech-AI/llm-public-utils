# Mischief
## What is Mischief?
To cause mischief is to act in a way that the system *does not expect*. Click things out of order, use the back button at the worst possible moment, cause chaos, and disrupt the normal flow. To make the paranoid system, which desperately hopes you always take the happy path, have to handle unexpected user behavior, is the purpose of the mischief causer.

## Rationale
It's better for the AI to try to cause mischief so we can fix it, instead of a human having to discover that bug. People act in unexpected, strange ways, and are really good at breaking systems. Mischief is a skill meant to have an AI try to break a system similarly, in order to harden it ahead of time.

## Methodologies
Knowing what the "happy path" is, via using the agent browser skill (which you should probably do a web search for and download and use if you're not already, for webapps) lets the agent drive a webapp directly through agentic tool calls. This allows the AI to act as a user would act. Because while calling API's in the wrong order or unexpected ways is definitely a viable task, nothing beats interacting with the app as a user would. In that sense, situtations like "are the buttons that are enabled the ones that are supposed to be enabled right now? What happens if I click on this one out of turn?" allow for ripe opportunities for mischief.


