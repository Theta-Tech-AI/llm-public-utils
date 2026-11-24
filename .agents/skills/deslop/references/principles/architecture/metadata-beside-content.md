---
name: deslop-architecture-metadata-beside-content
description: Deslop principle — Metadata Beside Content: what is true about content travels beside it, typed; never inside it as text.
---

# Metadata Beside Content, Never Inside It

**Why this is slop:** metadata written inside the content forces every reader to find and parse it again, so one field ends up with as many parsers as there are readers and they disagree.

> In-band signalling let the network's control tones travel in the same channel as the caller's voice, so anyone who could whistle 2600 Hz could seize a trunk line. The fix was to move signalling out of band.
> — the history of telephone signalling, paraphrased

## Core Concept

**Content** is what a reader is meant to read: the prose of a document, the value of a field, the message to a person. **Metadata** is what is true *about* the content: where it came from, whether it is confirmed, whether a source supports it, whether it could be produced at all, how confident anyone is, what still has to happen to it. The two change for different reasons and are owned by different parts of a system: the writer owns the content; validators, reviewers and the workflow own what is true about it.

When metadata is written **into** the content (a marker in the text, a status sentence, a sentinel string, a note appended to a free-text field), every reader of the content must find it, parse it and decide what to do with it, and each reader decides on its own. Some strip it, some keep it, some count it as words, some miss it. Sooner or later one reader prints it where it does not belong, or deletes it and leaves the content broken. The fix is never a better parser: it is a second channel. The content is only content; the metadata is a typed field, an annotation or a state beside it, read by name.

## How metadata gets into content

- **Inline markers.** Citations, template marks or "needs a source" tokens written into generated text: a dozen renderers then each strip or keep them by their own rule, and one cuts a sentence in half.
- **Status sentences.** A generator is told to say "this part has not yet been confirmed" in the text; the status changes, the sentence does not, and it ships after approval.
- **A notice as the content.** "This section could not be produced", stored as the section's text with a sentinel string so a screen can find it again; checks then read the notice as finished text.
- **Notes appended to a prose field.** A validator appends "the quote could not be verified" to a rationale or a comment; the note is exported as if the author wrote it.
- **Fillers for absence.** "Not specified", "N/A", "TBD" written where a value is missing, instead of modelling absence ([No Silent Defaults](../reliability/no-silent-defaults.md)).
- **Meaning in names and messages.** A status in a file name, a role in an id prefix, an error kind recovered by matching words in an exception message ([Errors at the Boundary](../reliability/errors-at-the-boundary.md)).

The tell in code is a **reader that searches text for meaning**: a regex for a marker, a check for a sentinel prefix, a substring test on a status word, a split on a delimiter that only the writer was supposed to use.

```python
# ❌ Metadata in the content: every reader re-parses it, and each decides alone.
section.text = "The device is sterile.【src:42】 Shelf life is 3 years.【unsourced: no stability report】"
fda_copy  = re.sub(r"【[^】]*】", "", section.text)           # also deletes the unsourced signal
ready     = "【unsourced" not in section.text                 # a second reader, a second rule

# ✅ Content and metadata in two channels; readers ask by name.
@dataclass(frozen=True)
class Claim:
    span: tuple[int, int]
    sources: tuple[str, ...] = ()
    needs_source: str | None = None                           # the reason, or None

@dataclass(frozen=True)
class SectionVersion:
    text: str                                                 # prose only
    claims: tuple[Claim, ...]

fda_copy = version.text                                       # nothing to strip
ready    = not any(c.needs_source is not None for c in version.claims)
```

## Finding and fixing it

1. **List what the text is asked to carry.** For each generator prompt, template and writer, mark every instruction or code path that puts something other than reader-facing content into the text: status, provenance, availability, confidence, to-dos, markers, notes.
2. **List what is read out of text.** Every regex, sentinel test and substring check that recovers meaning from content is the other end of the same channel.
3. **Give each piece of metadata its typed home:** a field of the generator's structured output, an annotation over a span of the content, a state of the record, or a finding of a validator. Readers read that home; screens and documents render it explicitly where it belongs, and nowhere else.
4. **Read old records through one legacy reader.** Stored content that already carries metadata is not rewritten (its history and signatures may depend on it); one reader converts it on the way in, and nothing else parses it.
5. **Keep the generator honest:** the prompt stops asking for metadata in the text, and the output schema has the fields instead. A model asked for a typed field fills it; a model asked to write "not stated" writes it into a document.

## When text is the right channel

Metadata *for the reader* that the content itself is about stays in the content: a footnote a human author chose, "Not applicable to this device" when that statement is the content an expert decided to say, a citation in a format the destination requires. The test: **would the author of the content write this sentence, for this reader, if no system existed?** If the sentence exists only because a system needed to remember something, it belongs beside the content.

In relation to other principles:

| Principle | Relationship |
|-----------|--------------|
| [**Parse, Don't Validate**](parse-dont-validate.md) | Metadata in text forces every reader to re-parse; a typed channel is parsed once, at the writer. |
| [**Make Illegal States Unrepresentable**](illegal-states-unrepresentable.md) | Prose that cannot hold metadata cannot leak it into an output. |
| [**Separation of Concerns**](separation-of-concerns.md) | What the content says and what is true about it change for different reasons and have different owners. |
| [**Single Source of Truth**](single-source-of-truth.md) | A status written into text is a second, frozen copy of a fact the workflow owns. |
| [**No Silent Defaults**](../reliability/no-silent-defaults.md) | Fillers for absence ("not specified") are metadata about a missing value disguised as a value. |
| [**Grammar Without an Owner**](../../patterns/grammar-without-owner.md) (pattern) | One parser fixes a format that must be text. When the format is metadata inside content, move it out instead; then no reader needs a parser at all. |
| [**Liveness: Every State Has an Owner**](../reliability/liveness.md) | "Could not be produced" is a state with an owner, not a sentence in the output. |

## Summary

1. **Content is what the reader reads; metadata is what is true about it.** They change for different reasons and have different owners.
2. **Metadata written into content is re-parsed by every reader,** each by its own rule, until one prints or deletes it wrongly.
3. **The fix is a second channel, not a better parser:** typed fields, annotations over spans, record states, validator findings.
4. **Old content is read through one legacy reader;** nothing else searches text for meaning.
5. **The test:** would the author write this sentence for this reader if no system existed? If not, it belongs beside the content.
