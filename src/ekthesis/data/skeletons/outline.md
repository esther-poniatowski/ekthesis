---
role: outline
status: draft
index:
aliases:
tags: []
purpose:
---

# Outline of {{artifact}}

<!-- yaml: outline — one key per section below; a section left empty is deleted -->

## Parts

<!-- yaml: parts[]: one subsection each, in reading order → name (the heading), claims[] (the numbered items, in order), support (the line led by **Support**) -->
<!-- e.g. 'Introduction', 'Methods', 'Results', 'Discussion' for a manuscript; one card, frame group or section otherwise -->
<!-- claims: cite each claim by its id in the claim boundaries, adding a wording only where the wording differs -->

### {{PART}}

1. {{CLAIM THAT THE PART MUST CARRY}}

**Support**: {{FIGURE, DERIVATION OR SOURCE THAT CARRIES THE CLAIMS}}

## Figures

<!-- yaml: figures[]: one subsection each, in reading order → name (the heading), caption (the line led by **Caption**), panels[]: one row each → panel, claim, evidence; optional -->
<!-- caption: state the claim of the figure as the sentence opening the caption -->
<!-- claim: cite each claim by its id in the claim boundaries -->
<!-- evidence: e.g. 'derivation', 'simulation', 'published dataset', 'none (defines objects)' -->

### {{FIGURE}}

**Caption**: {{CLAIM OPENING THE CAPTION}}

| Panel | Claim | Evidence |
| --- | --- | --- |
| {{PANEL}} | {{CLAIM OF THE PANEL}} | {{EVIDENCE FOR THE CLAIM}} |

## Excluded parts

<!-- yaml: excluded[]: one row each → part, reason; optional -->

| Part | Reason |
| --- | --- |
| {{PART LEFT OUT}} | {{REASON}} |

## Title and message

<!-- yaml: title, message, headline (the lines led by **Title**, **Message** and **Headline**); headline optional -->
<!-- derive the message from the central claim, the headline from the message, and the title from the headline -->

- **Title**: {{TITLE, OR A POINTER TO THE SOURCE LINE THAT PRINTS IT}}
- **Message**: {{THE ONE SENTENCE A READER SHOULD RETAIN}}
- **Headline**: {{THE MESSAGE, WITH ITS SURPRISE LEADING}}

## Notes

<!-- yaml: notes — content that fits no field above; optional -->
