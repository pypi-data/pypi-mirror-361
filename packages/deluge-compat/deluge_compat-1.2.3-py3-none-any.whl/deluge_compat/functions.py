"""Built-in Deluge functions."""

import base64
import math
import random
import urllib.parse
from typing import Any

import requests

from .types import DelugeString, List, Map, deluge_string


def getUrl(url: str, simple: bool = True, headers: dict[str, str] | None = None) -> str | Map:
    """Perform a GET request to URL."""
    try:
        response = requests.get(url, headers=headers or {})
        if simple:
            return deluge_string(response.text)
        else:
            return Map(
                {
                    "status_code": response.status_code,
                    "text": response.text,
                    "headers": dict(response.headers),
                }
            )
    except Exception as e:
        if simple:
            return deluge_string("")
        else:
            return Map({"error": str(e)})


def postUrl(
    url: str,
    body: Map | None = None,
    headers: Map | None = None,
    simple: bool = True,
) -> str | Map:
    """Perform a POST request to URL."""
    try:
        post_headers = dict(headers) if headers else {}
        post_data = dict(body) if body else {}

        response = requests.post(url, json=post_data, headers=post_headers)
        if simple:
            return deluge_string(response.text)
        else:
            return Map(
                {
                    "status_code": response.status_code,
                    "text": response.text,
                    "headers": dict(response.headers),
                }
            )
    except Exception as e:
        if simple:
            return deluge_string("")
        else:
            return Map({"error": str(e)})


def encodeUrl(url: str) -> DelugeString:
    """URL encode a string."""
    return deluge_string(urllib.parse.quote(url))


def urlEncode(url: str) -> DelugeString:
    """Alias for encodeUrl."""
    return encodeUrl(url)


def urlDecode(url: str) -> DelugeString:
    """URL decode a string."""
    return deluge_string(urllib.parse.unquote(url))


def base64Encode(text: str) -> DelugeString:
    """Base64 encode a string."""
    encoded_bytes = base64.b64encode(text.encode("utf-8"))
    return deluge_string(encoded_bytes.decode("utf-8"))


def base64Decode(text: str) -> DelugeString:
    """Base64 decode a string."""
    try:
        decoded_bytes = base64.b64decode(text.encode("utf-8"))
        return deluge_string(decoded_bytes.decode("utf-8"))
    except Exception:
        return deluge_string("")


def aesEncode(key: str, text: str) -> DelugeString:
    """AES encrypt text (simplified implementation)."""
    # This is a placeholder - real AES encryption would require cryptography library
    import hashlib

    hash_key = hashlib.md5(key.encode()).hexdigest()
    # Simple XOR-based "encryption" for demo purposes
    result = ""
    for i, char in enumerate(text):
        result += chr(ord(char) ^ ord(hash_key[i % len(hash_key)]))
    return deluge_string(base64.b64encode(result.encode()).decode())


def aesDecode(key: str, encrypted_text: str) -> DelugeString:
    """AES decrypt text (simplified implementation)."""
    try:
        import hashlib

        hash_key = hashlib.md5(key.encode()).hexdigest()
        decoded = base64.b64decode(encrypted_text.encode()).decode()
        result = ""
        for i, char in enumerate(decoded):
            result += chr(ord(char) ^ ord(hash_key[i % len(hash_key)]))
        return deluge_string(result)
    except Exception:
        return deluge_string("")


def abs_func(number: int | float) -> int | float:
    """Absolute value of a number."""
    return abs(number)


def cos_func(number: int | float) -> float:
    """Cosine of an angle."""
    return math.cos(number)


def sin_func(number: int | float) -> float:
    """Sine of an angle."""
    return math.sin(number)


def tan_func(number: int | float) -> float:
    """Tangent of an angle."""
    return math.tan(number)


def log_func(number: int | float) -> float:
    """Natural logarithm."""
    return math.log(number)


def min_func(a: int | float, b: int | float) -> int | float:
    """Minimum of two numbers."""
    return min(a, b)


