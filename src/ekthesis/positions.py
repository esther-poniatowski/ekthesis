"""
Parsing of a YAML document together with its node tree, and the position of a field in that tree.

Functions
---------
parse(path) -> tuple
    Parse the document at `path`, and return its value and its node tree.
position(node, at) -> Position or None
    Where the node at a field path starts, or else its closest existing ancestor.
"""

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
