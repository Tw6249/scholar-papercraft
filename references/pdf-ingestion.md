# PDF Ingestion With Codex PDF Plugin

Use this reference when PDFs are source materials, exemplar papers, scanned papers, or paper-like documents for Scholar Papercraft work.

## Principle

Use the Codex PDF plugin first:

```text
PDF -> Codex PDF plugin visual/text inspection -> audit -> material classification -> Paper State
```

The PDF itself remains the evidence source. Extracted text, rendered screenshots, OCR, Markdown, and JSON are working artifacts only.

For papers with equations, tables, two-column layouts, figures, or scanned pages, prioritize rendered page inspection over plain text extraction. Use extracted text for search, navigation, and rough summaries; verify claim-bearing content against the rendered PDF pages.

Treat every PDF artifact by role:

- `factual_source`: author-owned source material or a PDF the user explicitly authorizes as factual evidence.
- `style_only`: exemplar papers and writing samples. Use only for rhetoric, section moves, density, and community conventions.
- `unverified`: default for parsed or extracted material until audited.

## Codex PDF Plugin Workflow

Invoke the Codex PDF plugin (`[@pdf](plugin://pdf@openai-primary-runtime)` / `pdf:pdf`) for PDF reading, rendering, extraction, and inspection. Follow its core rule: render pages to images when layout matters, and use `pdfplumber`, `pypdf`, or Poppler text extraction only for quick checks.

Recommended workflow:

1. Identify the PDF role: `factual_source`, `style_only`, or `unverified`.
2. Use the PDF plugin to inspect page count, metadata, and representative pages.
3. Render relevant pages before relying on formulas, tables, captions, algorithms, theorem statements, proofs, or numerical claims.
4. Use text extraction for navigation and rough content indexing only.
5. Record page numbers or page ranges for claim-bearing evidence in Paper State.
6. Build or update `.paper-state/material_map.json` and claim/evidence references only after visual verification.

Verification targets:

- equations, symbols, subscripts, superscripts, theorem assumptions, and proof dependencies;
- table cell values, units, headers, and footnotes;
- figure captions, axis labels, legends, and plotted quantities;
- multi-column reading order and section boundaries;
- reference numbers, citation mapping, and bibliography entries;
- OCR text in scanned or image-heavy pages.

If the PDF plugin extraction is poor, do not silently promote the text to evidence. Render the relevant pages and transcribe only the needed claim-bearing fragments, marking uncertain symbols with `[VERIFY: ...]`.

## Use In Scholar Papercraft

For style distillation, PDFs remain `style_only`; never import their facts, citations, assumptions, limitations, or result numbers.

For claim-evidence work, extracted or parsed PDFs are `unverified` until checked. Verify:

- equation spelling and theorem assumptions;
- table cell values and units;
- figure captions and labels;
- reference numbers and citation mapping;
- reading order for multi-column sections;
- OCR text in scanned pages.

When formulas are central, inspect rendered PDF pages side by side with any extracted text before using the content in a claim ledger.
