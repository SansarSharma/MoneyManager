# File: notifications/base/update_listener.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class UpdateListener(ABC):
    """
    REQUIRES: none
    MODIFIES: none
    EFFECTS:  Interface for objects that react to data update events.
    """

    @abstractmethod
    def update(self, event: str, payload: Mapping[str, Any] | None = None) -> None:
        """
        REQUIRES: event is a short event key; payload is optional event data
        MODIFIES: implementer-defined
        EFFECTS:  Handles a data update notification.
        """
        raise NotImplementedError
