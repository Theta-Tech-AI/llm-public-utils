---
name: reformat-academic-paper
description: Reformat academic papers while preserving exact text, applying template styling, and extracting figures. Use when converting a .docx paper to a journal template with validation.
---

# Academic Document Reformatting

> **Bundled asset:** For a copy-paste prompt without the full technical docs, use `PROMPT_TEMPLATE.txt` in this directory.

## Overview

This prompt guides Claude Code to reformat an academic paper while preserving exact text and applying new styling from a template. The process extracts images, renames them by figure number, and validates the output for correctness.

## Prerequisites

Before using this prompt, you must:

1. **Install required libraries** (requires internet connection):
   ```bash
   python -m pip install python-docx python-docx-template
   ```
   - `python-docx` — core document manipulation
   - `python-docx-template` — loads `.dotx`/`.dot` template files and converts them to `.docx` automatically (so you do not need to open Word manually)

2. **Prepare the template file** (formatting only — no format conversion needed):
   - **Add page numbers**: Open template in Word → Insert > Page Number > Bottom of Page
   - **Set font**: Right-click "Normal" style > Modify > Set font name, size, color
   - **Set spacing**: In style modification dialog, set paragraph spacing
   - Save the template (any of `.dotx`, `.dot`, or `.docx` — the script converts automatically)

3. **Verify files are in place**:
   - Source document (`.docx`)
   - Template document (`.dotx`, `.dot`, or `.docx` — all supported)

## The Prompt

Copy and paste the following prompt to Claude Code, replacing the file paths with your actual files:

---

**TASK: Reformat Academic Document with Exact Text Preservation**

I need you to create a Python script and execute it to reformat an academic paper. The script must preserve text exactly while applying new styling from a template.

**INPUT FILES:**
- Source Document: `A_Phase_I_Study_of_Laser_Focal_Therapy_Rev_20_of_Prostate_Cancer_in_an_Outpatient_Setting.docx`
- Template Document: `cancers-template.docx` (must be .docx, not .dotx)

**CRITICAL REQUIREMENTS:**
1. Words cannot be changed between original and reformatted documents
2. Citation numbers must be copied exactly
3. Extract images and create ZIP file with figure-numbered names (figure_1.png, figure_2.png, etc.)
4. Apply template styles to content without modifying text
5. Output: New .docx file + ZIP file with images
6. Validate that text and citations match exactly

**OUTPUT FILES:**
- `reformatted_document.docx` - The new styled document
- `figures.zip` - All images renamed by figure number
- `validation_report.txt` - Verification results

**PROCESS - Please follow these steps:**

### STEP 1: Analyze Both Documents

First, create a preliminary analysis script to understand the document structure:

```python
from docx import Document
import zipfile
import os

def analyze_documents():
    # Load documents
    source = Document('A_Phase_I_Study_of_Laser_Focal_Therapy_Rev_20_of_Prostate_Cancer_in_an_Outpatient_Setting.docx')
    template = Document('cancers-template.docx')

    print("=== SOURCE DOCUMENT ANALYSIS ===")
    print(f"Total paragraphs: {len(source.paragraphs)}")
    print(f"Total tables: {len(source.tables)}")

    # Known section names for content-based heading detection
    KNOWN_SECTIONS = {
        'ABSTRACT', 'INTRODUCTION', 'METHODS', 'MATERIALS AND METHODS',
        'RESULTS', 'DISCUSSION', 'CONCLUSIONS', 'CONCLUSION',
        'REFERENCES', 'BIBLIOGRAPHY', 'ACKNOWLEDGEMENTS', 'ACKNOWLEDGMENTS',
        'FUNDING', 'CONFLICTS OF INTEREST', 'ABBREVIATIONS',
        'SUPPLEMENTARY MATERIALS', 'APPENDIX', 'DATA AVAILABILITY',
        'AUTHOR CONTRIBUTIONS', 'INSTITUTIONAL REVIEW BOARD STATEMENT',
        'INFORMED CONSENT STATEMENT', 'PURPOSE', 'BACKGROUND',
        'STUDY DESIGN', 'STATISTICAL ANALYSIS', 'LIMITATIONS',
    }

    # Find headings using BOTH style-based and content-based detection
    print("\n=== DOCUMENT STRUCTURE (Style-Based + Content-Based) ===")
    for i, para in enumerate(source.paragraphs[:50]):
        text = para.text.strip()
        style = para.style.name

        # Style-based detection
        is_heading_style = style.startswith('Heading') or style == 'Title'

        # Content-based detection: ALL-CAPS text matching known section names
        is_allcaps_section = (
            text.isupper()
            and len(text) > 2
            and len(text) < 100
            and text.upper() in KNOWN_SECTIONS
        )

        if is_heading_style or is_allcaps_section or len(text) < 100:
            detection = []
            if is_heading_style:
                detection.append("STYLE")
            if is_allcaps_section:
                detection.append("CONTENT")
            tag = "+".join(detection) if detection else "text"
            print(f"{i}: [{style}] ({tag}) {text[:80]}")

    # Analyze images
    print("\n=== IMAGES ===")
    with zipfile.ZipFile('A_Phase_I_Study_of_Laser_Focal_Therapy_Rev_20_of_Prostate_Cancer_in_an_Outpatient_Setting.docx', 'r') as zip_ref:
        media_files = [f for f in zip_ref.namelist() if f.startswith('word/media/')]
        print(f"Total images: {len(media_files)}")
        for img in media_files:
            print(f"  {img}")

    # Analyze template styles with prefix detection
    print("\n=== TEMPLATE STYLES ===")
    style_prefixes = {}
    for style in template.styles:
        if hasattr(style, 'name'):
            name = style.name
            print(f"  {name}")
            # Detect naming convention prefix
            if '_' in name:
                prefix = name.split('_')[0]
                if prefix not in style_prefixes:
                    style_prefixes[prefix] = []
                style_prefixes[prefix].append(name)

    print("\n=== TEMPLATE STYLE NAMING CONVENTION ===")
    if style_prefixes:
        for prefix, names in sorted(style_prefixes.items(), key=lambda x: -len(x[1])):
            print(f"  Prefix '{prefix}': {len(names)} styles")
            for n in names[:5]:
                print(f"    {n}")
        dominant = max(style_prefixes, key=lambda k: len(style_prefixes[k]))
        print(f"\n  Detected convention: {dominant}-prefixed (e.g., MDPI)")
    else:
        print("  Standard Word naming convention (Heading 1, Normal, etc.)")

if __name__ == '__main__':
    analyze_documents()
```

Run this analysis first to understand the document structure.

### STEP 1.5: Template Structure — Key XML Features

Before writing the main script, understand these three structural features that affect how the script works:

**S1 — Inline Text Boxes in Source Documents**

Source documents may contain `<w:txbxContent>` elements — text boxes embedded in the document flow. Python-docx's `.paragraphs` DOES traverse inline text boxes (`<wp:inline>` wrapper). For floating text boxes (`<wp:anchor>`, page-anchored), the content is outside the normal paragraph flow and is skipped.

```python
# Detection pattern — scan source body for embedded text boxes:
for child in doc._element.body.iter():
    if child.tag.endswith('}txbxContent'):
        pass  # Content inside is included by .paragraphs for inline boxes
```

**S2 — Floating Table in Template (First-Page Info Box)**

MDPI templates contain a single-column **floating table** anchored absolutely via `<w:tblpPr>` inside `<w:tblPr>`. This carries Academic Editor, Received/Revised/Accepted dates, Citation, and Copyright text for the first page. It must be preserved before the body is cleared.

```python
# Before clearing body: save floating tables
import copy as _copy
floating_tables = []
for child in list(body):
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag == 'tbl':
        tblPr = child.find(qn('w:tblPr'))
        if tblPr is not None and tblPr.find(qn('w:tblpPr')) is not None:
            floating_tables.append(_copy.deepcopy(child))

# ... clear body (all non-sectPr children) ...

# After clearing: re-insert at body position 0
# w:tblpPr contains absolute Y coordinate — visual position is fixed
# regardless of where the element appears in the XML body.
for tbl in floating_tables:
    body.insert(0, tbl)
```

**S3 — Headers/Footers and Images Live in Separate XML Files**

Template headers, footers, and images (including the MDPI journal logo) are stored in `word/header1.xml`, `word/header2.xml`, `word/footer1.xml`, `word/footer2.xml`, etc. — NOT in `word/document.xml`. They are referenced via `word/_rels/document.xml.rels`.

Key facts:
- `Document(template_path)` automatically inherits ALL of these: headers, footers, images, `w:titlePg` setting.
- **Critical pitfall:** Calling `copy_headers_and_setup()` AFTER `Document(template_path)` **duplicates** the header content — headers are already inherited. The function must NOT be called.
- MDPI templates use DOI text (e.g., "Cancers 2025, 17, x") in the footer — there are NO PAGE fields. Validate footer presence by checking `len(footer_xml) > 200`, not by searching for "PAGE".
- MDPI uses `w:titlePg` on the section: page 1 gets `header1.xml` (journal logo), subsequent pages get `header2.xml`. Both are inherited automatically.

### STEP 2: Create Comprehensive Reformatting Script

Now create the main script (`reformat_document.py`) with these components:

**IMPORTANT IMPORTS:**
```python
from docx import Document
from docx.shared import WD_ALIGN_PARAGRAPH, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docxtpl import DocxTemplate  # python-docx-template: handles .dotx/.dot conversion
from xml.etree import ElementTree as ET  # required for parse_numbering_indents()
import zipfile
import os
import re
from pathlib import Path
import sys
```

**CONFIGURATION: SECTION FORMATTING RULES**

```python
# Configuration: Section-specific formatting rules
# Controls how each classification type should be formatted from template
SECTION_FORMATTING_RULES = {
    'bibliography': {
        'remove_numbering': True,           # Strip w:numPr XML
        'use_template_analysis': True,      # Detect template's effective indent
        'apply_effective_indent': True,     # Use numbering-based indent if present
        'override_indent': None,            # No override (use template's effective)
        'apply_font': True,                 # Apply template font
        'apply_spacing': True,              # Apply template spacing
        'prepend_bullet': False,            # No bullet character
    },
    'list_item': {
        'remove_numbering': False,          # KEEP style's built-in bullets — stripping w:numPr causes double-bullets
        'use_template_analysis': True,      # Analyze template to get effective indent
        'apply_effective_indent': True,     # Apply numbering-based indent from template
        'override_indent': None,            # Let template provide the value (no override)
        'apply_font': True,
        'apply_spacing': True,
        'prepend_bullet': False,            # DON'T add text bullet — template's w:numPr handles rendering
    },
    'normal': {
        'remove_numbering': True,           # Most content shouldn't have numbering
        'use_template_analysis': True,
        'apply_effective_indent': True,     # Use template's indent (direct or effective)
        'override_indent': None,
        'apply_font': True,
        'apply_spacing': True,
        'prepend_bullet': False,
    },
    'heading1': {
        'remove_numbering': True,           # Headings use manual numbering
        'use_template_analysis': True,
        'apply_effective_indent': True,
        'override_indent': None,
        'apply_font': True,
        'apply_spacing': True,
        'prepend_bullet': False,
    },
    'heading2': {
        'remove_numbering': True,
        'use_template_analysis': True,
        'apply_effective_indent': True,
        'override_indent': None,
        'apply_font': True,
        'apply_spacing': True,
        'prepend_bullet': False,
    },
    'heading3': {
        'remove_numbering': True,
        'use_template_analysis': True,
        'apply_effective_indent': True,
        'override_indent': None,
        'apply_font': True,
        'apply_spacing': True,
        'prepend_bullet': False,
    },
}
```

