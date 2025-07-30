"""Zoho SalesIQ compatibility module for deluge-compat."""

from .core import Message, Visitor
from .functions import visitorsession_get, visitorsession_set
from .mocks import APIMockSource, MessageMockSource, MockManager, VisitorMockSource

__all__ = [
    "Visitor",
    "Message",
    "visitorsession_get",
    "visitorsession_set",
    "MockManager",
    "VisitorMockSource",
    "MessageMockSource",
    "APIMockSource",
]
