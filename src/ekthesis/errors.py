"""
Errors raised by `ekthesis` when its own resources are defective.

A defect of a checked record is reported as a finding, not raised.

Classes
-------
ResourceError
    A packaged or supplied schema or registry cannot be read.
"""


class ResourceError(Exception):
    """A schema or a registry cannot be read, or breaks the form that the check expects."""