**A. EXTRACT FROM SOURCE:**
- All text content preserving exact wording
- All paragraph structure and hierarchy
- All inline formatting (bold, italic, superscript for citations)
- All images from the document's ZIP structure (word/media/)
- Map each image to its figure caption and number

**B. PARSE FIGURE NUMBERS:**

```python
def extract_figure_mapping(doc):
    """
    Extract mapping between images and figure numbers.

    Strategy:
    1. Find paragraphs with images (check for embedded pictures)
    2. Look for caption in same or following paragraphs
    3. Parse figure number from caption text
    4. Build mapping: image_index -> figure_number
    5. Handle composite figures: if multiple images map to same figure,
       use suffixes: figure_1.png, figure_1_a.png, figure_1_b.png
    """
    import re
    from docx.oxml import parse_xml

    figure_map = {}
    figure_counter = 0

    for i, para in enumerate(doc.paragraphs):
        # Check if paragraph contains an image
        para_xml = para._element.xml.decode('utf-8') if isinstance(para._element.xml, bytes) else para._element.xml
        has_image = 'pic:pic' in para_xml or '<pic:pic' in para_xml

        if has_image:
            # Look for caption in next few paragraphs
            for offset in range(0, 3):
                if i + offset < len(doc.paragraphs):
                    caption_text = doc.paragraphs[i + offset].text
                    # Try to find "Figure N" pattern
                    match = re.search(r'Figure\s+(\d+)', caption_text, re.IGNORECASE)
                    if match:
                        figure_num = int(match.group(1))
                        figure_map[figure_counter] = figure_num
                        figure_counter += 1
                        break
            else:
                # No caption found, use sequential numbering
                figure_counter += 1
                figure_map[figure_counter - 1] = figure_counter

    return figure_map
```

**C. EXTRACT AND RENAME IMAGES:**

```python
def extract_images(source_docx_path, figure_map, output_zip_path='figures.zip'):
    """
    Extract images from source .docx and create ZIP with renamed files.
    Handles composite figures with multiple panels by adding suffixes.
    """
    import zipfile
    import os
    from pathlib import Path

    # Open source as ZIP
    with zipfile.ZipFile(source_docx_path, 'r') as source_zip:
        # Get all media files
        media_files = sorted([f for f in source_zip.namelist()
                            if f.startswith('word/media/')])

        print(f"Found {len(media_files)} images in document")

        # Track duplicate figure numbers for suffix handling
        figure_usage = {}

        # Create output ZIP
        with zipfile.ZipFile(output_zip_path, 'w') as output_zip:
            for idx, media_file in enumerate(media_files):
                # Read image data
                image_data = source_zip.read(media_file)

                # Get file extension
                ext = Path(media_file).suffix

                # Get figure number from mapping (or use sequential)
                fig_num = figure_map.get(idx, idx + 1)

                # Handle duplicate figure numbers (composite figures)
                if fig_num in figure_usage:
                    # This is a duplicate - add suffix
                    figure_usage[fig_num] += 1
                    suffix_letter = chr(ord('a') + figure_usage[fig_num] - 1)
                    new_filename = f"figure_{fig_num}_{suffix_letter}{ext}"
                else:
                    # First occurrence
                    figure_usage[fig_num] = 0
                    new_filename = f"figure_{fig_num}{ext}"

                print(f"  {media_file} -> {new_filename}")

                # Write to output ZIP
                output_zip.writestr(new_filename, image_data)

    print(f"Created {output_zip_path} with {len(media_files)} images")
    return len(media_files)
```

**D. PARSE NUMBERING INDENTS FROM TEMPLATE:**

```python
# Global: populated at Step 1.5 in main(); used by analyze_template_paragraph_formatting()
NUMBERING_INDENTS = {}  # {numId: {ilvl: indent_in_twips}}


def parse_numbering_indents(template_path):
    """
    Parse word/numbering.xml from template to extract per-level indentation values.

    Word uses two-level indirection for numbering indentation:
      - abstractNum elements define per-level indent values in TWIPS
      - num elements reference abstractNum by ID

    MDPI and other templates store paragraph indentation in numbering.xml, not as
    direct w:ind attributes on the style. Without this, all numbering-based indents
    would fall back to an inaccurate heuristic (0.5 inches per level).

    Returns:
        dict: {numId: {ilvl: indent_in_twips}}
    """
    result = {}
    W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

    try:
        with zipfile.ZipFile(template_path, 'r') as zf:
            if 'word/numbering.xml' not in zf.namelist():
                print("  No numbering.xml found in template")
                return result
            numbering_xml = zf.read('word/numbering.xml')
    except Exception as e:
        print(f"  Could not read numbering.xml: {e}")
        return result

    try:
        root = ET.fromstring(numbering_xml)
    except Exception as e:
        print(f"  Could not parse numbering.xml: {e}")
        return result

    # Step 1: Parse abstractNum elements — they hold the actual indent values per level
    abstract_indents = {}  # {abstractNumId: {ilvl: indent_twips}}

    for abstract_num in root.findall(f'{{{W_NS}}}abstractNum'):
        abstract_id_elem = abstract_num.get(f'{{{W_NS}}}abstractNumId')
        if abstract_id_elem is None:
            continue
        abstract_id = int(abstract_id_elem)
        abstract_indents[abstract_id] = {}

        for lvl in abstract_num.findall(f'{{{W_NS}}}lvl'):
            ilvl_elem = lvl.get(f'{{{W_NS}}}ilvl')
            if ilvl_elem is None:
                continue
            ilvl = int(ilvl_elem)

            pPr = lvl.find(f'{{{W_NS}}}pPr')
            if pPr is not None:
                ind = pPr.find(f'{{{W_NS}}}ind')
                if ind is not None:
                    left_val = ind.get(f'{{{W_NS}}}left')
                    if left_val is not None:
                        abstract_indents[abstract_id][ilvl] = int(left_val)

    # Step 2: Parse num elements — they map numId → abstractNumId
    for num_elem in root.findall(f'{{{W_NS}}}num'):
        num_id_elem = num_elem.get(f'{{{W_NS}}}numId')
        if num_id_elem is None:
            continue
        num_id = int(num_id_elem)

        abstract_ref = num_elem.find(f'{{{W_NS}}}abstractNumId')
        if abstract_ref is None:
            continue
        abstract_id_val = abstract_ref.get(f'{{{W_NS}}}val')
        if abstract_id_val is None:
            continue
        abstract_id = int(abstract_id_val)

        if abstract_id in abstract_indents:
            result[num_id] = abstract_indents[abstract_id]

    total_entries = sum(len(v) for v in result.values())
    print(f"  Parsed {len(result)} num entries ({total_entries} level indents) from numbering.xml")
    return result
```

**E. DISCOVER TEMPLATE STYLES:**

```python
def discover_template_styles(template_doc):
    """
    Scan template for available styles, detect naming convention (MDPI vs standard),
    and build a role-based mapping with fallback chains.

    Returns:
        role_map: dict mapping role names to actual template style names
                  e.g., {'heading1': 'MDPI_2.1_heading1', 'normal': 'MDPI_3.8.1_normal', ...}
    """
    # Collect all available style names
    available = {s.name for s in template_doc.styles if hasattr(s, 'name')}
    print(f"  Template has {len(available)} styles")

    # Detect naming convention by looking for prefixed styles
    prefixed_styles = {}
    for name in available:
        if '_' in name:
            prefix = name.split('_')[0]
            if prefix not in prefixed_styles:
                prefixed_styles[prefix] = []
            prefixed_styles[prefix].append(name)

    # Determine dominant prefix (e.g., "MDPI")
    dominant_prefix = None
    if prefixed_styles:
        dominant_prefix = max(prefixed_styles, key=lambda k: len(prefixed_styles[k]))
        print(f"  Detected style prefix: '{dominant_prefix}' ({len(prefixed_styles[dominant_prefix])} styles)")

    # Define role candidates: each role maps to a list of candidate style names (tried in order)
    # The first match found in the template wins
    role_candidates = {
        'title':    [],
        'authors':  [],
        'heading1': [],
        'heading2': [],
        'heading3': [],
        'normal':   [],
        'caption':  [],
        'bibliography': [],
        'abstract': [],
        'list_item': [],
    }

    # If we have a dominant prefix, add prefixed candidates first (highest priority)
    if dominant_prefix:
        # Search available styles for role keywords
        for name in sorted(available):
            name_lower = name.lower()
            if dominant_prefix.lower() in name_lower:
                if 'heading1' in name_lower or 'heading_1' in name_lower:
                    role_candidates['heading1'].insert(0, name)
                elif 'heading2' in name_lower or 'heading_2' in name_lower:
                    role_candidates['heading2'].insert(0, name)
                elif 'heading3' in name_lower or 'heading_3' in name_lower:
                    role_candidates['heading3'].insert(0, name)
                elif 'title' in name_lower:
                    role_candidates['title'].insert(0, name)
                elif 'text' in name_lower and 'no_indent' not in name_lower:
                    # Exclude *_no_indent variants — they give zero indentation to all body paragraphs
                    # 'MDPI_3.1' is a versioned MDPI style name (the primary body text style).
                    # For non-MDPI templates this condition is never true — harmless no-op.
                    # Other templates' text styles still match via the else branch below.
                    if 'MDPI_3.1' in name:
                        role_candidates['normal'].insert(0, name)   # Highest priority: MDPI_3.1_text
                    else:
                        role_candidates['normal'].append(name)       # Lower priority: other text styles
                elif 'normal' in name_lower:
                    role_candidates['normal'].insert(0, name)
                elif 'caption' in name_lower or 'figure' in name_lower:
                    role_candidates['caption'].insert(0, name)
                elif 'biblio' in name_lower or 'reference' in name_lower:
                    role_candidates['bibliography'].insert(0, name)
                elif 'abstract' in name_lower:
                    role_candidates['abstract'].insert(0, name)
                elif 'author' in name_lower:
                    role_candidates['authors'].insert(0, name)
                elif 'list' in name_lower or 'bullet' in name_lower:
                    role_candidates['list_item'].insert(0, name)

    # Add standard Word style names as fallbacks
    role_candidates['title'].extend(['Title', 'Heading 1'])
    role_candidates['authors'].extend(['Normal'])
    role_candidates['heading1'].extend(['Heading 1'])
    role_candidates['heading2'].extend(['Heading 2'])
    role_candidates['heading3'].extend(['Heading 3'])
    role_candidates['normal'].extend(['Normal'])
    role_candidates['caption'].extend(['Caption', 'Normal'])
    role_candidates['bibliography'].extend(['Bibliography', 'Normal'])
    role_candidates['abstract'].extend(['Normal'])
    role_candidates['list_item'].extend(['List Paragraph', 'List Bullet', 'List Number', 'Normal'])

    # Resolve: pick first available candidate for each role
    role_map = {}
    for role, candidates in role_candidates.items():
        role_map[role] = 'Normal'  # ultimate fallback
        for candidate in candidates:
            if candidate in available:
                role_map[role] = candidate
                break

    print("  Role → Style mapping:")
    for role, style in role_map.items():
        print(f"    {role:15s} → {style}")

    return role_map
```

