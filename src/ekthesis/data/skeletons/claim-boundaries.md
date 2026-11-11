---
role: spec
status: draft
index:
aliases:
tags: []
purpose:
---

# Claim boundaries of {{artifact}}

<!-- yaml: claims — one key per section below; a section left empty is deleted -->

## Admissible claims

<!-- yaml: admissible — a tree rooted at the central claim → id, claim, relation (the italic label of each nested item), conditions, route, support, attitude, ground, premises[], consequences[] -->
<!-- for a scored submission, select the tree outward from the central claim, and keep each claim under the retention test of its relation (ekthesis, docs/theory/selection-of-ideas.md, ^retention); otherwise, list the admissible claims at the first level -->
<!-- id: e.g. 'C' for the central claim, 'P1' for a premise, 'K1' for a consequence; the outline cites claims by id -->
<!-- relation: a relation of the registry of ekthesis (data/registries/relations.yml), run from the item, its source and satellite, to the claim above it, its target and nucleus, e.g. 'evidence', 'background', 'condition', 'non-volitional-cause', 'elaboration'; a consequence at the first level is the target of an 'evidence' whose source is the central claim, written 'evidence from C', since the registry holds no relation from a consequence to the claim from which it follows -->
<!-- conditions: each a ground with the role 'condition' of the answer named under ground; mark each generic | special, a distinction that gnomon does not record yet (gnomon task condition-genericity) -->
<!-- route, support, attitude: the fields 'route.kind', 'support' and 'status' of the answer named under ground, stated here only while no answer record holds them; route: derivation | proof | simulation | estimation | measurement; support: unsupported | informal | formally-proven | empirically-supported; attitude: entertained | hypothesized | accepted | retracted; '—' for a claim cited from a publication -->
<!-- ground: the identifier of the answer record, or the anchored note, that holds the result, never restated; for a claim still untested against data, name the published dataset or the experiment needed -->

- **C**: {{CLAIM ANSWERING THE QUESTION}} · conditions: {{CONDITIONS, OR —}} · route: {{ROUTE}} · support: {{SUPPORT}} · attitude: {{ATTITUDE}} · ground: {{GROUND}}
  - **P1** *{{RELATION}}*: {{PREMISE}} · conditions: {{CONDITIONS, OR —}} · route: {{ROUTE}} · support: {{SUPPORT}} · attitude: {{ATTITUDE}} · ground: {{GROUND}}
- **K1** *evidence from C*: {{CONSEQUENCE OR PREDICTION}} · conditions: {{CONDITIONS, OR —}} · route: {{ROUTE}} · support: {{SUPPORT}} · attitude: {{ATTITUDE}} · ground: {{GROUND}}

## Surprise

<!-- yaml: surprise (the line led by **Surprise**); optional; for a scored submission -->

**Surprise**: {{ELEMENT OF THE CENTRAL CLAIM UNEXPECTED BY A SPECIALIST OF THE CLOSEST PRIOR ANSWER}}

## Excluded claims

<!-- yaml: excluded[]: one row each → claim, expected by, reason -->
<!-- record a claim only when a reader of a declared audience would expect it; 'expected by' names that audience, or one of its representatives (ekthesis, docs/theory/selection-of-ideas.md, ^exclusions) -->

| Claim | Expected by | Reason |
| --- | --- | --- |
| {{CLAIM OR WORDING EXCLUDED}} | {{AUDIENCE EXPECTING THE CLAIM}} | {{REASON}} |

## Wordings

<!-- yaml: wordings[]: one row each → concept, wording, where; optional -->

| Concept | Wording | Where |
| --- | --- | --- |
| {{CONCEPT}} | {{WORDING ADMITTED}} | {{WHERE THE WORDING APPLIES}} |

## Notes

<!-- yaml: notes — content that fits no field above; optional -->
