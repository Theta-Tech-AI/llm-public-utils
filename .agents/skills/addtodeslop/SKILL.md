---
name: addtodeslop
description: Research a new coding principle and merge it into the deslop skill reference. Use when extending the deslop principles library with a missing, battle-tested software engineering concept.
---

# Add to Deslop

You are a coding principles researcher and technical writer. Your task is to identify an important coding principle that is missing from the deslop command and create a comprehensive, well-researched section for it, then merge it into the existing deslop.md file.

## Target Principle

If provided: $ARGUMENTS

If no argument provided, you will determine the best next principle to add.

If an argument is provided, that's the coding principles to add to deslop.

## Deslop

There should be a deslop skill at either `~/.agents/skills/deslop/SKILL.md` or in this repository at `.agents/skills/deslop/SKILL.md`.

This contains a set of coding principles to use to analyze the code, and the goal of this skill is to extend that file.

At the end of running this skill, deslop will have a new coding principle added to it.

## Process

### Phase 1: Discovery

1. **Read the existing deslop skill** - Find and then use the Read tool to examine `.agents/skills/deslop/SKILL.md` (or `~/.agents/skills/deslop/SKILL.md`). Build a complete list of principles that are already documented. This is critical to avoid duplicating existing content.

2. **Identify the gap** - If no principle was specified, perform a web search for "most important software engineering coding principles" to discover well-established principles. Compare the search results against your list of already-documented principles to find gaps.

3. **Select the next principle** - Choose the most impactful principle that:
   - Is widely recognized and battle-tested
   - Is NOT already covered in deslop (verify against your list!)
   - Complements the existing collection
   - Has practical, actionable guidance

4. **Announce your choice** - Tell the user which principle you've selected and why, including what principles already exist that you're avoiding.

### Phase 2: Initial Research

5. **Deep dive web search** - Search for "[principle name] software engineering best practices examples" to gather:
   - Formal definitions
   - Historical context and origin
   - Key benefits and trade-offs
   - Common violations and anti-patterns
   - Language-specific implementations (prefer Python)
   - Real-world examples

### Phase 3: Initial Draft

6. **Create a temp file** - Write to `/tmp/new_principle.md` following this structure (matching the style of existing sections in deslop.md):

```markdown
## [Principle Name]

> [A memorable one-liner definition or quote]
> — [Attribution]

### Core Concept

[1-2 paragraphs explaining what the principle is, why it matters, and when it applies]

### [Key Concept 1] (if needed)

[Explanation with examples]

### [Key Concept 2] (if needed)

[Explanation with examples]

### Common Violations

[Brief description of anti-patterns]

```python
# ❌ Wrong - [description]
[code example]

# ✅ Correct - [description]
[code example]
```

### Summary

1. **[Point 1]** — [brief explanation]
2. **[Point 2]** — [brief explanation]
3. **[Point 3]** — [brief explanation]
4. **[Point 4]** — [brief explanation]

**Important style notes:**
- Keep sections concise like existing deslop.md entries (not full standalone docs)
- Use the same formatting: `### ` for subsections, code blocks with `# ❌ Wrong` / `# ✅ Correct`
- Include a defining quote with attribution
- End with a numbered summary list
- Aim for similar length to existing principle sections (~50-150 lines)

### Phase 4: Iterative Refinement (3 Cycles)

For each of the 3 refinement cycles:

7. **Read the current temp file** - Use the Read tool to review `/tmp/new_principle.md`.

8. **Research to flesh out** - Web search for specific aspects that need more depth:
   - Cycle 1: Search for "[principle] real world examples case studies"
   - Cycle 2: Search for "[principle] common mistakes pitfalls"
   - Cycle 3: Search for "[principle] vs [related principle] when to use"

9. **Expand** - Add new subsections, examples, depth, and nuance based on research.

10. **Compact** - Remove redundancy, tighten prose, ensure every sentence adds value. Match the concise style of existing deslop.md sections.

Steps 9 and 10 are important: actually expand then compact. Repeated cycles increase information density.

This is where the real magic happens.

### Phase 5: Merge into Deslop

11. **Determine placement** - Read deslop.md and identify which category the new principle belongs to:
   - Core Principles
   - Object-Oriented Design
   - Data & State Management
   - Architecture & Design
   - Reliability & Operations
   - User Experience

   Or create a new category if none fit.

12. **Update the Table of Contents** - Add the new principle to the appropriate section in the ToC with an anchor link.

13. **Insert the principle** - Add the content from `/tmp/new_principle.md` into the appropriate location in deslop.md, maintaining the existing structure and formatting.

14. **Verify the merge** - Read the updated deslop.md to ensure:
   - ToC entry links correctly
   - Formatting is consistent
   - No duplicate principles
   - Section flows naturally with neighbors

### Phase 6: Cleanup and Report

15. **Delete temp file** - Remove `/tmp/new_principle.md`

16. **Report completion** - Tell the user:
    - The principle that was added
    - Which category it was placed in
    - A brief summary of what the new section covers
    - The principles it relates to in the existing collection

## Quality Standards

- **Match existing style** - The new section should be indistinguishable from existing ones
- **Concise over comprehensive** - This is a reference, not a textbook
- **Practical over theoretical** - Include real code examples in Python
- **Balanced** - Cover both when to apply AND when not to apply
- **Actionable** - Provide clear guidance
- **Connected** - Reference related principles already in deslop.md
