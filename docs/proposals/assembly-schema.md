---
tags:
  - proposal
index: "[Proposals](docs/proposals/_index.md)"
aliases:
  - Proposals for the assembly schema
---
# Proposals for the assembly schema

The goal [`assembly-schema`](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/TODO.md#L79), carried from `gnomon`, divides between the two tools. `ekthesis` receives the status `core` or `elaboration` of a component of an argument, the views that expand chosen components, and the check of the core route. The gaps of an assembly, its limits of validity, its deferred components and the query of its weakest link stay in `gnomon`.

## Status relative to one argument

The status `core` or `elaboration` of an idea belongs to the record of one exposition, never to the source of the idea. A unit takes part in several arguments, and one argument may answer a question stated by no research record. Then, the same unit may be core in one argument and an elaboration in another. A status recorded on the unit would therefore let one argument stand for all of them. The expositions that present a unit, with the status of the unit in each, are found by a query over their records.

**Literature.** None cited.

**Bears on.** [`assembly-schema`](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/TODO.md#L79), and the [record of an exposition](../adr/argument-record.md#^record), still without a status.

**Retired source.** `docs/design/2-architecture/reasoning-structure.md`, `docs/design/_backup/arguments-reasoning/argument-bundles.md` and `docs/design/_backup/schema-fields-base.md` of `gnomon`, at commit 9e138e2.

## Name of the status

The status carried from `gnomon` bears the name `elaboration`. The [registry](../../src/ekthesis/data/registries/relations.yml) also names a relation `elaboration`. The status and the relation state different facts. The relation states that one idea details another, in one of six forms. The status states that a view may leave an idea out, and present it only when the view expands the idea that it deepens. The two vary independently. An interpretation, an evidence or a condition can take the status without being the source of the relation. Conversely, the relation can join two core ideas, such as a subquestion and the question that it serves. The status and the relation occupy different fields of a record, so the shared name breaks no check. The cost is that a reader meets the word in two senses, and in a third with the class `elaboration` that the relation requires of the sources. ^status-name

The [scope of `gnomon`](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/adr/research-scope.md) names the status `core` or `elaboration`, and the researcher kept these names on 2026-11-11: the shared name breaks no check, and it keeps the name under which `gnomon` states the status. Three names of its own were weighed. The pair `core` and `expansion` would remove the second sense, since an expansion is presented only in a view that expands its target, as the [views](#^views) below state. The name `optional` states the absence from a view, but not the dependence on a target. The name `detail` repeats the description of the relation `elaboration` in the registry, and would bring back the confusion.

**Literature.** [mann1988], for the relation `elaboration`.

**Bears on.** [`assembly-schema`](https://github.com/esther-poniatowski/gnomon/blob/ac7816bf9c51630d5024d4c00d1c882a0df833f6/TODO.md#L79), and the [forms of an elaboration](../adr/argument-record.md#^elaboration-forms).

**Retired source.** The [term *elaboration*](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/argument-architecture-records.md#L143) in the argument architecture records of `geonexus`.

## Level, output and core route

A level of an exposition is the exposition itself or one of its parts, since the [record](../adr/argument-record.md#^record) holds no smaller group of ideas. A level states its object, often a question, and its output: the ideas that it delivers, named by their identifiers. The status of an idea is relative to the output of its own level. Thus, the same idea can be core in its part and an expansion relative to the output of the whole exposition. An expansion names the ideas that it deepens by its relations, so the expansions form a graph across levels and parts rather than one hierarchy. ^core-route

The core route of a level holds its core ideas. A core idea either belongs to the output of its level, or is the source of a relation whose target is a core idea and whose entry in the registry requires a class. Therefore, when the relation of an idea requires no class, as `background` does, the idea can be core only by belonging to the output. An expansion belongs to no output, and is the source of at least one relation toward an idea that it deepens. *(Inference: `geonexus` counted the relations of the grade "argument" in its vocabulary. Among the relations of the registry, those that require a class rest on the contents of their ideas, and stand closest to that grade.)*

The research side of the architecture records of `geonexus` is retired. `gnomon` computes the assembly of a level of an inquiry as a view, as its decision on the [assembly of a level](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/adr/assembly-of-a-level.md#^assembly-view) states. The level, its output and its core route above concern the presentation of an argument only.

**Literature.** None cited.

**Bears on.** The parts of the [record](../adr/argument-record.md#^record), still without an object, an output or a status.

**Retired source.** [Shape of the record](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/argument-architecture-records.md#L57-L85) and [elaboration and views](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/argument-architecture-records.md#L133-L135) in the argument architecture records of `geonexus`.

## Operation of a level

A level names its operation: the function that the level performs for its reader. Each operation names a relation of the registry, so the operation adds no vocabulary beside the registry. The moves of a genre order the operations of the parts, as the [order of the moves](order-of-ideas.md#^moves) proposes. The operations of `geonexus` map onto the registry as follows: ^operations

| Operation | Relation that the operation names |
| --- | --- |
| derives | `evidence`, from each premise to the derived claim |
| explains | `non-volitional-cause`, from the cause to the effect |
| qualifies | `condition` or `concession`, toward the qualified idea |
| specializes | `elaboration`, with the form generalization and specific *(inference)* |
| defines | `background`, from the definition to the idea that uses it |
| contrasts | `contrast`, between the two ideas |
| distinguishes | `contrast`, between the two ideas distinguished *(inference)* |
| classifies | `elaboration`, with the form set and member *(inference)* |
| interprets | `interpretation`, from the interpretation to the idea interpreted *(inference)* |
| clarifies | `elaboration`, with a form *(inference)* |
| illustrates | `elaboration`, with the form abstraction and instance |
| motivates | `solutionhood`, from the problem to its answer |
| poses | none: the posed question belongs to the output, and no relation of the registry joins an idea to the question that it raises (task [`raised-question`](../../TODO.md)) |
| identifies | none: the problem belongs to the output, and reaches its answer by `solutionhood` *(inference)* |
| models | none: the definition of the model belongs to the output *(inference)* |
| states | none: the stated idea belongs to the output itself |
| decides | none: the kind of a decision waits for the closed list of the kinds of a referenced idea, which the [kind of a referenced idea](../adr/argument-record.md#^referenced-kind) defers |
| synthesizes | none: a synthesis is a device, as the [syntheses](#^synthesis) below state |

The rows without a mark follow the mappings faithful to the vocabulary of `geonexus`. The rows marked *(inference)* name an operation whose relation in `geonexus` lacked a faithful counterpart in the registry. This note maps each of them by its own reading.

**Literature.** None cited.

**Bears on.** The parts of the [record](../adr/argument-record.md#^record), and the [registry of relations](../../src/ekthesis/data/registries/relations.yml).

**Retired source.** [Levels and operations](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/exposition-pilot-profile.md#L55-L110) in the exposition pilot profile of `geonexus`.

## Views

A view holds the core route of every level that it presents, and the expansions of every idea that it expands. Three rules govern a view: ^views

- **Expansion by target**: a view names the ideas whose expansions it presents. Thus, a poster can present one mechanism in detail, and the model only through its core route.
- **Complete targets**: an expansion enters a view only when every idea that it deepens is in that view.
- **Checks per view**: every check of the announcements runs on each view, since an idea left out of a view falsifies an announcement that forecasts it.

Therefore, a short artifact and a long artifact can share one record and differ by their views. In the pilot of `geonexus`, one record of a brief served three views. The live view folded the conditions, figures and grounds, the full view opened every element, and the view of a poster kept the core route and expanded chosen ideas only.

**Literature.** None cited.

**Bears on.** The [record](../adr/argument-record.md#^record), still without a view.

**Retired source.** [Elaboration and views](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/argument-architecture-records.md#L133-L141) in the argument architecture records, and [announcements, syntheses and views](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/exposition-pilot-profile.md#L125-L135) in the exposition pilot profile, both in `geonexus`.

## Announcements

An announcement is a device, in the sense of the [kinds of relation](../theory/exposition.md#^relation-kinds), that realizes the architecture of its level. The announcement forecasts each idea kept by the view, from the function of the idea and from its object. An announcement states the function of each idea, never its result, since the output already states the results. Nor does it describe the text, as "This part first discusses" would. When the relations order the ideas of a part, the part opens on an announcement after its message. The form of an announcement follows the structure of the ideas: ^announcements

- **Ordered ideas**: one sentence per idea, opening on "First", "Then" and "Finally", when the relations order the ideas: "First, the distortions produced by the nonlinearity of single neurons are derived. Then, the action of recurrence is derived for three distinct gains."
- **Purpose form**: a sentence opening on the goal of an idea, then naming its means: "To separate the effects of the two sources, each property of the mixture is crossed with its source."
- **Coordinate ideas**: an enumeration without ordinal connectors, since an order would assert a dependence absent between the ideas. For instance: "Two properties of the mixture are treated in parallel: the bias is assigned to its sources, and so is the emergence."

**Literature.** None cited.

**Bears on.** The [views](#^views), on each of which the announcements are checked.

**Retired source.** [Realization in prose](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/argument-architecture-records.md#L145-L153) in the argument architecture records of `geonexus`.

## Syntheses

A synthesis of an exposition adds no idea: it reformulates referenced units, under the [rule on syntheses](../adr/provenance-of-ideas.md#^syntheses). The argument architecture records of `geonexus` admitted a synthesis that supplies an output no other component supplies, such as a table crossing each property of a mixture with its source. That rule is retired. Content such as a crossing table is new, so it belongs to the source. In research, that content is the synthesis answer of `gnomon` to the question of the level, and the parts support that answer by `supports`, as the [parts of an answer](https://github.com/esther-poniatowski/gnomon/blob/6f82744f902cb65471f2a3d7736a8f3e029c4fcb/docs/adr/assembly-of-a-level.md#^parts-as-answers) state. The exposition presents that answer as a referenced idea. When a synthesis restates the output of its level, the synthesis stays a device. The check reports an authored source of a restatement or a summary, as the [consequences of the argument record](../adr/argument-record.md#consequences) state. ^synthesis

**Literature.** None cited.

**Bears on.** The [rule on syntheses](../adr/provenance-of-ideas.md#^syntheses).

**Retired source.** [Synthesis](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/argument-architecture-records.md#L155) in the argument architecture records of `geonexus`.

## Checks of an assembly

Five checks test the assembly of an exposition from its record and its views: ^assembly-checks

- **Core route**: every core idea belongs to the output of its level, or is the source of a relation that requires a class toward a core idea. The check reports any other core idea as an orphan.
- **Placed expansions**: every expansion is the source of at least one relation, and belongs to no output.
- **Complete targets**: every expansion in a view has every idea that it deepens in that view.
- **Output kind**: the output of a level holds an idea of the kind that its operation requires. This check waits for the closed list of the kinds of a referenced idea, which the [kind of a referenced idea](../adr/argument-record.md#^referenced-kind) defers to the first rule that reads them.
- **Resolved references**: every idea of an output, and every end of a relation, resolves. `ekthesis check` already reports a relation that names no idea of the record.

Two checks of `geonexus` are not carried. The rule on syntheses above replaces the check of a synthesis. The check of realization compared each relation between two components with a relation between their statements. In `ekthesis`, the relations join ideas only, never parts, so the check of realization has no relation to compare. *(Inference: a relation between parts would reopen that check.)* The core route absorbs the check of supplied output parts: an output here consists of ideas, and each idea of an output is core. *(Inference: the absorption follows from outputs named by their ideas.)* The [check by reconstruction](argument-specification.md#^reconstruction) runs on each view. That check begins with the operation, the object and the output of each level, and the reviewer confirms that the output resolves the object.

**Literature.** None cited.

**Bears on.** The command `ekthesis check`, and the [record](../adr/argument-record.md#^record).

**Retired source.** [Checks](https://github.com/esther-poniatowski/geonexus/blob/27218d855189b31d9472e5d5eeb9cd420da390f9/docs/_decisions/argument-architecture-records.md#L157-L170) in the argument architecture records of `geonexus`.

---
## Sources

Marks follow the [legend of reading marks](../../CONTRIBUTING.md#^reading-marks).

- [mann1988] ◐ [Mann & Thompson, "Rhetorical Structure Theory: toward a functional theory of text organization", *Text* 8(3), 243–281, 1988](https://doi.org/10.1515/text.1.1988.8.3.243); the relation of elaboration and its forms
