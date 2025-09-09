# File: notifications/base/data_update_publisher.py

from __future__ import annotations

from typing import Any, Iterable, List, Mapping, Optional

from notifications.base.update_listener import UpdateListener


class DataUpdatePublisher:
    """
    REQUIRES: none
    MODIFIES: _listeners
    EFFECTS:  Maintains a list of listeners and notifies them of events.
    """

    def __init__(self) -> None:
        self._listeners: List[UpdateListener] = []

    def attach(self, listener: UpdateListener) -> None:
        """
        REQUIRES: listener is a concrete UpdateListener
        MODIFIES: _listeners
        EFFECTS:  Registers the listener if not already attached.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)

    def detach(self, listener: UpdateListener) -> None:
        """
        REQUIRES: listener previously attached (else no-op)
        MODIFIES: _listeners
        EFFECTS:  Unregisters the listener.
        """
        try:
            self._listeners.remove(listener)
        except ValueError:
            pass

    def listeners(self) -> Iterable[UpdateListener]:
        """
        REQUIRES: none
        EFFECTS:  Returns an iterator over the current listeners.
        """
        return iter(self._listeners)

    def notify(self, event: str, payload: Optional[Mapping[str, Any]] = None) -> None:
        """
        REQUIRES: event is a short event key; payload optional
        MODIFIES: each listener via UpdateListener.update()
        EFFECTS:  Broadcasts the event to all listeners.
        """
        for l in list(self._listeners):
            try:
                l.update(event, payload or {})
            except Exception:
                # Fail-safe: a misbehaving listener should not break the publisher.
                continue
