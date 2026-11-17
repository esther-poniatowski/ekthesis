"""
Parsing of a YAML document together with its node tree, and the position of a field in that tree.

Functions
---------
parse(path) -> tuple
    Parse the document at `path`, and return its value and its node tree.
position(node, at) -> Position or None
    Where the node at a field path starts, or else its closest existing ancestor.
repeated_keys(node) -> Iterator
    Each key that a mapping of the tree repeats, with its field path and its two key nodes.
"""

from collections.abc import Iterator

from pathlib import Path

import yaml

from .findings import Position
from .layout import FieldPath


def parse(path: Path) -> tuple[object, yaml.Node | None]:
    """Parse the document at `path` as `yaml.safe_load` does, and return its node tree as well."""
    loader = yaml.SafeLoader(path.read_text(encoding="utf-8"))
    try:
        node = loader.get_single_node()
        return (loader.construct_document(node) if node is not None else None), node
    finally:
        loader.dispose()


def position(node: yaml.Node | None, at: FieldPath) -> Position | None:
    """
    Return where the node at `at` starts in the tree `node`, or else its closest existing ancestor.

    A key is matched by its text as written, and the last of two equal keys is kept, as the
    loader keeps it. When the path leaves the tree, the last node that it reaches is located, since
    the absence of a node is detected in its parent. The root, the whole document, yields `None`.
    """
    if node is None:
        return None
    current, depth = node, 0
    for segment in at.segments:
        child = _child(current, segment)
        if child is None:
            break
        current, depth = child, depth + 1
    if not depth:
        return None
    return Position(current.start_mark.line + 1, current.start_mark.column + 1)


def _child(node: yaml.Node, segment: str | int) -> yaml.Node | None:
    """Return the child of `node` at `segment`, or `None` when `node` holds no such child."""
    if isinstance(node, yaml.SequenceNode) and isinstance(segment, int):
        return node.value[segment] if 0 <= segment < len(node.value) else None
    if isinstance(node, yaml.MappingNode):
        values = [
            value
            for key, value in node.value
            if isinstance(key, yaml.ScalarNode) and key.value == str(segment)
        ]
        return values[-1] if values else None
    return None


def repeated_keys(node: yaml.Node | None) -> Iterator[tuple[FieldPath, yaml.Node, yaml.Node]]:
    r"""
    Yield each key that a mapping of the tree `node` repeats, in the order of the document.

    A YAML parser keeps the value of the last of two equal keys and drops the earlier one, so a
    repeated key loses a value without an error. Each item holds the field path of the key, the
    node of its earlier occurrence, and the node of the repeated occurrence.

    Examples
    --------
    >>> tree = yaml.compose("a: 1\nb: {c: 2, c: 3}\na: 4\n")
    >>> [(str(at), later.start_mark.line + 1) for at, _, later in repeated_keys(tree)]
    [('b.c', 2), ('a', 3)]
    """
    yield from _repeated(node, FieldPath())


def _repeated(
    node: yaml.Node | None, at: FieldPath
) -> Iterator[tuple[FieldPath, yaml.Node, yaml.Node]]:
    """Yield the repeated keys of `node` and of its descendants, `at` being the path of `node`."""
    if isinstance(node, yaml.SequenceNode):
        for index, item in enumerate(node.value):
            yield from _repeated(item, at.child(index))
    elif isinstance(node, yaml.MappingNode):
        seen: dict[str, yaml.Node] = {}
        for key, value in node.value:
            if isinstance(key, yaml.ScalarNode):
                yield from _repeated(value, at.child(key.value))
                if key.value in seen:
                    yield at.child(key.value), seen[key.value], key
                else:
                    seen[key.value] = key
            else:
                yield from _repeated(value, at)