def max_func(a: int | float, b: int | float) -> int | float:
    """Maximum of two numbers."""
    return max(a, b)


def exp_func(number: int | float) -> float:
    """Exponential function (e^x)."""
    return math.exp(number)


def power_func(base: int | float, exponent: int | float) -> int | float:
    """Power function."""
    return pow(base, exponent)


def round_func(number: float, decimals: int = 0) -> float:
    """Round a number to specified decimal places."""
    return round(number, decimals)


def sqrt_func(number: int | float) -> float:
    """Square root."""
    return math.sqrt(number)


def toDecimal(number: int) -> float:
    """Convert integer to decimal."""
    return float(number)


def toHex(number: int) -> str:
    """Convert integer to hexadecimal."""
    return hex(number)


def ceil_func(number: float) -> int:
    """Ceiling function."""
    return math.ceil(number)


def floor_func(number: float) -> int:
    """Floor function."""
    return math.floor(number)


def randomNumber(max_value: int = 2000000000, min_value: int = 0) -> int:
    """Generate a random number."""
    return random.randint(min_value, max_value - 1)


def info(*args) -> None:
    """Log information (equivalent to Deluge's info statement)."""
    print("INFO:", *args)


def sendemail(*args, **kwargs) -> Map:
    """Mock email sending function compatible with Deluge syntax."""
    # Log the email details for debugging/testing
    email_data = Map()
    email_data.put("status", "email_sent")
    email_data.put("from", kwargs.get("from", ""))
    email_data.put("to", kwargs.get("to", ""))
    email_data.put("subject", kwargs.get("subject", ""))
    email_data.put("message", kwargs.get("message", ""))

    # Print email details in debug mode
    if kwargs.get("debug", False):
        print(f"[MOCK EMAIL] From: {email_data.get('from')}")
        print(f"[MOCK EMAIL] To: {email_data.get('to')}")
        print(f"[MOCK EMAIL] Subject: {email_data.get('subject')}")
        print(f"[MOCK EMAIL] Message: {email_data.get('message')}")

    return email_data


# Create alias for Deluge compatibility
sendmail = sendemail


def sendsms(*args, **kwargs) -> Map:
    """Placeholder for sending SMS."""
    return Map({"status": "sms_sent"})


def pushNotification(*args, **kwargs) -> Map:
    """Placeholder for push notification."""
    return Map({"status": "notification_sent"})


def Collection() -> Map:
    """Create a new Collection (which can hold List or Map)."""
    return Map()


def ifnull(value: Any, default: Any) -> Any:
    """Return default if value is None/null."""
    return default if value is None else value


def replaceAll(text: str, search: str, replace: str) -> DelugeString:
    """Replace all occurrences in string."""
    return deluge_string(text.replace(search, replace))


# Create aliases for math functions to match Deluge naming
BUILTIN_FUNCTIONS = {
    "getUrl": getUrl,
    "postUrl": postUrl,
    "encodeUrl": encodeUrl,
    "urlEncode": urlEncode,
    "urlDecode": urlDecode,
    "base64Encode": base64Encode,
    "base64Decode": base64Decode,
    "aesEncode": aesEncode,
    "aesDecode": aesDecode,
    "abs": abs_func,
    "cos": cos_func,
    "sin": sin_func,
    "tan": tan_func,
    "log": log_func,
    "min": min_func,
    "max": max_func,
    "exp": exp_func,
    "power": power_func,
    "round": round_func,
    "sqrt": sqrt_func,
    "toDecimal": toDecimal,
    "toHex": toHex,
    "ceil": ceil_func,
    "floor": floor_func,
    "randomNumber": randomNumber,
    "info": info,
    "sendemail": sendemail,
    "sendmail": sendmail,
    "sendsms": sendsms,
    "pushNotification": pushNotification,
    "Collection": Collection,
    "Map": Map,
    "List": List,
    "ifnull": ifnull,
    "replaceAll": replaceAll,
}
