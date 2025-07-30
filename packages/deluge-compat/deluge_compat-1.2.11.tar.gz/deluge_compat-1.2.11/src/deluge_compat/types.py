"""Deluge-compatible data types."""

import json
import re
from datetime import datetime
from typing import Any


class Map(dict):
    """Deluge Map type - a dictionary with Deluge-specific methods."""

    def put(self, key: Any, value: Any) -> None:
        """Add a key-value pair to the map."""
        self[key] = value

    def putAll(self, other_map: "Map") -> None:
        """Add all key-value pairs from another map."""
        self.update(other_map)

    def isEmpty(self) -> bool:
        """Check if the map is empty."""
        return len(self) == 0

    def size(self) -> int:
        """Get the size of the map."""
        return len(self)

    def containKey(self, key: Any) -> bool:
        """Check if the map contains a key."""
        return key in self

    def containValue(self, value: Any) -> bool:
        """Check if the map contains a value."""
        return value in self.values()

    def get(self, key: Any, default: Any = None) -> Any:
        """Get value by key, wrapping strings as DelugeStrings."""
        value = super().get(key, default)
        if isinstance(value, str) and not isinstance(value, DelugeString):
            return DelugeString(value)
        return value

    def keys(self) -> "List":  # type: ignore[override]
        """Get all keys as a Deluge List."""
        return List(super().keys())

    def getJSON(self, key: str) -> Any:
        """Get a value and treat it as JSON."""
        return self.get(key)

    def __add__(self, other: Any) -> "DelugeString":
        """Support Map + string concatenation by converting Map to JSON."""
        import json

        if isinstance(other, str):
            result = json.dumps(dict(self)) + other
            return DelugeString(result)
        return NotImplemented

    def __radd__(self, other: Any) -> "DelugeString":
        """Support string + Map concatenation by converting Map to JSON."""
        import json

        if isinstance(other, str):
            result = other + json.dumps(dict(self))
            return DelugeString(result)
        return NotImplemented


class List(list):
    """Deluge List type - a list with Deluge-specific methods."""

    def add(self, element: Any) -> None:
        """Add an element to the list."""
        self.append(element)

    def addAll(self, other_list: "List") -> None:
        """Add all elements from another list."""
        self.extend(other_list)

    def removeElement(self, element: Any) -> None:
        """Remove an element from the list."""
        if element in self:
            self.remove(element)

    def removeAll(self, remove_list: "List") -> None:
        """Remove all elements that are in remove_list."""
        for item in remove_list:
            while item in self:
                self.remove(item)

    def get(self, index: int) -> Any:
        """Get element at index."""
        if 0 <= index < len(self):
            return self[index]
        return None

    def size(self) -> int:
        """Get the size of the list."""
        return len(self)

    def isEmpty(self) -> bool:
        """Check if the list is empty."""
        return len(self) == 0

    def isempty(self) -> bool:
        """Alias for isEmpty."""
        return self.isEmpty()

    def clear(self) -> None:
        """Remove all elements."""
        super().clear()

    def sort(self, ascending: bool = True) -> None:  # type: ignore[override]
        """Sort the list."""
        super().sort(reverse=not ascending)

    def distinct(self) -> "List":
        """Return a new list with unique elements."""
        seen = set()
        result = List()
        for item in self:
            if item not in seen:
                seen.add(item)
                result.add(item)
        return result

    def intersect(self, other_list: "List") -> "List":
        """Return common elements between lists."""
        return List([item for item in self if item in other_list])

    def __iter__(self):
        """Iterate over list items, wrapping strings as DelugeStrings."""
        for item in super().__iter__():
            if isinstance(item, str) and not isinstance(item, DelugeString):
                yield DelugeString(item)
            else:
                yield item

    def sublist(self, start_index: int, end_index: int | None = None) -> "List":
        """Return a sublist."""
        if end_index is None:
            end_index = len(self)
        return List(self[start_index:end_index])

    def lastindexOf(self, element: Any) -> int:
        """Return the last index of an element."""
        try:
            return len(self) - 1 - self[::-1].index(element)
        except ValueError:
            return -1

    def indexOf(self, element: Any) -> int:
        """Return the first index of an element."""
        try:
            return self.index(element)
        except ValueError:
            return -1


