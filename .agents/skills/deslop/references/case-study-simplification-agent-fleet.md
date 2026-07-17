# Case study: simplifying an LLM writing-agent subsystem

A real deslop pass (2026-07, anonymized) on a production RAG document-authoring
product. The subsystem drafted a multi-section regulatory document with LLM
agents. It worked — and it was slop. Every finding below is an instance of a
Part I principle; the "after" column is the shipped simplification.

## The before/after table

| Slop found | Principle violated | Simplification shipped |
|---|---|---|
| Writing-voice rules lived in 3 places: an XML prompt fragment `<include>`d into one agent's prompt, a regex linter re-enforcing the same rules on output at 3 call sites, and prose duplicated in the main prompt | DRY / Single Source of Truth | Voice rules folded once into the shared agent preamble every agent inherits; fragment, includes, and all 3 linter call sites deleted |
| A regex (`\b(?:the\s+)?(?:sources?|label(?:ing)?|ifu…)\s+…(?:describ|stat|indicat…)` — 20 lines of alternations) policing *prose style* of LLM output | KISS, Decide Don't Cope | Deleted outright. Style is a prompt concern; a regex can never enumerate English. The existing semantic validators (hallucination/consistency checkers) remain the real output gate |
| One agent *run* per document section, plus a separate per-leaf wrapper for the largest section — a fleet of near-identical dispatches, each with its own lifecycle, lease, progress tracking, and frontend fan-out | Parts Plethora, Modularity done wrong | One long-running agent that authors the whole document, with tools to list sections, check completion, and jump between them — the loop moves from the orchestration layer into the agent, where it can use judgment |
| A hardcoded 30-line "proven outline" of section headings baked into the prompt | Convention Over Configuration inverted | A heading-planning tool the agent calls, whose required/suggested headings derive from the accepted example documents (data), not prompt prose |
| Paragraph "edit" was a *second implementation*: a separate one-shot LLM call with its own 40-line prompt, no tools, no citations, no provenance | DRY, Principle of Least Surprise | Edit = the same writing agent with two capabilities removed (write other sections, change headings). A subset, not a sibling |

## The transferable lessons

1. **An instruction enforced twice is a contradiction waiting to happen.** The
   prompt said "write in the manufacturer's voice"; the regex tried to *verify*
   voice mechanically and rejected legitimate prose the prompt allowed. When an
   LLM instruction and a mechanical check encode the same *stylistic* rule, keep
   the instruction, delete the check, and gate on *semantic* validators instead.
2. **N near-identical agent dispatches are the multi-agent version of copy-paste.**
   If the only difference between runs is a parameter (here: section name), you
   don't have N agents — you have one agent and a `for` loop that belongs
   *inside* it, where the model can reorder, revisit, and share context.
3. **A "different" agent that is really a permissions subset should be built as
   a subset.** The edit flow needed the full toolset minus two capabilities;
   implementing it as a separate prompt+call meant every improvement to the main
   agent silently missed the editor.
4. **Prompts are code — deslop them too.** Duplicated guardrails across a shared
   preamble and per-agent prompts, historical narration, and hardcoded data
   (outlines) in prompt prose are the same slop as in source files, and respond
   to the same principles.