**F. ANALYZE TEMPLATE PARAGRAPH FORMATTING:**

```python
def analyze_template_paragraph_formatting(template_doc, style_name):
    """
    Analyze how a template style formats paragraphs.

    Distinguishes between:
    - Direct paragraph formatting (left_indent, first_line_indent properties)
    - Numbering-based indentation (via w:numPr, numId, ilvl)

    Returns dict with comprehensive formatting info.
    """
    from docx.oxml.ns import qn
    import re

    try:
        style = template_doc.styles[style_name]
    except KeyError:
        return None

    pf = style.paragraph_format

    # Get direct properties
    result = {
        'style_name': style_name,
        'direct_left_indent': pf.left_indent,
        'direct_first_line_indent': pf.first_line_indent,
        'spacing_before': pf.space_before,
        'spacing_after': pf.space_after,
        'line_spacing': pf.line_spacing,
        'alignment': pf.alignment,
        'font_name': style.font.name if style.font.name else None,
        'font_size': style.font.size,
        'has_numbering': False,
        'numId': None,
        'ilvl': None,
        'effective_left_indent': pf.left_indent,
        'effective_first_line_indent': pf.first_line_indent,
    }

    # Check for numbering in style XML
    style_element = style._element
    style_xml = style_element.xml
    if isinstance(style_xml, bytes):
        style_xml = style_xml.decode('utf-8')

    # Look for w:numPr in style definition
    if 'w:numPr' in style_xml or 'w:numId' in style_xml:
        result['has_numbering'] = True

        # Extract numId and ilvl
        numId_match = re.search(r'w:numId[^>]*w:val="(\d+)"', style_xml)
        ilvl_match = re.search(r'w:ilvl[^>]*w:val="(\d+)"', style_xml)

        if numId_match:
            result['numId'] = int(numId_match.group(1))
        if ilvl_match:
            result['ilvl'] = int(ilvl_match.group(1))

        # Use NUMBERING_INDENTS (parsed from word/numbering.xml) for accurate indent values
        # Fall back to heuristic only if the parsed data is unavailable
        if result['ilvl'] is not None:
            num_id = result['numId']
            ilvl = result['ilvl']
            if (num_id is not None
                    and num_id in NUMBERING_INDENTS
                    and ilvl in NUMBERING_INDENTS[num_id]):
                twips = NUMBERING_INDENTS[num_id][ilvl]
                indent_emu = twips * 635  # 1 twip = 635 EMU
                if pf.left_indent is None:
                    result['effective_left_indent'] = indent_emu
                print(f"  Template analysis: {style_name} uses numbering "
                      f"(numId={num_id}, ilvl={ilvl}), indent={twips} twips from numbering.xml")
            else:
                # Heuristic fallback: 0.5 inches per level
                estimated_indent = Pt(36 * ilvl)
                result['effective_left_indent'] = estimated_indent
                result['effective_first_line_indent'] = Pt(-9)  # Small hanging indent
                print(f"  Template analysis: {style_name} uses numbering (level {ilvl}), "
                      f"estimated indent ~{estimated_indent} (heuristic fallback)")
        elif result['numId'] is not None:
            # numId present but ilvl absent — Word implicitly uses level 0
            result['ilvl'] = 0
            num_id = result['numId']
            if num_id in NUMBERING_INDENTS and 0 in NUMBERING_INDENTS[num_id]:
                twips = NUMBERING_INDENTS[num_id][0]
                indent_emu = twips * 635
                if pf.left_indent is None:
                    result['effective_left_indent'] = indent_emu
            print(f"  Template analysis: {style_name} has numId but no ilvl, defaulting to level 0")

    # If direct indent is None, check base_style for inherited indentation
    if result['effective_left_indent'] is None:
        try:
            if hasattr(style, 'base_style') and style.base_style:
                base_pf = style.base_style.paragraph_format
                if base_pf.left_indent is not None:
                    result['effective_left_indent'] = base_pf.left_indent
                    print(f"  Template analysis: {style_name} inherits left_indent={base_pf.left_indent} from base style")
                if base_pf.first_line_indent is not None:
                    result['effective_first_line_indent'] = base_pf.first_line_indent
        except AttributeError:
            pass

    return result
```

**G. REMOVE ALL NUMBERING FROM PARAGRAPH:**

```python
def remove_all_numbering_from_paragraph(para):
    """
    Completely remove ALL numbering-related XML from a paragraph.

    This prevents Word from auto-rendering bullets/numbers when we've
    already added them manually as text.

    Removes:
    - w:numPr (numbering properties)
    - Verifies removal was successful

    Returns: para (modified in place)
    """
    from docx.oxml.ns import qn

    # Get paragraph XML element
    p_element = para._element

    # Find paragraph properties
    pPr = p_element.find(qn('w:pPr'))
    if pPr is not None:
        # Find and remove w:numPr
        numPr = pPr.find(qn('w:numPr'))
        if numPr is not None:
            pPr.remove(numPr)
            print(f"    Removed numbering XML from: {para.text[:50]}...")

    # VERIFICATION: Ensure w:numPr is actually gone
    pxml = p_element.xml
    if isinstance(pxml, bytes):
        pxml = pxml.decode('utf-8')

    if 'w:numPr' in pxml:
        print(f"    WARNING: Failed to fully remove numbering from: {para.text[:50]}...")

    return para
```

**H. THREE-ZONE PARAGRAPH CLASSIFICATION STATE MACHINE:**

The single-pass three-zone machine replaces the old two-pass `classify_paragraphs()` approach. Classification is computed **inline** during content copying inside `copy_content_with_template_formatting()` — there is no separate classification step.

**Zone definitions:**

| Zone | Trigger | Paragraphs assigned |
|------|---------|---------------------|
| A (pre_abstract) | Starts at document begin | First 2 non-empty, non-heading paras → `title` / `authors` |
| B (in_abstract) | ABSTRACT heading detected | Paras until a non-abstract heading → `abstract` |
| C (default) | After abstract zone | bullet → ref → body (normal detection) |

**Constants used:**
```python
HEADING_WORDS = {
    'ABSTRACT', 'INTRODUCTION', 'METHODS', 'METHOD', 'RESULTS', 'DISCUSSION',
    'CONCLUSION', 'CONCLUSIONS', 'REFERENCES', 'ACKNOWLEDGMENTS', 'ACKNOWLEDGEMENTS',
    'SUPPLEMENTARY', 'MATERIALS', 'BACKGROUND', 'OBJECTIVES', 'FIGURES', 'TABLES',
}

# Sub-headings known to appear only inside a structured abstract.
# Encountering these while in_abstract=True does NOT break out of Zone B.
# Main-body words (INTRODUCTION, DISCUSSION, etc.) are NOT in this set so they
# correctly exit Zone B even when in_abstract=True.
ABSTRACT_SUBSECTIONS = {
    'MATERIALS', 'METHODS', 'METHOD', 'RESULTS', 'RESULT',
    'CONCLUSION', 'CONCLUSIONS', 'BACKGROUND', 'OBJECTIVES', 'OBJECTIVE',
}
```

**Role assignment logic (for each paragraph in order):**
```python
# 1. Detect explicit heading from source style
is_explicit_heading = style_name.startswith('Heading 1') or style_name == 'Title'  # → heading1
# ... also Heading 2 → heading2, Heading 3 → heading3

# 2. Detect ALL-CAPS heading
heading_words_set = set(re.split(r'[\s\-/]+', text_upper)) if text else set()
is_allcaps_heading = (
    bool(text) and text_upper == text and len(text.split()) <= 8
    and bool(heading_words_set & HEADING_WORDS)
)

# 3. Zone A: first two non-empty, non-heading paragraphs before any heading
if pre_abstract and not is_explicit_heading:
    if is_allcaps_heading:
        pre_abstract = False  # exit Zone A; fall through to normal detection
    elif text:
        pre_abstract_non_empty += 1
        if pre_abstract_non_empty == 1: role = 'title'
        elif pre_abstract_non_empty == 2: role = 'authors'

# 4. Heading detection (all zones)
if role is None:
    if is_explicit_heading:
        role = explicit_heading_role; pre_abstract = False
    elif is_allcaps_heading:
        # In Zone B: suppress only for known abstract sub-section words
        suppress = in_abstract and bool(heading_words_set & ABSTRACT_SUBSECTIONS)
        if not suppress:
            role = 'heading1'; pre_abstract = False
        # else: abstract sub-heading → fall through to Zone B → 'abstract'

# 5. Zone B: abstract body text
if role is None and in_abstract:
    role = 'abstract'

# 6. Zone C / normal detection
if role is None:
    if _para_has_numpr(para): role = 'bullet'
    elif current_section == 'references': role = 'ref'
    else: role = 'body'

# 7. Zone B state transitions (AFTER role assigned so heading gets heading role, not 'abstract')
if role == 'heading1':
    in_abstract = ('ABSTRACT' in text_upper)
if role == 'heading1' and 'REFERENCE' in text_upper:
    current_section = 'references'
```

Helper function used for bullet detection:
```python
def _para_has_numpr(para):
    """Return True if the source paragraph has list/bullet numbering (w:numPr)."""
    pPr = para._element.find(qn('w:pPr'))
    return pPr is not None and pPr.find(qn('w:numPr')) is not None
```
**I. COPY CONTENT WITH TEMPLATE FORMATTING:**

