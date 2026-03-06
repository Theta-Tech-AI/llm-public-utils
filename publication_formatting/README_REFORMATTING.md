# Academic Document Reformatting System

## Overview

This system enables reformatting of academic papers while preserving exact text and citations. It uses Claude Code's native tools to create and execute a Python script that applies template styling and extracts figures.

## Quick Navigation

Choose the guide that fits your needs:

### 1. QUICK_START.md
**→ Start here if you just want to get it done**
- 3-step process (convert template, run prompt, get files)
- Minimal explanation
- Takes 15-45 minutes total

### 2. PROMPT_TEMPLATE.txt
**→ Copy-paste ready prompt**
- The exact prompt to give Claude Code
- No explanations, just the instructions
- Use this after converting the template

### 3. REFORMAT_PAPER_PROMPT.md
**→ Complete technical documentation**
- Full prompt with code examples
- Detailed implementation guidance
- Troubleshooting section
- Customization instructions

### 4. paper_formatting_plan.md
**→ Original planning document**
- How the system was designed
- Technical decisions and rationale
- Feasibility assessment
- Implementation phases

## What This System Does

### Inputs
- Your academic paper (.docx)
- A journal template (.dotx)

### Outputs
- Reformatted paper with template styling applied
- ZIP file with figures renamed (figure_1.png, figure_2.png, etc.)
- Validation report confirming no text was changed

### Key Features
- **Preserves text exactly** - No words are changed
- **Preserves citations** - Citation numbers stay the same
- **Applies template formatting** - Headers, footers, fonts, page setup from template
- **Adds page numbers** - Dynamic "Page X of Y" in footer
- **Numbers sections** - Automatic hierarchical numbering (1, 1.1, 1.1.1)
- **Extracts figures** - Renames images by figure number
- **Validates output** - Confirms nothing was accidentally modified

## How It Works

1. You provide a detailed prompt to Claude Code
2. Claude writes a Python script using python-docx
3. The script:
   - Reads your paper and extracts all content
   - Identifies figures and their numbers
   - Extracts and renames images
   - Applies template styles without changing text
   - Creates the reformatted document
   - Validates that text matches exactly
4. You receive three output files ready to use

## Requirements

### One-Time Setup
- Convert `cancers-template.dot` to `.dotx` format (2 minutes)
  - Use Microsoft Word or LibreOffice
  - File → Save As → Word Template (.dotx)

### Each Use
- Claude Code installed and running
- Source document (.docx)
- Template document (.dotx)
- 10-30 minutes for Claude to write and run the script

### Installation Required
- python-docx must be installed (one-time setup):
  ```bash
  python -m pip install python-docx
  ```
  **Note:** This requires an internet connection
- All other libraries are Python standard library (no installation needed)

## Files in This System

| File | Purpose |
|------|---------|
| `QUICK_START.md` | Get started fast with minimal reading |
| `PROMPT_TEMPLATE.txt` | Copy-paste prompt without explanations |
| `REFORMAT_PAPER_PROMPT.md` | Full documentation with code examples |
| `README_REFORMATTING.md` | This file - navigation and overview |
| `paper_formatting_plan.md` | Original design document |

## Typical Workflow

```
┌─────────────────────────────────────┐
│  Convert template to .dotx          │
│  (One-time, 2 minutes)              │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Copy prompt from PROMPT_TEMPLATE   │
│  Paste into Claude Code             │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Claude writes Python script        │
│  Claude executes script             │
│  (10-30 minutes)                    │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Receive 3 output files:            │
│  - reformatted_document.docx        │
│  - figures.zip                      │
│  - validation_report.txt            │
└─────────────────────────────────────┘
```

## What Makes This Different

### Traditional Approach
- Manual copy-paste between documents
- Manual style application
- Manual figure extraction and renaming
- Risk of changing text accidentally
- Time-consuming and error-prone

### This System
- Fully automated process
- Guarantees text preservation
- Validates output automatically
- Extracts and renames figures automatically
- Reproducible and reliable

## Success Criteria

After running the system, check your `validation_report.txt`:

✓ **Word count matches** - No words added or removed
✓ **Citation count matches** - All citations preserved
✓ **Overall status: PASSED** - Safe to use the output

If any check fails, the report will show you exactly what differed.

## Customization

This system can be adapted for:
- Different journal templates (update file paths and style names)
- Different citation formats (modify regex patterns)
- Different figure caption formats (adjust parsing logic)
- Multiple papers in batch (add loop in script)

See `REFORMAT_PAPER_PROMPT.md` for customization details.

## Advantages of This Approach

### No Permanent Installation
- No custom skills to maintain
- No version control needed
- No dependency conflicts
- Works in any Claude Code environment

### Transparent Process
- You see all the code Claude writes
- You can modify the script if needed
- You can save and reuse the script
- Easy to debug if something goes wrong

### Reproducible
- Same prompt produces same results
- Can be run multiple times
- Can be shared with colleagues
- Version control friendly

## Troubleshooting

See the troubleshooting section in `REFORMAT_PAPER_PROMPT.md` for solutions to common issues:
- Template style not found
- Figure numbers not extracted correctly
- Validation failures
- Citation format issues

## Technical Details

### Core Technology
- **python-docx**: Document manipulation
- **zipfile**: Image extraction from .docx ZIP structure
- **regex**: Pattern matching for citations and figures

### Processing Steps
1. Parse source document XML structure
2. Extract figure numbers from SEQ fields or captions
3. Map images to figure numbers
4. Create new document from template
5. Apply styles while preserving text
6. Extract and rename images
7. Validate output

### Validation Logic
- Compare word counts using `split()`
- Extract citations using regex patterns
- Compare lists for exact match
- Report any discrepancies

## Support

If you encounter issues:

1. Check `QUICK_START.md` for common solutions
2. Review `REFORMAT_PAPER_PROMPT.md` troubleshooting section
3. Examine the generated Python script for errors
4. Run the script again with modifications if needed

## Future Enhancements

Possible improvements to this system:
- Support for more citation formats (footnotes, endnotes)
- Batch processing of multiple papers
- Custom style mapping configurations
- Enhanced figure caption parsing
- Support for equations and special characters
- Integration with reference managers (Zotero, Mendeley)

## License and Usage

This system is provided as-is for academic use. Feel free to modify and adapt for your needs.

## Credits

Designed for HaloDx clinical research documentation project.
Built using Claude Code native tools and python-docx library.
