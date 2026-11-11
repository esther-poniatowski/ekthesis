"""
Resolution of a Markdown link to the source of an idea.

A link `[text](path#anchor)` resolves when `path`, relative to the directory of the record, names a
file, and when that file holds the anchor, if any. Two anchors are recognized, as in Obsidian:

- a block anchor `#^id`, declared by the token `^id` at the end of a line;
- a heading anchor `#Heading`, matching the text of a heading; in a nested form `#A#B`, the last
  heading is matched.

Functions
---------
resolve_link(link, base) -> str or None
    Explain why a link does not resolve, or return `None` when it does.
"""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

_LINK = re.compile(r"^\[[^\]]+\]\((?P<target>[^()\s]+)\)$")
_HEADING = re.compile(r"^#{1,6}\s+(?P<text>.+?)\s*#*\s*$", re.MULTILINE)


def resolve_link(link: str, base: Path) -> str | None:
    """
    Explain why `link` does not resolve from the directory `base`, or return `None` if it does.

    Parameters
    ----------
    link : str
        Markdown link, written `[text](path#anchor)`.
    base : Path
        Directory against which a relative path is resolved.

    Returns
    -------
    str or None
        Reason for which the link does not resolve, or `None`.

    Examples
    --------
    >>> resolve_link("[note](https://example.org/note.md)", Path("."))
    'the link https://example.org/note.md names no local file'
    """
    match = _LINK.match(link)
    if match is None:
        return f"{link} is no Markdown link"
    target = match["target"]
    if urlsplit(target).scheme:
        return f"the link {target} names no local file"
    location, _, anchor = target.partition("#")
    path = (base / unquote(location)).resolve()
    if not location or not path.is_file():
        return f"the link {target} names no file"
    if not anchor:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return f"the file {location} cannot be read: {error}"
    anchor = unquote(anchor)
    if anchor.startswith("^"):
        found = re.search(rf"(^|\s){re.escape(anchor)}\s*$", text, re.MULTILINE) is not None
        kind = "block anchor"
    else:
        heading = anchor.split("#")[-1].strip().casefold()
        found = any(match["text"].casefold() == heading for match in _HEADING.finditer(text))
        kind = "heading"
    return None if found else f"the file {location} holds no {kind} {anchor}"