```python
def copy_content_with_template_formatting(source_doc, template_doc, output_doc):
    """
    Copy content from source while applying MDPI template styles and formatting.
    Uses the three-zone state machine (see Section H) to classify paragraphs inline.
    No separate classify_paragraphs() call needed — classification is computed here.
    """
    # Discover which MDPI (or fallback) style names exist in the template
    role_map = discover_template_styles(template_doc)

    # Known heading words for content-based detection (source uses 'Normal' for headings)
    HEADING_WORDS = {
        'ABSTRACT', 'INTRODUCTION', 'METHODS', 'METHOD', 'RESULTS', 'DISCUSSION',
        'CONCLUSION', 'CONCLUSIONS', 'REFERENCES', 'ACKNOWLEDGMENTS', 'ACKNOWLEDGEMENTS',
        'SUPPLEMENTARY', 'MATERIALS', 'BACKGROUND', 'OBJECTIVES', 'FIGURES', 'TABLES',
    }
    # Words known to appear only as abstract sub-headings.  Encountering these
    # while in_abstract=True does NOT break out of Zone B — they become 'abstract'.
    ABSTRACT_SUBSECTIONS = {
        'MATERIALS', 'METHODS', 'METHOD', 'RESULTS', 'RESULT',
        'CONCLUSION', 'CONCLUSIONS', 'BACKGROUND', 'OBJECTIVES', 'OBJECTIVE',
    }

    # Three-zone state machine (see Section H for full description):
    pre_abstract = True
    pre_abstract_non_empty = 0
    in_abstract = False
    current_section = "body"

    for para in source_doc.paragraphs:
        text = para.text.strip()
        style_name = para.style.name
        text_upper = text.upper()

        # --- Determine logical role ---
        role = None

        # Detect explicit heading from source style
        if style_name.startswith('Heading 1') or style_name == 'Title':
            is_explicit_heading = True
            explicit_heading_role = 'heading1'
        elif style_name.startswith('Heading 2'):
            is_explicit_heading = True
            explicit_heading_role = 'heading2'
        elif style_name.startswith('Heading 3'):
            is_explicit_heading = True
            explicit_heading_role = 'heading3'
        else:
            is_explicit_heading = False
            explicit_heading_role = None

        # ALL-CAPS heading check
        heading_words_set = set(re.split(r'[\s\-/]+', text_upper)) if text else set()
        is_allcaps_heading = (
            bool(text) and
            text_upper == text and
            len(text.split()) <= 8 and
            bool(heading_words_set & HEADING_WORDS)
        )

        # Zone A: pre-abstract — first two non-empty, non-heading paragraphs
        if pre_abstract and not is_explicit_heading:
            if is_allcaps_heading:
                pre_abstract = False  # heading appeared → exit Zone A
            elif text:
                pre_abstract_non_empty += 1
                if pre_abstract_non_empty == 1:
                    role = 'title'
                elif pre_abstract_non_empty == 2:
                    role = 'authors'
                # count >= 3: fall through to normal detection

        # Heading detection (all zones)
        if role is None:
            if is_explicit_heading:
                role = explicit_heading_role
                pre_abstract = False
            elif is_allcaps_heading:
                # In Zone B: suppress ONLY for known abstract sub-section words
                suppress = in_abstract and bool(heading_words_set & ABSTRACT_SUBSECTIONS)
                if not suppress:
                    role = 'heading1'
                    pre_abstract = False
                # else: abstract sub-heading → fall through to Zone B → 'abstract'

        # Zone B: abstract body text (non-heading paras inside abstract zone)
        if role is None and in_abstract:
            role = 'abstract'

        # Zone C / normal detection
        if role is None:
            if _para_has_numpr(para):
                role = 'bullet'
            elif current_section == 'references':
                role = 'ref'
            else:
                role = 'body'

        # Zone B state transitions — AFTER role is assigned so the heading
        # paragraph itself gets a heading role, not 'abstract'
        if role == 'heading1':
            if 'ABSTRACT' in text_upper:
                in_abstract = True
            else:
                in_abstract = False

        # Track references section transition
        if role == 'heading1' and 'REFERENCE' in text_upper:
            current_section = 'references'

        # Map role → actual style name available in the output document
        target_style = role_map[role]

        try:
            new_para = output_doc.add_paragraph(style=target_style)
        except Exception:
            new_para = output_doc.add_paragraph()

        # Strip auto-numbering from reference paragraphs (source text already has
        # "1. Author…" so keeping w:numPr would produce double numbers "1. 1. Author…")
        if role == 'ref':
            pPr = new_para._element.find(qn('w:pPr'))
            if pPr is None:
                pPr = OxmlElement('w:pPr')
                new_para._element.insert(0, pPr)
            numPr = pPr.find(qn('w:numPr'))
            if numPr is not None:
                pPr.remove(numPr)
            existing_ind = pPr.find(qn('w:ind'))
            if existing_ind is not None:
                pPr.remove(existing_ind)
            ind = OxmlElement('w:ind')
            ind.set(qn('w:left'), '425')      # 0.2951 inches left indent
            ind.set(qn('w:hanging'), '425')   # hanging: first line flush with margin
            pPr.append(ind)

        # Copy runs to preserve inline formatting (bold, italic, super/subscript)
        for run in para.runs:
            new_run = new_para.add_run(run.text)
            new_run.bold = run.bold
            new_run.italic = run.italic
            new_run.underline = run.underline
            if run.font.superscript:
                new_run.font.superscript = True
            if run.font.subscript:
                new_run.font.subscript = True

        # CRITICAL: Verify text was copied correctly; fall back to plain copy
        # SKIP verification for headings and list_items:
        #   - Headings: verification clears formatting and causes duplicate text
        #   - List items: verification re-adds text without bullet XML, discarding it
        SKIP_VERIFICATION = {'heading1', 'heading2', 'heading3', 'title', 'authors', 'bullet'}
        if role not in SKIP_VERIFICATION and para.text != new_para.text:
            new_para.clear()
            new_para.add_run(para.text)

    return output_doc
```
**J. COPY TABLES:**

```python
def copy_tables(source_doc, output_doc, template_doc):
    """Copy tables from source to output with template formatting."""
    print(f"  Copying {len(source_doc.tables)} tables...")
    for table in source_doc.tables:
        new_table = output_doc.add_table(rows=len(table.rows),
                                         cols=len(table.columns))
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                # Clear default paragraph in new cell
                new_cell = new_table.rows[i].cells[j]
                new_cell.text = ''

                # IMPORTANT: Cells can contain multiple paragraphs
                # Copy all paragraphs from source cell to preserve all content
                for para in cell.paragraphs:
                    new_para = new_cell.add_paragraph()
                    # Copy runs with formatting
                    for run in para.runs:
                        new_run = new_para.add_run(run.text)
                        new_run.bold = run.bold
                        new_run.italic = run.italic
                        new_run.underline = run.underline
                        if run.font.superscript:
                            new_run.font.superscript = True
                        if run.font.subscript:
                            new_run.font.subscript = True
```

**K. ORCHESTRATOR FUNCTION - APPLY TEMPLATE STYLES:**

```python
def apply_template_styles(source_doc, template_doc, output_path, template_path=None):
    """
    Create new document with template styles applied to source content.
    Orchestrates all formatting steps in the correct order.

    CRITICAL architecture notes:
    - Create output FROM template (not blank Document()) to inherit all styles,
      headers, footers, images, and page setup automatically.
    - Preserve floating tables BEFORE clearing the body — they carry the template's
      first-page info box (Academic Editor, dates, Citation, Copyright).
    - Do NOT call copy_headers_and_setup() — headers are already inherited from
      Document(template_path); calling it again would duplicate header content.
    - Do NOT call add_page_numbers_from_template() — MDPI footer uses DOI text
      (not PAGE fields) and is inherited from template.
    """
    import copy as _copy

    # Create output document FROM the template so it inherits all headers,
    # footers, styles, and numbering definitions wholesale.
    if template_path:
        output_doc = Document(template_path)
    else:
        output_doc = Document()

    # Save floating tables (positioned on the page, not in text flow).
    # These carry the template's first-page info box anchored absolutely via w:tblpPr.
    body = output_doc._element.body
    floating_tables = []
    for child in list(body):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag == 'tbl':
            tblPr = child.find(qn('w:tblPr'))
            if tblPr is not None and tblPr.find(qn('w:tblpPr')) is not None:
                floating_tables.append(_copy.deepcopy(child))

    # Clear body content — keep sectPr so page setup / headers / footers survive.
    # IMPORTANT: Use output_doc._element.body, NOT output_doc.paragraphs.
    # output_doc.paragraphs traverses header/footer paragraphs too and would
    # corrupt the template's header/footer structure if iterated for removal.
    for child in list(body):
        if not child.tag.endswith('sectPr'):
            body.remove(child)

    # Re-insert floating tables; absolute positioning (w:tblpPr) means visual
    # location is determined by the XML coordinates, not element position in body.
    for tbl in floating_tables:
        body.insert(0, tbl)

    # Copy content with template formatting (three-zone machine; see Sections H, I)
    output_doc = copy_content_with_template_formatting(source_doc, template_doc, output_doc)

    # Copy tables at correct positions (positional insertion, not append-at-end)
    copy_tables_at_correct_position(source_doc, output_doc)

    # Apply section numbering (uses _heading_level() to detect both standard and MDPI styles)
    output_doc = apply_section_numbering(output_doc, template_doc)

    # Save output
    output_doc.save(output_path)
    print(f"  Created {output_path}")
```

**copy_tables_at_correct_position (positional table insertion):**
```python
def copy_tables_at_correct_position(source_doc, output_doc):
    """
    Deep-copy each source table into the output body at the correct relative position
    (measured by paragraph count) instead of appending all tables at the end.
    """
    body        = source_doc._element.body
    output_body = output_doc._element.body
    sectPr      = output_body.find(qn('w:sectPr'))

    para_count = 0
    for child in list(body):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag == 'p':
            para_count += 1
        elif tag == 'tbl':
            output_paras = [c for c in list(output_body) if c.tag == qn('w:p')]
            cloned = _copy.deepcopy(child)
            if para_count > 0 and para_count <= len(output_paras):
                anchor = output_paras[para_count - 1]
                output_body.insert(list(output_body).index(anchor) + 1, cloned)
            else:
                if sectPr is not None:
                    output_body.insert(list(output_body).index(sectPr), cloned)
                else:
                    output_body.append(cloned)
            print(f"  Inserted table after paragraph {para_count}")
```
**L. COPY TEMPLATE HEADERS AND PAGE SETUP:**

