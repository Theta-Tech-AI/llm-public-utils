---
name: comb
description: Repeatedly move through the "happy path" of an app and find small subtle, like combing your hair and finding little knots.
---

# Comb
## Overview
To comb through the code base is to go through the happy path over and over again, with slight deviations, finding subtle little knots as you comb through the hair until it's silky smooth.

## Combing Metaphor
You start with a wide-toothed comb, gently combing through the hair on the happy easy path. Just gently go through the hair, ignore some knots, and just smooth the basic over. In our case, this means go through the happy path of the app. Just use it as expected. Don't try to break it or anything.

Then do it again. Do another combing pass with the wide-toothed comb - try another happy path, try the same happy path again with another state. Make sure the wide toothed comb can go through the entire app as expected over and over again.

Then, swap out your wide-toothed comb with a slightly narrower comb, which can find large obvious knots and tease them out, and comb through them. The hair becomes a bit smoother, a bit silkier. Go through the hair gently (every step is gentle here!) over and over again. THe hair becomes a bit smoother, a bit silkier.

Then gradually decrease the width of the comb, teasing out subtler and subtler bugs. Gradually move off the happy path into less expected paths, combing out knots along the way.

But the end, you can run a super fine-toothed comb through the hair and it just flows with nearly no friction. That's where we want to be with the app.

## Tools
The "agent browser" skill is crucial here for webapps! This allows the agent to actually drive the app in a fully deployed state. It actually clicks the buttons instead of just driving it through the API. Now, also use the API and drive the app in expected and unexpected ways. It's faster. But really it's not the only tool in your toolchest, nor the best. The closest you can get to an actual user experience, the better.

## What to do with Knots?
The option is to either fix the knot now, or file a GitHub issue for it. The default should be to file a GitHub issue for each knot and then tell the user what you filed with a full hyperlink. But sometimes, the user may want to just auto-fix the issues as you find them, so you can ask a clarifying question to the user if the instructions are unclear. TLDR: File github issues by default, or fix knots on the fly if the user wants.
