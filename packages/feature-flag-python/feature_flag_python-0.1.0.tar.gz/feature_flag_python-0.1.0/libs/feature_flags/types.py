"""Type definitions for feature flags."""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, TypeVar

T = TypeVar("T")


class ExperimentVariant(Enum):
    """Experiment variant types"""

    CONTROL = "control"
    TREATMENT = "treatment"


@dataclass
class FeatureFlagResponse:
    """Feature flag response data"""

    enabled: bool
    config: Optional[dict[str, Any]] = None


@dataclass
class ExperimentResponse:
    """Experiment response data"""

    id: str
    variant: str
    isEnabled: bool
    payload: Optional[dict[str, Any]] = None

    def get_payload_value(self, default: T = None) -> T:
        """Get the parsed payload value with type checking."""
        if not self.payload:
            return default
        try:
            payload = json.loads(self.payload) if isinstance(self.payload, str) else self.payload
            return payload.get("value", default)
        except (json.JSONDecodeError, AttributeError):
            return default
