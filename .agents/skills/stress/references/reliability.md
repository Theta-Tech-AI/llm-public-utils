# Reliability
## Philosophy
It doesn't matter if it produces shit - if it produces shit reliably and consistently, well maybe a mushroom which eats shit will come to depend on it, and perhaps even spark an intellectual revolution via its hallucinogenic properties.

You never know what value others may derive from something unexpectedly, outside of what you thought they caree about. And oftentimes, you only discover that by building something so  reliable that people are able use it repeatedly, trusting that it will "just work" and not break.

When a system is not reliable, and obscure or u expected bugs occur, people develop a general anxiety right before using it, and never get to the point where they can extract the true value from it for themselves.

Being reliable, consistently working, is what enables a sense of relief or trust in a system which makes usage sticky.

When you put the video game into the system, you never have to worry that the menu will be glitchy. You don't expect weird user behavior bugs. Those things lose the immersiveness of the game. The same applies to sofware systems.

## Deployment
To stress test a software system, you must st the bare minimum have an environment where you can test the happy path. In web apps in particular (which this skill tends to focus on), this usually entails layers of deployment, some of which may not exist, some of which may not be desired (e.g. deploying to prod), some of which may be under ci/cd such as github actions or circleci or render or similar, and some may not be listed here. But this is one pattern of deployments which should exist to enable reliability testing:

1. localhost - for rapid code iterations and local development. Easy to run unit tests here too.
2. Cloud development - this may be per dev, or perhaps a pre-staging, but there is typically some sort of no-cost-to-break cloud deployment.
3. Cloud staging- for quality assuring before prod, as closely monitoring it as possible. This may even entail sub-steps or sub-staging environments or multiple staging deployments depending on the company.
4. Production - never touch this or consider it as part of the development process unless explicitly instructe, and confirm any prod changes with the user before acting. But this does have to be reliable too. The idea and hope is that if staging is working, so is prod. But as we all know, in the real world that is rarely the case. Regardless, this should really be to verify as a final check, not for dev feedback. Any issues found exclusively on prod that didn't show up on staging should be first attempted to be reproduced on staging instead of iterating on production. This is just a final checkbox of "yes, this works just like staging." Staging is where you want to really pretend an actual user is using it.

You may need to scour the codebase for yaml files or similar to understand the deployment setup, but make sure you get the lay of the land first before making any decisions or taking any action.

Regardless, first get deployment all situated. And it might be already. Then continue with reliability testing.

## Reliability Testing
Just confirm the happy path a few times. Run something end to end, ensure it completed successfully, and then move on to more sophisticated stress tests.

There is no point in finding issues with the system unless the happy path is consistently functional.
