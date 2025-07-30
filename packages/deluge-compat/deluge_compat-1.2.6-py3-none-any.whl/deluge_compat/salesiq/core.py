"""Core SalesIQ objects for Zoho Deluge compatibility."""

from typing import Any

from ..types import deluge_string


class Visitor:
    """Zoho SalesIQ Visitor object implementation."""

    def __init__(self, data: dict[str, Any] | None = None):
        """Initialize visitor with mock or real data."""
        self._data = data or self._get_default_data()

    def _get_default_data(self) -> dict[str, Any]:
        """Return default visitor data structure."""
        return {
            # Basic information
            "name": "",
            "email": "",
            "phone": "",
            "active_conversation_id": "",
            # Visitor context
            "channel": "Website",
            "browser": "Unknown",
            "country": "",
            "country_code": "",
            "time_zone": "",
            "language": "en",
            "os": "Unknown",
            "city": "",
            "state": "",
            # Page and navigation
            "current_page_url": "",
            "current_page_title": "",
            "landing_page_url": "",
            "landing_page_title": "",
            "previous_page_url": "",
            # Campaign tracking
            "campaign_content": "",
            "campaign_medium": "",
            "campaign_source": "",
            "referer": "",
            # Additional metadata
            "ip": "",
            "lead_score": "0",
            "number_of_past_chats": "0",
            "number_of_past_visits": "0",
            "last_visit_time": "",
            # Company information
            "company_name": "",
            "company_employees": "",
            # Unique identifiers
            "visitid": "",
            "uuid": "",
            "department_id": "",
            # Custom fields
            "custom_info": {},
        }

    def getJSON(self, key: str) -> Any:
        """Get a value from visitor data (SalesIQ method)."""
        value = self._data.get(key)
        # Convert strings to deluge strings for compatibility
        if isinstance(value, str):
            return deluge_string(value)
        return value

    def get(self, key: str) -> Any:
        """Get a value from visitor data (alternative method)."""
        return self.getJSON(key)

    def set(self, key: str, value: Any) -> None:
        """Set a value in visitor data."""
        self._data[key] = value

    def update(self, data: dict[str, Any]) -> None:
        """Update multiple visitor fields at once."""
        self._data.update(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert visitor object to dictionary."""
        return self._data.copy()

    def __repr__(self) -> str:
        """String representation of visitor."""
        return f"Visitor(email={self._data.get('email')}, name={self._data.get('name')})"


class Message:
    """Zoho SalesIQ Message object implementation."""

    def __init__(self, text: str = "", data: dict[str, Any] | None = None):
        """Initialize message with text and optional additional data."""
        self._data = data or {}
        self._data["text"] = text

    def get(self, key: str) -> Any:
        """Get a value from message data."""
        value = self._data.get(key)
        # Convert strings to deluge strings for compatibility
        if isinstance(value, str):
            return deluge_string(value)
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a value in message data."""
        self._data[key] = value

    def getText(self) -> str:
        """Get message text (convenience method)."""
        return self.get("text")

    def setText(self, text: str) -> None:
        """Set message text (convenience method)."""
        self.set("text", text)

    def to_dict(self) -> dict[str, Any]:
        """Convert message object to dictionary."""
        return self._data.copy()

    def __repr__(self) -> str:
        """String representation of message."""
        return f"Message(text={self._data.get('text')})"
