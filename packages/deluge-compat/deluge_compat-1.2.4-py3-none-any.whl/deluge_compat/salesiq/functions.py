"""SalesIQ-specific functions for Zoho Deluge compatibility."""

from typing import Any

from ..types import Map

# Global session storage - in production this could be Redis or similar
_session_storage: dict[str, dict[str, Any]] = {}


def visitorsession_get(portal: str, key: str, connection: str) -> Map:
    """
    Fetch value temporarily stored by visitorsession.set task.

    Args:
        portal: Portal name (e.g., "sales1.examplelab")
        key: Key to retrieve from session
        connection: Connection name (e.g., "sales_iq")

    Returns:
        Map containing the stored data or empty Map if not found
    """
    session_key = f"{portal}:{connection}"
    session_data = _session_storage.get(session_key, {})

    if key in session_data:
        # Return Map with the key and its value
        result = Map()
        result.put("data", Map({key: session_data[key]}))
        result.put(f"{key}_response", session_data[key])
        return result
    else:
        # Return empty Map when key not found
        return Map()


def visitorsession_set(portal: str, data: Map, connection: str) -> Map:
    """
    Temporarily store values during a chat conversation.

    Args:
        portal: Portal name (e.g., "sales1.examplelab")
        data: Map containing key-value pairs to store
        connection: Connection name (e.g., "sales_iq")

    Returns:
        Map with status of the operation
    """
    session_key = f"{portal}:{connection}"

    # Initialize session if it doesn't exist
    if session_key not in _session_storage:
        _session_storage[session_key] = {}

    # Store all key-value pairs from the data Map
    for key, value in data.items():
        _session_storage[session_key][key] = value

    # Return success response
    response = Map()
    response.put("status", "success")
    response.put("stored_keys", list(data.keys()))
    return response


def clear_visitor_session(portal: str, connection: str) -> None:
    """
    Clear all session data for a specific portal/connection.

    Args:
        portal: Portal name
        connection: Connection name
    """
    session_key = f"{portal}:{connection}"
    if session_key in _session_storage:
        del _session_storage[session_key]


def get_all_sessions() -> dict[str, dict[str, Any]]:
    """Get all active sessions (for debugging/testing)."""
    return _session_storage.copy()