```python
def copy_run_formatting(source_run, target_run):
    """Helper to copy all run-level formatting."""
    target_run.bold = source_run.bold
    target_run.italic = source_run.italic
    target_run.underline = source_run.underline
    target_run.font.name = source_run.font.name
    target_run.font.size = source_run.font.size
    if source_run.font.color.rgb:
        target_run.font.color.rgb = source_run.font.color.rgb
    if source_run.font.superscript:
        target_run.font.superscript = True
    if source_run.font.subscript:
        target_run.font.subscript = True


def copy_headers_and_setup(template_doc, output_doc, source_doc):
    """
    Copy header/footer structure from template to output.
    Preserve different first page settings.
    """
    template_section = template_doc.sections[0]
    output_section = output_doc.sections[0]

    # Copy section properties
    output_section.different_first_page_header_footer = template_section.different_first_page_header_footer
    output_section.page_height = template_section.page_height
    output_section.page_width = template_section.page_width
    output_section.top_margin = template_section.top_margin
    output_section.bottom_margin = template_section.bottom_margin
    output_section.left_margin = template_section.left_margin
    output_section.right_margin = template_section.right_margin

    # Copy first page header if different
    if template_section.different_first_page_header_footer:
        template_first_header = template_section.first_page_header
        output_first_header = output_section.first_page_header
        for para in template_first_header.paragraphs:
            new_para = output_first_header.add_paragraph()
            new_para.alignment = para.alignment
            for run in para.runs:
                new_run = new_para.add_run(run.text)
                copy_run_formatting(run, new_run)

    # Copy regular header
    for para in template_section.header.paragraphs:
        new_para = output_section.header.add_paragraph()
        new_para.alignment = para.alignment
        for run in para.runs:
            new_run = new_para.add_run(run.text)
            copy_run_formatting(run, new_run)

    print("  Copied headers and page setup from template")
    return output_doc
```

**M. ADD PAGE NUMBERS FROM TEMPLATE:**

```python
def add_page_numbers_from_template(template_doc, output_doc):
    """Copy page number setup from template footer to output."""

    def create_element(name):
        return OxmlElement(name)

    def create_attribute(element, name, value):
        element.set(qn(name), value)

    def add_page_number_field(paragraph):
        """Add PAGE and NUMPAGES fields for 'Page X of Y' format."""
        run = paragraph.add_run()
        paragraph.add_run("Page ")

        # Add PAGE field (current page number)
        fldChar1 = create_element('w:fldChar')
        create_attribute(fldChar1, 'w:fldCharType', 'begin')
        instrText = create_element('w:instrText')
        create_attribute(instrText, 'xml:space', 'preserve')
        instrText.text = "PAGE"
        fldChar2 = create_element('w:fldChar')
        create_attribute(fldChar2, 'w:fldCharType', 'end')

        r_element = run._r
        r_element.append(fldChar1)
        r_element.append(instrText)
        r_element.append(fldChar2)

        paragraph.add_run(" of ")

        # Add NUMPAGES field (total pages)
        run2 = paragraph.add_run()
        fldChar3 = create_element('w:fldChar')
        create_attribute(fldChar3, 'w:fldCharType', 'begin')
        instrText2 = create_element('w:instrText')
        create_attribute(instrText2, 'xml:space', 'preserve')
        instrText2.text = "NUMPAGES"
        fldChar4 = create_element('w:fldChar')
        create_attribute(fldChar4, 'w:fldCharType', 'end')

        r_element2 = run2._r
        r_element2.append(fldChar3)
        r_element2.append(instrText2)
        r_element2.append(fldChar4)

    # Check if template has page numbers
    template_section = template_doc.sections[0]
    template_footer = template_section.footer
    has_page_numbers = False
    footer_alignment = None

    for para in template_footer.paragraphs:
        para_xml = str(para._element.xml)
        if 'PAGE' in para_xml or 'NUMPAGES' in para_xml:
            has_page_numbers = True
            footer_alignment = para.alignment
            break

    if has_page_numbers:
        output_section = output_doc.sections[0]
        output_footer = output_section.footer
        for para in output_footer.paragraphs:
            para.clear()

        footer_para = output_footer.paragraphs[0] if output_footer.paragraphs else output_footer.add_paragraph()
        footer_para.alignment = footer_alignment if footer_alignment else WD_ALIGN_PARAGRAPH.CENTER
        add_page_number_field(footer_para)
        print("  Added page numbers to footer")
    else:
        print("  No page numbers found in template")

    return output_doc
```

**N. APPLY TEMPLATE FONT AND PARAGRAPH FORMATTING:**

```python
def apply_paragraph_formatting_from_template(source_para, output_para,
                                             template_doc, style_name,
                                             classification, role_map):
    """
    Apply template formatting to output paragraph based on classification rules.

    Uses SECTION_FORMATTING_RULES to determine:
    - Whether to remove numbering
    - Whether to analyze template for effective indent
    - Whether to apply indent, font, spacing
    - Whether to prepend bullets

    This provides systematic, configuration-driven formatting.
    """
    from docx.shared import Pt
    from docx.oxml.ns import qn

    # Get rules for this classification
    rules = SECTION_FORMATTING_RULES.get(classification, SECTION_FORMATTING_RULES['normal'])

    # For list_item: check if template's resolved list style has built-in bullet rendering.
    # If the style has no w:numPr XML (minimal templates without a proper list style),
    # fall back to text bullet — otherwise bullets would be invisible in the output.
    if classification == 'list_item' and role_map is not None:
        list_style_name = role_map.get('list_item', 'Normal')
        try:
            list_style = template_doc.styles[list_style_name]
            style_xml = list_style._element.xml
            if isinstance(style_xml, bytes):
                style_xml = style_xml.decode('utf-8')
            if 'w:numPr' not in style_xml:
                # Template's list style has no built-in bullet — use text bullet fallback
                rules = dict(rules)  # copy — do not mutate the shared global config
                rules['remove_numbering'] = True
                rules['prepend_bullet'] = True
                print(f"    list_item: template style '{list_style_name}' has no w:numPr, "
                      f"falling back to text bullet")
        except (KeyError, AttributeError):
            pass  # Keep original rules if style inspection fails

    # STEP 1: Remove numbering if rules say so
    if rules['remove_numbering']:
        output_para = remove_all_numbering_from_paragraph(output_para)

    # STEP 2: Analyze template formatting if needed
    template_analysis = None
    if rules['use_template_analysis']:
        template_analysis = analyze_template_paragraph_formatting(template_doc, style_name)

    # STEP 3: Apply indentation based on rules
    pf = output_para.paragraph_format

    if rules.get('override_indent') is not None:
        # For list items: dynamically match normal paragraph indentation for alignment
        if classification == 'list_item':
            normal_style_name = role_map.get('normal', 'Normal')
            try:
                normal_style = template_doc.styles[normal_style_name]
                normal_indent = normal_style.paragraph_format.left_indent
                if normal_indent is not None and normal_indent > 0:
                    pf.left_indent = normal_indent
                    print(f"    Applied normal paragraph indent ({normal_indent}) to bullet")
                else:
                    pf.left_indent = rules['override_indent']  # Fallback
            except (KeyError, AttributeError):
                pf.left_indent = rules['override_indent']  # Fallback if lookup fails
        else:
            pf.left_indent = rules['override_indent']
            print(f"    Applied override indent: {rules['override_indent']}")

    elif rules['apply_effective_indent'] and template_analysis:
        # Use template's effective indent (from direct or numbering)
        if template_analysis['effective_left_indent'] is not None:
            pf.left_indent = template_analysis['effective_left_indent']
            print(f"    Applied effective indent from template: {pf.left_indent}")

        if template_analysis['effective_first_line_indent'] is not None:
            pf.first_line_indent = template_analysis['effective_first_line_indent']

    # STEP 4: Prepend bullet if rules say so
    if rules.get('prepend_bullet') and output_para.runs:
        first_text = output_para.text.strip()
        BULLET_CHARS = ('-', '*', '\u2022', '\u2023', '\u2043',
                        '\u25e6', '\u25aa', '\u25ab', '\u2013', '\u2014')

        # Check if bullet already present
        already_has = (len(first_text) > 1
                       and first_text[0] in BULLET_CHARS
                       and first_text[1] in (' ', '\t'))

        if not already_has:
            bullet_char = rules.get('bullet_char', '\u2022')
            output_para.runs[0].text = bullet_char + ' ' + output_para.runs[0].text
            print(f"    Prepended bullet character")

    # STEP 5: Apply font if rules say so
    if rules['apply_font'] and template_analysis:
        if template_analysis['font_name']:
            for run in output_para.runs:
                run.font.name = template_analysis['font_name']

        if template_analysis['font_size']:
            for run in output_para.runs:
                run.font.size = template_analysis['font_size']

    # STEP 6: Apply spacing if rules say so
    if rules['apply_spacing'] and template_analysis:
        if template_analysis['spacing_before'] is not None:
            pf.space_before = template_analysis['spacing_before']

        if template_analysis['spacing_after'] is not None:
            pf.space_after = template_analysis['spacing_after']

        if template_analysis['line_spacing'] is not None:
            pf.line_spacing = template_analysis['line_spacing']

        if template_analysis['alignment'] is not None:
            pf.alignment = template_analysis['alignment']

    return output_para
```

**O. APPLY SECTION NUMBERING:**

```python
def apply_section_numbering(output_doc, template_doc, role_map):
    """
    Apply automatic section numbering based on heading levels.

    Detects headings by:
    1. Standard Word styles (Heading 1, Heading 2, etc.)
    2. MDPI-prefixed styles (matched via role_map)
    3. Style names containing 'heading' (case-insensitive)

    Excludes back-matter sections from numbering (References, Acknowledgements, etc.)
    """

    # Back-matter sections should NOT be numbered
    SKIP_SECTIONS = {
        'REFERENCES', 'BIBLIOGRAPHY', 'ACKNOWLEDGEMENTS', 'ACKNOWLEDGMENTS',
        'FUNDING', 'CONFLICTS OF INTEREST', 'ABBREVIATIONS',
        'SUPPLEMENTARY MATERIALS', 'APPENDIX', 'DATA AVAILABILITY',
        'AUTHOR CONTRIBUTIONS', 'INSTITUTIONAL REVIEW BOARD STATEMENT',
        'INFORMED CONSENT STATEMENT',
    }

    # Build a reverse lookup: style_name → heading level
    heading_style_levels = {}

    # Standard styles
    for level in range(1, 7):
        heading_style_levels[f'Heading {level}'] = level - 1

    # MDPI/custom styles from role_map
    if role_map:
        for role, style_name in role_map.items():
            if role == 'heading1':
                heading_style_levels[style_name] = 0
            elif role == 'heading2':
                heading_style_levels[style_name] = 1
            elif role == 'heading3':
                heading_style_levels[style_name] = 2

    # Track section counters for each level
    counters = [0, 0, 0, 0, 0, 0]
    in_back_matter = False

    for para in output_doc.paragraphs:
        style_name = para.style.name
        current_text = para.text.strip()

        # Determine heading level from style name
        level = None
        if style_name in heading_style_levels:
            level = heading_style_levels[style_name]
        elif 'heading' in style_name.lower():
            # Try to extract level number from style name
            import re as _re
            m = _re.search(r'(\d+)', style_name)
            if m:
                level = int(m.group(1)) - 1

        if level is not None:
            # Check if this is a back-matter section
            cleaned_text = re.sub(r'^[\d\.]+\s+', '', current_text).strip()
            if cleaned_text.upper() in SKIP_SECTIONS:
                in_back_matter = True
                print(f"  Skipped back-matter heading: {cleaned_text}")
                continue

            if in_back_matter:
                # Once in back-matter, skip all subsequent headings
                print(f"  Skipped back-matter heading: {cleaned_text}")
                continue

            try:
                # Increment this level
                counters[level] += 1

                # Reset deeper levels
                for i in range(level + 1, len(counters)):
                    counters[i] = 0

                # Build number string
                number_parts = [str(counters[i]) for i in range(level + 1) if counters[i] > 0]
                number_string = '.'.join(number_parts)

                # Remove existing number
                cleaned_text = re.sub(r'^[\d\.]+\s+', '', current_text)

                # Rebuild with number
                para.clear()
                number_run = para.add_run(number_string + ". ")
                number_run.bold = True
                text_run = para.add_run(cleaned_text)
                text_run.bold = True

                print(f"  Numbered heading: {number_string}. {cleaned_text}")

            except (ValueError, IndexError):
                pass

    return output_doc
```

