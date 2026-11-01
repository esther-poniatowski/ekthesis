---
tags:
  - decision
status: accepted
created: 2026-10-29
revised: 2026-11-01
index: "[Architecture decisions](docs/adr/_index.md)"
aliases:
  - Terminology, audience and project specifications
---
# Terminology, audience and project specifications

> [!QUESTION] Goal: which tool provides the mechanisms of glossaries, audience specifications and project specifications, and which repository holds their instances?

A project names its concepts in a glossary. Its project specification binds its glossary, its notation and its audiences. Each exposition of the project calibrates its claims, its terminology and its level of technicity against the audiences named by its record. `geonexus` declares these records with schemas of its own, and checks them with a checker of its own. The [decision of `gnomon` on terminology, audience and project specifications](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/docs/adr/terminology-audience-project-specifications.md) first gave these mechanisms to `gnomon`. Two later decisions change that assignment: the decision of `gnomon` on its scope moves glossaries and audiences to `ekthesis`, and the decision of `geonexus` on [tool roles](https://github.com/esther-poniatowski/geonexus/blob/0712bb5136960141f82ec65d5ae475834293af4a/docs/_decisions/tool-roles.md) divides the project specification.

## Decision

`ekthesis` provides the mechanisms of three record types: the glossary, the audience specification, and the binding of a project. Each mechanism holds a schema, a template generated from that schema, and the checks of its records. A consumer instantiates the records of its projects and of its audiences.

The project specification divides among three owners:

- the questions and the goals of a project form a research root record of `gnomon`;
- the binding of a project belongs to `ekthesis`;
- the identity of the project stays in its `repository.yml`.

The records of `ekthesis` form one chain:

- the **binding** of a project names its glossary, the notation of `gnomon` and its audiences, each by a logical target typed by the contract that the target must satisfy;
- a **glossary** names the concepts of a project, as the [decision on glossaries](glossaries.md) states;
- an **audience** specification records the knowledge, the skills and the register of a readership, as the [decision on audiences](audiences.md) states.

The record of an exposition names its audiences, and `ekthesis` checks the terms of the exposition against them.

## Constraints that decide the owner

- **Glossaries, audiences and bindings serve the presentation only.** A glossary names concepts for readers, an audience calibrates an exposition, and a binding selects the glossary, the notation and the audiences of a project. No inquiry needs these records to state, establish or check its content.
- **One symbol has one declaration.** The notation of `gnomon` refers to the inquiry records for their symbols. If the binding of a project restated those symbols, it would hold a second copy. The [single field per fact](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/docs/adr/single-field-per-fact.md) excludes that copy. Therefore, the binding names the notation and holds no symbol.
- **One question has one record.** If the binding of a project listed the questions of its scope, it would restate the question records. Therefore, those questions form the research root record of `gnomon`.
- **A reference does not transfer ownership.** A record of another field may name an instance, such as a contact profile naming the audiences that include a researcher. That reference leaves the mechanism of audiences with `ekthesis`, and the contact profile with its own owner.
- **A consumer defines no schema.** Under the decision on tool roles, `geonexus` keeps only the policy and the content of the consumer. Therefore, the project specification cannot remain a schema of the consumer.

## Options weighed

| Option | Benefit | Reason it is not taken alone |
| ------ | ------- | ---------------------------- |
| Each consumer keeps its own mechanisms | Each research vault adapts its schemas freely | Every vault restates the same schemas and checks, and the consumer defines schemas |
| `gnomon` provides the mechanisms, and consumers hold the instances | One owner for the schemas and the checks, beside the research records | Then, an exposition without research records depends on `gnomon` |
| One project specification, owned by a tool of its own | One record describes a project | The record joins the content of an inquiry, the choices of presentation and the identity of a repository; these three parts change for different reasons |
| `ekthesis` provides the glossary, the audience and the binding of a project; the questions and goals go to `gnomon`; the identity stays in `repository.yml` | Each part has the owner whose work needs it | A project is described by three records |

The present decision takes the last option.

## Consequences

- The schemas of the glossary, of the audience and of the binding of a project take the namespace `ekthesis`. They replace the schemas of `geonexus`, in the order of extraction set by the decision on tool roles. The checks of imports, references, conflicts, aliases and cycles move with them.
- The project specification of each standalone project migrates into the three records.
- The decisions of `geonexus` on [notations separate from glossaries](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/notations-separate-from-glossaries.md), [namespaced imports](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/namespaced-imports.md), [consumer-side glossary binding](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/consumer-side-glossary-binding.md), [context-dependent usage](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/context-dependent-usage.md), [audience-agnostic glossaries](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/audience-agnostic-glossaries.md), [audience knowledge by reference](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/audience-knowledge-by-reference.md), [audience subtypes](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/audience-subtypes.md) and [project specifications](https://github.com/esther-poniatowski/geonexus/blob/42d8a238991105b3c1640a69d5bfe27c8db703e0/docs/_decisions/project-specifications.md) supply the first statement of these mechanisms.
