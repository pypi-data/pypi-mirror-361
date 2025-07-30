#!/usr/bin/env python3
"""Example showing HTTP operations in Deluge compatibility layer."""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from deluge_compat import run_deluge_script


def test_http_operations():
    """Test HTTP GET request simulation."""
    print("=== Testing HTTP Operations ===")

    script = """
    result = Map();

    // Simulate a simple GET request
    url = "https://api.github.com/users/octocat";
    response = getUrl(url);

    result.put("url", url);
    result.put("response_length", response.length());
    result.put("contains_login", response.contains("login"));

    info "HTTP request completed";

    return result;
    """

    try:
        result = run_deluge_script(script)
        print("HTTP result:", result)

        for key, value in result.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")


def test_invokeurl():
    """Test invokeurl block translation."""
    print("\n=== Testing invokeurl Block ===")

    # This is a simplified version - the translator would handle the full syntax
    script = """
    result = Map();

    // Simple invokeurl example (simplified)
    params = Map();
    params.put("url", "https://httpbin.org/get");
    params.put("type", "GET");

    response = _invokeurl(params);

    result.put("response_type", "string");
    result.put("has_response", response.length() > 0);

    return result;
    """

    try:
        result = run_deluge_script(script)
        print("invokeurl result:", result)

    except Exception as e:
        print(f"Error: {e}")


def test_encoding_functions():
    """Test encoding/decoding functions."""
    print("\n=== Testing Encoding Functions ===")

    script = """
    original = "Hello World!";
    result = Map();

    // Base64 encoding
    encoded = base64Encode(original);
    decoded = base64Decode(encoded);

    result.put("original", original);
    result.put("base64_encoded", encoded);
    result.put("base64_decoded", decoded);
    result.put("encoding_successful", original.equals(decoded));

    // URL encoding
    url_text = "hello world & test";
    url_encoded = encodeUrl(url_text);
    url_decoded = urlDecode(url_encoded);

    result.put("url_original", url_text);
    result.put("url_encoded", url_encoded);
    result.put("url_decoded", url_decoded);

    return result;
    """

    try:
        result = run_deluge_script(script)
        print("Encoding result:", result)

        for key, value in result.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_http_operations()
    test_invokeurl()
    test_encoding_functions()

    print("\n=== HTTP Tests Completed ===")