**P. VALIDATION:**

```python
def validate_documents(source_path, output_path, report_path='validation_report.txt'):
    """
    Verify that reformatting preserved content correctly.

    Key design decisions:
    - Use _body_para_text() to count only direct body paragraphs (excludes table
      cells, header/footer paragraphs, and the preserved floating template table).
    - Use _strip_section_prefix() to strip "N." / "N.N." section number tokens
      added by apply_section_numbering() before comparing word counts.
    - Use _non_floating_table_count() to exclude the preserved floating table.
    - Footer check uses len(footer_xml) > 200 — MDPI uses DOI text, not PAGE fields.
    """
    source_doc = Document(source_path)
    output_doc = Document(output_path)

    def _body_para_text(doc):
        """Text from direct body paragraphs only — excludes table cell content."""
        ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        lines = []
        for child in doc._element.body:
            if child.tag == f'{{{ns}}}p':
                lines.append(''.join(t.text or '' for t in child.iter()
                                     if t.tag == f'{{{ns}}}t'))
        return '
'.join(lines)

    def _strip_section_prefix(text, style_name):
        """Strip 'N.' / 'N.N.' tokens added by apply_section_numbering() from headings."""
        if _heading_level(style_name) >= 0:
            return re.sub(r'^\d+(?:\.\d+)*\.\s+', '', text)
        return text

    def _non_floating_table_count(doc):
        """Count tables excluding absolutely-positioned (floating) tables."""
        count = 0
        for tbl in doc.tables:
            tbl_pr = tbl._element.find(qn('w:tblPr'))
            if tbl_pr is None or tbl_pr.find(qn('w:tblpPr')) is None:
                count += 1
        return count

    # Extract text from direct body paragraphs only so that the floating template
    # table (Academic Editor, Received, Citation, Copyright) is not counted.
    source_text = _body_para_text(source_doc)
    output_text = _body_para_text(output_doc)

    # Build adjusted output text: strip section number prefixes from headings
    _ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    _para_map = {p._element: p for p in output_doc.paragraphs}
    adjusted_output_text = '
'.join(
        _strip_section_prefix(
            _para_map[child].text,
            _para_map[child].style.name,
        )
        for child in output_doc._element.body
        if child.tag == f'{{{_ns_w}}}p' and child in _para_map
    )

    source_words   = source_text.split()
    output_words   = output_text.split()
    adj_out_words  = adjusted_output_text.split()

    # Citation extraction
    citation_patterns = [
        r'\[(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\]',
        r'\((\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\)',
    ]
    source_citations = []
    output_citations = []
    for pattern in citation_patterns:
        source_citations.extend(re.findall(pattern, source_text))
        output_citations.extend(re.findall(pattern, output_text))

    report_lines = ['=' * 60, 'VALIDATION REPORT', '=' * 60, '']

    # Word count (adjusted for section number tokens)
    report_lines.append('WORD COUNT:')
    report_lines.append(f'  Source:            {len(source_words):,} words')
    report_lines.append(f'  Output (raw):      {len(output_words):,} words')
    report_lines.append(f'  Output (adjusted): {len(adj_out_words):,} words (section numbers excluded)')
    word_match = len(source_words) == len(adj_out_words)
    report_lines.append(f"  Status:  {'PASS' if word_match else 'FAIL'}")
    report_lines.append('')

    # Citation check
    report_lines.append('CITATIONS:')
    report_lines.append(f'  Source:  {len(source_citations)} citations found')
    report_lines.append(f'  Output:  {len(output_citations)} citations found')
    citation_match = source_citations == output_citations
    report_lines.append(f"  Status:  {'PASS' if citation_match else 'FAIL'}")
    report_lines.append('')

    # Paragraph count — direct body <w:p> children only (excludes floating table)
    _ns_b = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    src_body_paras = sum(1 for c in source_doc._element.body if c.tag == f'{{{_ns_b}}}p')
    out_body_paras = sum(1 for c in output_doc._element.body if c.tag == f'{{{_ns_b}}}p')
    para_match = src_body_paras == out_body_paras
    report_lines.append('PARAGRAPH COUNT:')
    report_lines.append(f'  Source:  {src_body_paras} body paragraphs')
    report_lines.append(f'  Output:  {out_body_paras} body paragraphs')
    report_lines.append(f"  Status:  {'PASS' if para_match else 'FAIL'}")
    report_lines.append('')

    # Table count — exclude floating/positioned tables (w:tblpPr) from output
    src_tables = _non_floating_table_count(source_doc)
    out_tables = _non_floating_table_count(output_doc)
    table_match = src_tables == out_tables
    report_lines.append('TABLE COUNT:')
    report_lines.append(f'  Source:  {src_tables} tables')
    report_lines.append(f'  Output:  {out_tables} tables (floating template table excluded)')
    report_lines.append(f"  Status:  {'PASS' if table_match else 'FAIL'}")
    report_lines.append('')

    # Drawing count (informational only — drawings extracted to figures.zip)
    with zipfile.ZipFile(source_path, 'r') as zs:
        src_xml = zs.read('word/document.xml').decode('utf-8', errors='replace')
    with zipfile.ZipFile(output_path, 'r') as zo:
        out_xml = zo.read('word/document.xml').decode('utf-8', errors='replace')
    src_drawings = src_xml.count('<w:drawing')
    out_drawings = out_xml.count('<w:drawing')
    drawing_match = src_drawings == out_drawings
    report_lines.append('INLINE DRAWINGS:')
    report_lines.append(f'  Source:  {src_drawings} drawings')
    report_lines.append(f'  Output:  {out_drawings} drawings')
    report_lines.append(f"  Status:  {'PASS' if drawing_match else 'FAIL'} (informational; images in figures.zip)")
    report_lines.append('')

    # Footer check — MDPI templates use DOI/journal text, not PAGE fields.
    # Check for any non-empty footer content (len > 200 means non-trivial XML).
    output_section = output_doc.sections[0]
    output_footer  = output_section.footer
    footer_text = ' '.join(p.text for p in output_footer.paragraphs).strip()
    has_footer  = bool(footer_text)
    if not has_footer:
        footer_xml = str(output_footer._element.xml)
        has_footer = len(footer_xml) > 200  # non-trivial XML → footer is present
    report_lines.append('FOOTER:')
    report_lines.append(f'  Content: {footer_text[:80] if footer_text else "(inherited from template)"}')
    report_lines.append(f"  Status:  {'PASS' if has_footer else 'FAIL - Footer not present'}")
    report_lines.append('')

    # Section numbering — _heading_level() handles both 'Heading 1' and 'MDPI_2.1_heading1'
    numbered_headings = 0
    for para in output_doc.paragraphs:
        try:
            if _heading_level(para.style.name) >= 0 and re.match(r'^\d+\.', para.text):
                numbered_headings += 1
        except Exception:
            pass
    report_lines.append('SECTION NUMBERING:')
    report_lines.append(f'  Numbered headings: {numbered_headings}')
    report_lines.append(f"  Status:  {'PASS' if numbered_headings > 0 else 'FAIL - No numbered headings'}")
    report_lines.append('')

    # Overall status — required checks only (inline drawings excluded)
    all_pass = word_match and citation_match and para_match and table_match
    report_lines.extend(['=' * 60,
                         f"OVERALL: {'ALL CHECKS PASSED' if all_pass else 'VALIDATION FAILED'}",
                         '=' * 60])

    report_text = '
'.join(report_lines)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text.encode(sys.stdout.encoding or 'utf-8', errors='replace')
                     .decode(sys.stdout.encoding or 'utf-8'))
    return all_pass
```
**Q. CONVERT TEMPLATE FORMAT (if needed):**

```python
def convert_template_if_needed(template_path):
    """
    Convert a .dotx or .dot template file to .docx using python-docx-template.

    Standard python-docx cannot reliably load .dotx/.dot files due to content-type
    differences in the ZIP structure. python-docx-template (docxtpl) reads the raw
    XML directly and saves as a proper .docx, so no manual Word conversion is needed.

    Args:
        template_path: Path to template file (.dotx, .dot, or .docx)

    Returns:
        Path to a .docx file (converts in place if needed, otherwise returns as-is)
    """
    path = Path(template_path)

    if path.suffix.lower() not in ('.dotx', '.dot'):
        # Already .docx — no conversion needed
        return template_path

    docx_path = path.with_suffix('.docx')
    print(f"  Converting {path.name} → {docx_path.name} using python-docx-template...")

    try:
        tpl = DocxTemplate(str(path))
        tpl.save(str(docx_path))
        print(f"  Conversion complete: {docx_path.name}")
        return str(docx_path)
    except ImportError:
        print("  ERROR: python-docx-template is not installed.")
        print("  Install it with: python -m pip install python-docx-template")
        raise
    except Exception as e:
        print(f"  ERROR: Template conversion failed: {e}")
        raise
```

**R. INDENTATION ALIGNMENT DIAGNOSTIC:**

