"""
Entry point for the `ekthesis` package, invoked as a module.

Usage
-----
To launch the command-line interface, execute::

    python -m ekthesis


See Also
--------
ekthesis.cli: Module implementing the application's command-line interface.
"""

from .cli import app

app()
