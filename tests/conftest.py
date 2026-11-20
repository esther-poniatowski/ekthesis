"""Pytest configuration and shared fixtures for ekthesis tests."""

from pathlib import Path

import pytest

from test_ekthesis.pinned import PinnedFiles


@pytest.fixture(name="pinned", scope="session")
def fixture_pinned(tmp_path_factory: pytest.TempPathFactory) -> PinnedFiles:
    """Files of the dependencies at the commits that the configuration of Kleisis pins."""
    return PinnedFiles(tmp_path_factory.mktemp("pinned"))