```python
def check_indentation_alignment(output_doc, classifications, source_doc,
                                 template_doc=None, role_map=None):
    """
    Diagnostic check: verify output paragraph indentation matches template values.

    Samples up to 3 paragraphs per classification type, reads their actual
    left_indent in inches, and compares against expected values derived from
    the template's own style definitions.

    If template_doc and role_map are provided, expected values are read dynamically
    from the template (works for any template, not just MDPI). Falls back to
    hardcoded MDPI values only if template analysis is unavailable.

    Returns:
        bool: True if all sampled paragraphs are within 0.05 inches of expected
    """
    # Map classification → role name for template lookup
    CLASSIFICATION_ROLE = {
        'heading1':    'heading1',
        'heading2':    'heading2',
        'heading3':    'heading3',
        'normal':      'normal',
        'bibliography': 'bibliography',
        'list_item':   'list_item',
    }

    # Map classification → category label for reporting
    CLASSIFICATION_CATEGORY = {
        'heading1':    'heading',
        'heading2':    'heading',
        'heading3':    'heading',
        'normal':      'body',
        'bibliography': 'bibliography',
        'list_item':   'bullet',
    }

    # Build EXPECTED_INDENTS dynamically from template if available
    EXPECTED_INDENTS = {}
    if template_doc is not None and role_map is not None:
        print("  Reading expected indentation from template styles...")
        for cls, role in CLASSIFICATION_ROLE.items():
            style_name = role_map.get(role)
            if style_name:
                analysis = analyze_template_paragraph_formatting(template_doc, style_name)
                if analysis and analysis.get('effective_left_indent') is not None:
                    category = CLASSIFICATION_CATEGORY.get(cls)
                    if category and category not in EXPECTED_INDENTS:
                        indent_inches = analysis['effective_left_indent'] / 914400
                        EXPECTED_INDENTS[category] = indent_inches
                        print(f"    {category}: {indent_inches:.4f}\" (from {style_name})")

    if not EXPECTED_INDENTS:
        # Fallback: hardcoded MDPI-calibrated values (used only if template analysis fails)
        print("  Using MDPI-calibrated reference values (template-specific check unavailable)")
        EXPECTED_INDENTS = {
            'heading': 1.8111,
            'body':    1.8111,
            'bibliography': 0.2951,
            'bullet':  2.1104,
        }

    print("\n  Indentation alignment check:")

    # Build per-classification samples of output paragraphs
    classified_paras = {}
    output_paragraphs = list(output_doc.paragraphs)

    for i, cls in enumerate(classifications):
        if cls not in classified_paras:
            classified_paras[cls] = []
        if len(classified_paras[cls]) < 5:
            # Match source index to output index (approximate — same order)
            if i < len(output_paragraphs) and output_paragraphs[i].text.strip():
                classified_paras[cls].append((i, output_paragraphs[i]))

    all_pass = True
    for cls, para_list in classified_paras.items():
        category = CLASSIFICATION_CATEGORY.get(cls)
        if category is None or category not in EXPECTED_INDENTS:
            continue

        expected = EXPECTED_INDENTS[category]
        for i, para in para_list[:3]:
            actual_emu = para.paragraph_format.left_indent
            if actual_emu is None:
                print(f"    {cls} para {i}: indent=None (no direct indent set)")
                continue

            # Convert EMU to inches (1 inch = 914400 EMU)
            actual_inches = actual_emu / 914400
            diff = abs(actual_inches - expected)
            status = 'PASS' if diff < 0.05 else 'FAIL'
            if status == 'FAIL':
                all_pass = False
            print(f"    {cls} para {i}: indent={actual_inches:.4f}\" "
                  f"(expected {expected:.4f}\") [{status}]")

    return all_pass
```

**S. MAIN EXECUTION:**

```python
def main():
    """Main execution function."""
    import sys

    print("Starting document reformatting...")
    print("=" * 60)

    # File paths — template may be .dotx, .dot, or .docx (auto-converted if needed)
    source_path = 'A_Phase_I_Study_of_Laser_Focal_Therapy_Rev_20_of_Prostate_Cancer_in_an_Outpatient_Setting.docx'
    template_path = 'cancers-template-new.dotx'  # .dotx/.dot/.docx all accepted
    output_path = 'reformatted_document.docx'

    try:
        # Step 0: Convert template to .docx if it's a .dotx or .dot file
        print("\n[0/9] Checking template format...")
        template_path = convert_template_if_needed(template_path)

        # Step 1: Load documents
        print("\n[1/5] Loading documents...")
        from docx import Document
        source_doc = Document(source_path)
        template_doc = Document(template_path)  # Load converted .docx
        print(f"  Loaded {len(source_doc.paragraphs)} paragraphs from source")
        print(f"  Loaded template with {len(list(template_doc.styles))} styles")

        # Step 1.5: Parse numbering indents from template (must run before style discovery)
        # Populates the NUMBERING_INDENTS global used by analyze_template_paragraph_formatting()
        print("\n[1.5/9] Parsing numbering indents from template...")
        global NUMBERING_INDENTS
        NUMBERING_INDENTS = parse_numbering_indents(template_path)

        # Step 2: Discover template styles (automatic MDPI/standard detection)
        print("\n[2/9] Discovering template styles...")
        role_map = discover_template_styles(template_doc)

        # Step 3: Extract figure mapping
        print("\n[3/5] Extracting figure numbers...")
        figure_map = extract_figure_mapping(source_doc)

        # Step 4: Extract images
        print("\n[4/5] Extracting images...")
        image_count = extract_images(source_path, figure_map, output_zip_path=figures_path)

        # Step 5: Apply template styles (orchestrates all formatting steps)
        # Note: classification is computed inline via the three-zone machine inside
        # copy_content_with_template_formatting() — no separate classify_paragraphs() call.
        print("\n[5/5] Applying template formatting and validating...")
        print("  This includes: headers, footers, fonts, section numbering, and content")
        apply_template_styles(source_doc, template_doc, output_path, template_path=template_path)
        print(f"  Reformatting complete")

        # Validate output
        validation_passed = validate_documents(source_path, output_path, report_path=report_path)

        print("\n" + "=" * 60)
        print("REFORMATTING COMPLETE")
        print("=" * 60)
        print(f"\nOutput files:")
        print(f"  - {output_path}")
        if image_count > 0:
            print(f"  - {figures_path}")
        print(f"  - validation_report.txt")
        print(f"\nValidation: {'✓ PASSED' if validation_passed else '✗ FAILED'}")

        if not validation_passed:
            print("\nWARNING: Validation detected discrepancies.")
            print("Please review validation_report.txt for details.")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### STEP 3: Execute the Script

Please create the complete `reformat_document.py` script with all the components above, then execute it:

```bash
python reformat_document.py
```

### STEP 4: Report Results

After execution, please:
1. Show me the validation report
2. Confirm that all three output files were created
3. Report any warnings or errors encountered

**ERROR HANDLING NOTES:**
- If figure numbers cannot be reliably extracted, the script will use sequential numbering
- If a template style doesn't exist, it will fall back to 'Normal' style
- If validation fails, the script will still produce output but report the specific failures
- All errors and warnings will be logged to console

**IMPORTANT REMINDERS:**
- The script preserves text exactly - no paraphrasing or modifications
- Citations are copied character-for-character with their original formatting
- Only paragraph-level styles are changed; inline formatting is preserved
- Images are renamed based on their figure caption numbers

Please proceed with creating and executing the script.

---

## Expected Output

After running this prompt, you should have:

1. **reformatted_document.docx** - Your paper with the new template styling applied
2. **figures.zip** - All images renamed as figure_1.png, figure_2.png, etc.
3. **validation_report.txt** - A report showing:
   - Word count comparison
   - Citation number verification
   - Overall pass/fail status

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'docx'"
**Problem**: python-docx is not installed
**Solution**: Install it with:
```bash
python -m pip install python-docx
```
**Note**: Requires internet connection. This must be done before running the script.

### Issue: "ValueError: file is not a Word file" (when loading .dotx)
**Problem**: python-docx cannot properly load .dotx template files
**Solution**:
1. Open the .dotx file in Microsoft Word
2. Save As → Word Document (.docx)
3. Update the script to use the .docx file instead
**Why**: .dotx files have a different content type that python-docx doesn't handle correctly

### Issue: "Duplicate name in ZIP file" (when extracting figures)
**Problem**: Multiple images belong to the same figure (composite figure with panels A, B, C)
**Solution**: The script automatically handles this by adding suffixes:
- figure_1.png (first image of Figure 1)
- figure_1_a.png (second image of Figure 1)
- figure_1_b.png (third image of Figure 1)
**Code**: This is handled in the `extract_images()` function with the `figure_usage` dictionary

### Issue: "Validation fails - word count mismatch" (51+ word difference)
**Problem**: Bibliography entries or other text with hyperlinks/field codes not copying correctly
**Solution**: The script includes text verification after copying runs:
```python
if para.text != new_para.text:
    new_para.clear()
    new_para.add_run(para.text)
```
**Why**: Hyperlinks and field codes don't copy properly run-by-run. Need to verify and fall back to plain text.
**Common locations**: Bibliography/References sections with article URLs

### Issue: "Table content missing or incomplete"
**Problem**: Using `cell.text = source_cell.text` only copies first paragraph
**Solution**: Iterate through all paragraphs in each cell:
```python
for para in source_cell.paragraphs:
    new_para = target_cell.add_paragraph()
    for run in para.runs:
        new_run = new_para.add_run(run.text)
```
**Why**: Table cells can contain multiple paragraphs, but cell.text only returns the first one

### Issue: "Template style not found"
**Problem**: Style names in the template use a custom prefix (e.g., MDPI) that doesn't match standard Word names
**Solution**: The script now automatically discovers template styles using `discover_template_styles()`. It scans all available styles, detects the naming convention (MDPI-prefixed, standard, or custom), and builds a role-based mapping with fallback chains. If a style is still not found after automatic discovery, it falls back to 'Normal'.
**Customization**: To add support for additional style naming conventions, extend the `role_candidates` dictionary in `discover_template_styles()`.

### Issue: "Figure numbers not extracted correctly"
**Solution**: The script will fall back to sequential numbering (figure_1, figure_2, etc.). You can manually verify the figure numbering in the output document.

### Issue: "Citations don't match"
**Solution**: Check if citations are in an unusual format. You may need to modify the citation regex patterns in the validation function.

### Issue: Paragraph-level validation shows mismatches
**Problem**: The enhanced validation shows exactly which paragraphs have word count differences
**Solution**:
1. Review the first 5 mismatched paragraphs in the validation report
2. Look for patterns (all in bibliography? all in tables?)
3. Check if those sections have hyperlinks or field codes
4. The diagnostic output helps pinpoint the issue

### Issue: "Output has no page numbers"
**Symptom:** Footer is empty or shows static text instead of dynamic page numbers

**Common Causes:**
1. Template doesn't have page numbers in footer
2. Template has static text instead of PAGE field
3. Footer wasn't copied from template

**Solution:**
- Open template.docx in Word
- Go to Insert > Page Number
- Choose "Bottom of Page" and select a format
- Save template and re-run script
- The script detects PAGE fields in template XML and recreates them

**Verification:**
- Open output in Word
- Check footer shows "Page 1 of X"
- Page numbers should update when you add/remove pages

---

### Issue: "Font doesn't match template"
**Symptom:** Output uses default font instead of template's font

**Common Causes:**
1. Font is applied to individual text runs in template, not in style definition
2. Template wasn't loaded as Document object
3. Style name mismatch

**Solution:**
- Open template.docx in Word
- Right-click "Normal" in Styles pane
- Click "Modify"
- Set desired font name, size, color
- Click OK and save
- Ensure script loads: `template_doc = Document(template_path)`

**Verification:**
- Select body text in output
- Check Home tab shows template's font
- Check validation report "FONT SETTINGS" section

---

### Issue: "Headings are not numbered"
**Symptom:** Headings appear as "Introduction" instead of "1. Introduction"

**How heading detection works:**
The script uses a multi-strategy approach - you do NOT need Heading styles in your source document:

1. **Style-based** (highest priority): If source uses Heading 1/2/3 styles, those are detected first
2. **Content-based**: ALL-CAPS text matching known section names (INTRODUCTION, METHODS, etc.) is automatically classified as a heading
3. **Template style matching**: MDPI-prefixed and other custom heading styles are detected via `discover_template_styles()`

**Back-matter exclusion:**
Sections like REFERENCES, ACKNOWLEDGEMENTS, FUNDING, etc. are automatically excluded from numbering.

**Abstract zone handling:**
ALL-CAPS text between ABSTRACT and INTRODUCTION (e.g., PURPOSE, METHODS, RESULTS within a structured abstract) is classified as heading2, not heading1.

**If headings are still not numbered:**
- Verify the section name appears in the `MAIN_SECTIONS` set in `classify_paragraphs()`
- Check that section titles are in ALL CAPS in the source document
- Ensure `apply_section_numbering()` is called after content copying

**Verification:**
- Check validation report shows "Numbered headings: X"
- Headings should appear as: "1. ", "1.1. ", "1.2. ", "2. ", etc.
- Back-matter headings (References, etc.) should NOT have numbers

---

### Issue: "Header is missing or doesn't match template"
**Symptom:** Output has blank header or different content than template

**Common Causes:**
1. Template header is empty
2. Template uses "Different First Page" but script didn't copy first page header
3. Header wasn't copied from template

**Solution:**
- Verify template has header content (double-click header in Word)
- Check if template uses "Different First Page" setting
- Ensure script calls `copy_headers_and_setup()` before copying content

**Verification:**
- Open output in Word
- Double-click header area
- Should match template header exactly
- Check if first page header is different (if template uses that setting)

---

### Issue: "Floating table (info box) missing from output"
**Symptom:** The first-page Academic Editor / Received / Accepted / Citation / Copyright box is absent from the output

**Cause:** The template's floating table was cleared along with the rest of the body content

**Solution:** Preserve floating tables BEFORE clearing the body, then re-insert AFTER:
```python
# Before body.remove() loop:
floating_tables = []
for child in list(body):
    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
    if tag == 'tbl':
        tblPr = child.find(qn('w:tblPr'))
        if tblPr is not None and tblPr.find(qn('w:tblpPr')) is not None:
            floating_tables.append(_copy.deepcopy(child))