class DelugeString(str):
    """Deluge String type with Deluge-specific methods."""

    def contains(self, substring: str) -> bool:
        """Check if string contains substring (case-sensitive)."""
        return substring in self

    def containsIgnoreCase(self, substring: str) -> bool:
        """Check if string contains substring (case-insensitive)."""
        return substring.lower() in self.lower()

    def startsWith(self, prefix: str) -> bool:
        """Check if string starts with prefix."""
        return self.startswith(prefix)

    def endsWith(self, suffix: str) -> bool:
        """Check if string ends with suffix."""
        return self.endswith(suffix)

    def remove(self, substring: str) -> "DelugeString":
        """Remove all occurrences of substring."""
        return DelugeString(self.replace(substring, ""))

    def removeFirstOccurence(self, substring: str) -> "DelugeString":
        """Remove first occurrence of substring."""
        return DelugeString(self.replace(substring, "", 1))

    def removeLastOccurence(self, substring: str) -> "DelugeString":
        """Remove last occurrence of substring."""
        idx = self.rfind(substring)
        if idx == -1:
            return DelugeString(self)
        return DelugeString(self[:idx] + self[idx + len(substring) :])

    def getSuffix(self, delimiter: str) -> "DelugeString":
        """Get substring after delimiter."""
        idx = self.find(delimiter)
        if idx == -1:
            return DelugeString("")
        return DelugeString(self[idx + len(delimiter) :])

    def getPrefix(self, delimiter: str) -> "DelugeString":
        """Get substring before delimiter."""
        idx = self.find(delimiter)
        if idx == -1:
            return DelugeString(self)
        return DelugeString(self[:idx])

    def toUpperCase(self) -> "DelugeString":
        """Convert to uppercase."""
        return DelugeString(self.upper())

    def toLowerCase(self) -> "DelugeString":
        """Convert to lowercase."""
        return DelugeString(self.lower())

    def getAlphaNumeric(self) -> "DelugeString":
        """Get only alphanumeric characters."""
        return DelugeString("".join(c for c in self if c.isalnum()))

    def getAlpha(self) -> "DelugeString":
        """Get only alphabetic characters."""
        return DelugeString("".join(c for c in self if c.isalpha()))

    def removeAllAlphaNumeric(self) -> "DelugeString":
        """Remove all alphanumeric characters."""
        return DelugeString("".join(c for c in self if not c.isalnum()))

    def removeAllAlpha(self) -> "DelugeString":
        """Remove all alphabetic characters."""
        return DelugeString("".join(c for c in self if not c.isalpha()))

    def length(self) -> int:
        """Get string length."""
        return len(self)

    def getOccurence(self, substring: str) -> int:
        """Count occurrences of substring."""
        return self.count(substring)

    def indexOf(self, substring: str) -> int:
        """Get index of first occurrence."""
        idx = self.find(substring)
        return idx if idx != -1 else -1

    def lastIndexOf(self, substring: str) -> int:
        """Get index of last occurrence."""
        idx = self.rfind(substring)
        return idx if idx != -1 else -1

    def substring(self, start: int, end: int | None = None) -> "DelugeString":
        """Get substring."""
        if end is None:
            return DelugeString(self[start:])
        return DelugeString(self[start:end])

    def subString(self, start: int, end: int | None = None) -> "DelugeString":
        """Alias for substring."""
        return self.substring(start, end)

    def subText(self, start: int, end: int | None = None) -> "DelugeString":
        """Alias for substring."""
        return self.substring(start, end)

    def equals(self, other: str) -> bool:
        """Case-sensitive equality check."""
        return str(self) == str(other)

    def equalsIgnoreCase(self, other: str) -> bool:
        """Case-insensitive equality check."""
        return self.lower() == other.lower()

    def matches(self, regex: str) -> bool:
        """Check if string matches regex pattern."""
        return bool(re.search(regex, self))

    def replaceAll(self, search: str, replace: str) -> "DelugeString":
        """Replace all occurrences."""
        return DelugeString(self.replace(search, replace))

    def replaceFirst(self, search: str, replace: str) -> "DelugeString":
        """Replace first occurrence."""
        return DelugeString(self.replace(search, replace, 1))

    def toList(self, separator: str = ",") -> List:
        """Split string into a List."""
        if separator == "":
            return List(list(self))
        return List(self.split(separator))

    def toMap(self) -> Map:
        """Parse string as JSON into a Map."""
        try:
            data = json.loads(self)
            if isinstance(data, dict):
                result = _convert_json_to_deluge_types(data)
                if isinstance(result, Map):
                    return result
                else:
                    raise ValueError("Conversion did not produce a Map")
            else:
                raise ValueError("String does not represent a JSON object")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

    def toDate(self) -> datetime:
        """Parse string as date."""
        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y",
            "%m/%d/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(self, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date: {self}")

    def toTime(self) -> datetime:
        """Alias for toDate."""
        return self.toDate()

    def executeXPath(self, selection: str) -> str:
        """Execute XPath on XML/JSON string."""
        # Simplified implementation - would need proper XML/JSON parsing
        return str(self)

    def toXML(self) -> str:
        """Convert to XML format."""
        return str(self)

    def toLong(self) -> int:
        """Convert to integer."""
        try:
            if self.startswith("0x") or self.startswith("0X"):
                return int(self, 16)
            return int(self)
        except ValueError as e:
            raise ValueError(f"Cannot convert to long: {self}") from e

    def toXmlList(self) -> List:
        """Convert XML to List."""
        return List([str(self)])

    def getJSON(self, key: str | None = None) -> Map | Any:
        """Parse string as JSON and optionally get a specific key."""
        parsed_json = self.toMap()
        if key is None:
            return parsed_json
        return parsed_json.get(key)

    def toJSONList(self) -> List:
        """Parse string as JSON array into List."""
        try:
            data = json.loads(self)
            if isinstance(data, list):
                result = _convert_json_to_deluge_types(data)
                if isinstance(result, List):
                    return result
                else:
                    raise ValueError("Conversion did not produce a List")
            else:
                raise ValueError("String does not represent a JSON array")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

    def leftPad(self, pad_char: str, length: int) -> "DelugeString":
        """Pad string on the left."""
        return DelugeString(self.rjust(length, pad_char))

    def rightPad(self, pad_char: str, length: int) -> "DelugeString":
        """Pad string on the right."""
        return DelugeString(self.ljust(length, pad_char))

    def trim(self) -> "DelugeString":
        """Remove whitespace from both ends."""
        return DelugeString(self.strip())


def deluge_string(s: str) -> DelugeString:
    """Convert a regular string to a Deluge string."""
    return DelugeString(s)


def _convert_json_to_deluge_types(obj: Any) -> Map | List | DelugeString | Any:
    """Recursively convert JSON objects to Deluge types."""
    if isinstance(obj, dict):
        result = Map()
        for key, value in obj.items():
            result[key] = _convert_json_to_deluge_types(value)
        return result
    elif isinstance(obj, list):
        result = List()
        for item in obj:
            result.append(_convert_json_to_deluge_types(item))
        return result
    elif isinstance(obj, str):
        return DelugeString(obj)
    else:
        return obj
