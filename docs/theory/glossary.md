---
tags:
  - theory
index: "[Theory](docs/theory/_index.md)"
aliases:
  - Glossary
  - Names and symbols
  - Glossary (theory)
---
# Glossary

> [!QUESTION] Goal: what does a glossary hold, and how does it name the concepts of a project without changing them?

A **name** is a word or a phrase that designates a concept. A concept keeps one meaning, whereas its names vary with the audience and the context of a text. The glossary holds the names of the concepts of one project. A glossary belongs to expression: it changes how a content is presented, never the content. The concept and its symbols belong to research, and `gnomon` records them. ^names

## Entries of a glossary

A **glossary** holds the names of the concepts of one project: for each concept, its label, its variants, its alternative forms with the contexts in which each is admitted, and its names in other frameworks. A form forbidden for some audiences keeps its replacement, its reason and the audiences concerned. A glossary defines no concept: each entry designates one concept and points to it. An entry may restate the meaning of its concept for the audience of the glossary, in a gloss that adds no content. ^glossary

The Simple Knowledge Organization System separates a concept from its lexical labels in the same way, with a preferred label and alternative labels, and relates two concepts by the relation `broader` [skos2009]. The glossary differs on one point. The lexical labels of that system belong to the concept itself, whereas a glossary belongs to one project, so two projects can name one concept differently without changing it.

**Two names designate one concept only when they carry the same meaning.** Two names of one referent can differ in sense, as "the morning star" and "the evening star" do [frege1892a]. Under a proposal of this method, a glossary admits two forms for one concept only when they carry the same meaning in the contexts listed. A name that carries a different meaning designates a different concept, which receives its own record, with a confusion entry that states the distinction.

## Distinctions

- **A glossary holds forms, and a text in those forms presents the concepts.** The glossary is authored, so it is no generated view of the concepts. The glossary maps concepts to the forms that express them in one project. A text written in those forms presents the concepts without changing them, as an [exposition](exposition.md) does.
- **A forbidden form is a fact about a name, not about a meaning.** A form may be forbidden for one audience and admitted for another, while the concept stays the same. The prohibition therefore belongs to the glossary, never to the concept.
- **A name differs from a printed symbol.** A name belongs to the glossary of a project. A symbol belongs to the notation of `gnomon`, and an artifact may change only its printed form, under the [renaming of a symbol for a venue](../adr/symbol-renaming.md).

---
## Sources

> [!NOTE] Status of the claims
> - **Established:** the separation of concepts from labels, and the distinction between sense and reference, as cited.
> - **Proposals:**
> 	- the glossary as a record of one project, apart from the concept;
> 	- the rule that two forms designate one concept only when they carry the same meaning in the contexts listed.

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [frege1892a] ◐ Frege, "Über Sinn und Bedeutung", *Zeitschrift für Philosophie und philosophische Kritik* (N.F.) 100(1), 25–50, 1892; sense and reference
- [skos2009] ◐ [Miles & Bechhofer (eds.), *SKOS Simple Knowledge Organization System Reference*, W3C Recommendation, 18 August 2009](https://www.w3.org/TR/skos-reference/); preferred and alternative labels, and the relation `broader`, checked through the namespace document
