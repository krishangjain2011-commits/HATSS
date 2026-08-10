"""Tests for secure runtime configuration defaults."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_debug_mode() -> None:
    """Production must refuse an unsafe debug configuration."""
    with pytest.raises(ValidationError, match="HATSS_DEBUG must be false"):
        Settings(environment="production", debug=True)


def test_default_cors_configuration_is_not_a_wildcard() -> None:
    """The foundation must only trust explicitly configured browser origins."""
    assert "*" not in Settings().cors_origin_strings