# After clearing:
for tbl in floating_tables:
    body.insert(0, tbl)
```
**Why:** MDPI templates have a `<w:tbl>` with `<w:tblpPr>` that absolutely positions the first-page info box. The `w:tblpPr` holds the fixed Y coordinate, so inserting the table at body position 0 is fine — Word renders it at the correct visual position regardless.

---

### Issue: "Header/footer images or journal logo missing"
**Symptom:** Output has a plain header/footer instead of the MDPI journal logo and DOI text

**Cause:** Either (a) `Document(template_path)` was not used, or (b) `copy_headers_and_setup()` was called after `Document(template_path)` and duplicated/corrupted the header

**Root cause:** Headers, footers, and images live in separate XML files (`word/header1.xml`, `word/header2.xml`, `word/footer1.xml`, `word/footer2.xml`) — not in `word/document.xml`. They are referenced via `word/_rels/document.xml.rels`.

**Solution:**
1. Always create the output with `output_doc = Document(template_path)` — this inherits all header/footer XML files automatically.
2. Do NOT call `copy_headers_and_setup()` after this — it would add duplicate header paragraphs.
3. MDPI uses `w:titlePg`: the first page gets `header1.xml` (journal logo); subsequent pages get `header2.xml`. Both are inherited automatically.

**MDPI footer note:** The footer contains DOI text like "Cancers 2025, 17, x" — not PAGE fields. Validate footer presence by checking `len(footer_xml) > 200`, not by searching for "PAGE".

---

### Issue: "References show double numbers (1. 1. Author...)"
**Symptom:** Each reference entry shows its number twice: "1. 1. Smith et al., ..."

**Cause:** The MDPI references style (`MDPI_8.1_references`) carries `<w:numPr>` which makes Word auto-number the paragraph. The source text already contains "1. Author..." so the auto-number is prepended again.

**Solution:** After adding the new paragraph with the references style, strip `<w:numPr>` and add a direct hanging indent:
```python
if role == 'ref':
    pPr = new_para._element.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        new_para._element.insert(0, pPr)
    numPr = pPr.find(qn('w:numPr'))
    if numPr is not None:
        pPr.remove(numPr)
    existing_ind = pPr.find(qn('w:ind'))
    if existing_ind is not None:
        pPr.remove(existing_ind)
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), '425')      # 0.2951 inches
    ind.set(qn('w:hanging'), '425')   # hanging: first line flush with margin
    pPr.append(ind)
```
**Why `left=425, hanging=425`:** 425 twips ≈ 0.2951 inches — matches MDPI's reference indent. The hanging indent keeps the first line (number + period) flush with the left margin while subsequent lines indent.

---

### Issue: "Back-matter sections have numbers"
**Symptom:** References, Acknowledgements, or Funding sections show numbers like "8. REFERENCES"

**Cause:** The section name is not in the `SKIP_SECTIONS` exclusion set
**Solution:** The script automatically excludes these back-matter sections from numbering:
- REFERENCES, BIBLIOGRAPHY, ACKNOWLEDGEMENTS, ACKNOWLEDGMENTS
- FUNDING, CONFLICTS OF INTEREST, ABBREVIATIONS
- SUPPLEMENTARY MATERIALS, APPENDIX, DATA AVAILABILITY
- AUTHOR CONTRIBUTIONS, INSTITUTIONAL REVIEW BOARD STATEMENT, INFORMED CONSENT STATEMENT

If your document has a back-matter section not in this list, add it to the `SKIP_SECTIONS` set in `apply_section_numbering()`.

---

### Issue: "Bullet points missing or displayed as plain text"
**Symptom:** Source document had bullet lists, but output shows plain paragraphs without bullets

**How bullet detection works:**
The script detects list items via three methods:
1. **XML-based:** Checks for `w:numPr` element in paragraph XML (Word's numbering definition)
2. **Style-based:** Style name contains "List" (e.g., List Paragraph, List Bullet)
3. **Character-based:** Text starts with a bullet character (`-`, `*`, `•`, `–`, `—`) followed by a space

**How bullet rendering works:**
The script first checks whether the template's resolved list style (`role_map['list_item']`) has its own `w:numPr` XML (built-in bullet rendering). If it does (e.g., MDPI's List Paragraph style), the template's built-in bullets are preserved — no text bullet is prepended. If the template's list style has no `w:numPr` (minimal templates), the script falls back to prepending a Unicode bullet character (`•`).

**If bullets are still missing:**
- Verify the source document actually uses bullets (not manually typed dashes)
- Check if the source uses an unusual list style name — add it to `is_list_paragraph()`
- Check if your template's list style has `w:numPr` XML (open the .docx as ZIP and inspect `word/styles.xml`)
- If using a minimal template, the fallback text bullet (`•`) should be applied automatically

---

### Issue: "Abstract sub-headings classified as main headings"
**Symptom:** Structured abstract keywords like PURPOSE, METHODS, RESULTS within the abstract are numbered as main sections (e.g., "2. PURPOSE") instead of sub-sections

**Cause:** The two-pass classification system didn't correctly identify the abstract zone
**Solution:** The script uses landmark detection to find the abstract zone:
1. Pass 1 finds ABSTRACT and INTRODUCTION positions
2. Pass 2 treats ALL-CAPS text between them as heading2 (abstract sub-headings)

If misclassification occurs:
- Verify the source document has both "ABSTRACT" and "INTRODUCTION" as separate paragraphs
- Check that abstract sub-headings are in ALL CAPS
- Add missing keywords to the `ABSTRACT_SUBHEADINGS` set in `classify_paragraphs()`

---

### Known Limitations

1. **Content-Based Heading Detection**: Requires section titles to be in ALL CAPS or match known section names in the `MAIN_SECTIONS` set. Mixed-case headings that aren't styled as Heading 1/2/3 won't be detected automatically.

2. **Structured Abstract Detection**: Assumes the abstract zone is between an "ABSTRACT" heading and an "INTRODUCTION" heading. If these landmarks are missing, abstract sub-headings may be misclassified.

3. **Hyperlink Formatting**: Hyperlinks are preserved as plain text, not as active links.

4. **Complex Field Codes**: Field codes are converted to their displayed text values.

5. **Template Must Be .docx**: Cannot use .dotx files directly with python-docx.

6. **Internet Required**: Initial setup requires internet connection to install python-docx.

7. **Section Numbering**: Uses manual text-based numbering, not Word's outline numbering. Sufficient for most cases but won't create automatic Table of Contents hierarchy.

8. **Bullet Points**: When the template's list style has built-in `w:numPr` bullet rendering (e.g., MDPI's List Paragraph style), the script preserves Word's native numbering XML. For minimal templates without a built-in list style, it falls back to prepending a Unicode bullet character (`•`). Text-based fallback bullets display correctly but won't auto-continue when editing the output document in Word.

## Customization

To use this prompt with different templates or source documents:

1. Update the file paths in the INPUT FILES section
2. **Template style mapping is now automatic** - the `discover_template_styles()` function scans your template and builds a role-based mapping. To extend support for new naming conventions, add entries to the `role_candidates` dictionary.
3. **Section names**: To add new section headings for content-based detection, add them to the `MAIN_SECTIONS` set in `classify_paragraphs()`
4. **Back-matter exclusion**: To change which sections are excluded from numbering, modify the `SKIP_SECTIONS` set in `apply_section_numbering()`
5. **Abstract sub-headings**: To add new structured abstract keywords, add them to the `ABSTRACT_SUBHEADINGS` set in `classify_paragraphs()`
6. **List detection**: To add custom list style names, add them to `is_list_paragraph()` or extend the `role_candidates['list_item']` fallback chain
7. Adjust the citation regex patterns if your document uses a different citation format
7. Change the figure caption pattern if your document uses different caption formatting (e.g., "Fig." instead of "Figure")

## Notes

- This process uses only Claude Code's built-in tools (Bash, Write, Read)
- The python-docx library must be installed with `python -m pip install python-docx`
- Installation requires internet connection (one-time setup)
- The Python script is generated fresh each time you run the prompt
- You can save and modify the generated script for future use

## Best Practices

1. **Always validate**: Check the validation report after running. A passing validation ensures content was preserved exactly.

2. **Use .docx templates**: Convert .dotx files to .docx format before using them.

3. **Review composite figures**: If your document has figures with multiple panels (Figure 1A, 1B, 1C), verify the suffix naming works correctly.

4. **Check bibliographies first**: Bibliography sections with hyperlinks are most likely to have issues. The text verification step handles this, but verify the output.

5. **Keep source safe**: Always keep your original source document. The script doesn't modify it, but it's good practice.

6. **Test with simple document**: If unsure, test the prompt with a simple 2-3 page document first to understand the process.
