"""Zoho namespace objects for proper dot notation access."""

from typing import Any

from .salesiq.functions import visitorsession_get, visitorsession_set
from .types import deluge_string


class VisitorSessionNamespace:
    """Namespace for zoho.salesiq.visitorsession functions."""

    def get(self, portal: str, key: str, connection: str) -> Any:
        """Get visitor session data."""
        return visitorsession_get(portal, key, connection)

    def set(self, portal: str, data: Any, connection: str) -> Any:
        """Set visitor session data."""
        return visitorsession_set(portal, data, connection)


class SalesIQNamespace:
    """Namespace for zoho.salesiq functions."""

    def __init__(self):
        self.visitorsession = VisitorSessionNamespace()


class ZohoNamespace:
    """Main Zoho namespace object."""

    def __init__(self):
        self.salesiq = SalesIQNamespace()
        self.adminuserid = deluge_string("admin@example.com")
