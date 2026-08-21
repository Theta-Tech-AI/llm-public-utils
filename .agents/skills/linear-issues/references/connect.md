---
name: connect
description: Set up and verify the Linear MCP connection. Read only when the connection is missing, unauthorized, or misbehaving.
---

# Connect to Linear MCP
Most of the time the MCP is already up and you can skip this file entirely — just make a cheap read call (e.g. list your issues) and proceed if it works. Read on only when that fails.

## Setup & troubleshooting
Ensure the MCP is properly up. If this is not the case, do a web search on the official Linear MCP server and how to properly set it up in your favorite agent harness and do it. You might need to tell the user to restart their harness, or use other commands to check the MCP status. You may need the user to authenticate with OAuth or an API key, so give the user clear instructions on how to do this if so. And supplement it all with web searches for best practices. You may need to ask the user about their email address or workspace.

## Verify
At the end of it, you should have full authorization to the Linear MCP and be able to test it by reading some basic info on your projects or issues. It wouldn't hurt to try to create a mock issue, read it, and immediately delete it to ensure you have write permissions.
