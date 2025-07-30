"""Test Deluge built-in functions."""

import base64
import urllib.parse
from unittest.mock import Mock, patch

from deluge_compat.functions import (
    BUILTIN_FUNCTIONS,
    abs_func,
    aesDecode,
    aesEncode,
    base64Decode,
    base64Encode,
    ceil_func,
    cos_func,
    encodeUrl,
    exp_func,
    floor_func,
    getUrl,
    ifnull,
    info,
    log_func,
    max_func,
    min_func,
    postUrl,
    power_func,
    randomNumber,
    replaceAll,
    round_func,
    sin_func,
    sqrt_func,
    tan_func,
    toDecimal,
    toHex,
    urlDecode,
    urlEncode,
)
from deluge_compat.types import Map


class TestHttpFunctions:
    """Test HTTP-related functions."""

    @patch("requests.get")
    def test_getUrl_simple(self, mock_get):
        """Test getUrl with simple response."""
        mock_response = Mock()
        mock_response.text = "Hello World"
        mock_get.return_value = mock_response

        result = getUrl("http://example.com")
        assert str(result) == "Hello World"
        assert result.__class__.__name__ == "DelugeString"

    @patch("requests.get")
    def test_getUrl_complex(self, mock_get):
        """Test getUrl with complex response."""
        mock_response = Mock()
        mock_response.text = "Response body"
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_get.return_value = mock_response

        result = getUrl("http://example.com", simple=False)
        assert isinstance(result, Map)
        assert result.get("status_code") == 200
        assert result.get("text") == "Response body"

    @patch("requests.post")
    def test_postUrl(self, mock_post):
        """Test postUrl function."""
        mock_response = Mock()
        mock_response.text = "Posted successfully"
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        body = Map()
        body.put("key", "value")

        result = postUrl("http://example.com", body=body)
        assert str(result) == "Posted successfully"

        # Verify the call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://example.com"
        assert call_args[1]["json"] == {"key": "value"}


class TestEncodingFunctions:
    """Test encoding and decoding functions."""

    def test_base64_encode_decode(self):
        """Test base64 encoding and decoding."""
        original = "Hello World"
        encoded = base64Encode(original)
        decoded = base64Decode(str(encoded))

        assert str(decoded) == original
        assert encoded.__class__.__name__ == "DelugeString"
        assert decoded.__class__.__name__ == "DelugeString"

        # Test with actual base64
        expected = base64.b64encode(original.encode()).decode()
        assert str(encoded) == expected

    def test_url_encode_decode(self):
        """Test URL encoding and decoding."""
        original = "hello world & test"
        encoded = encodeUrl(original)
        decoded = urlDecode(str(encoded))

        assert str(decoded) == original
        assert encoded.__class__.__name__ == "DelugeString"

        # Test with actual URL encoding
        expected = urllib.parse.quote(original)
        assert str(encoded) == expected

        # Test alias
        encoded2 = urlEncode(original)
        assert str(encoded) == str(encoded2)

    def test_aes_encode_decode(self):
        """Test AES encoding and decoding (simplified implementation)."""
        key = "secret_key"
        original = "Hello World"

        encoded = aesEncode(key, original)
        decoded = aesDecode(key, str(encoded))

        assert str(decoded) == original
        assert encoded.__class__.__name__ == "DelugeString"
        assert decoded.__class__.__name__ == "DelugeString"

        # Test with wrong key
        wrong_decoded = aesDecode("wrong_key", str(encoded))
        assert str(wrong_decoded) != original


class TestMathFunctions:
    """Test mathematical functions."""

    def test_basic_math(self):
        """Test basic mathematical operations."""
        assert abs_func(-5) == 5
        assert abs_func(5) == 5

        assert min_func(3, 7) == 3
        assert max_func(3, 7) == 7

        assert power_func(2, 3) == 8
        assert power_func(5, 2) == 25

    def test_trigonometric_functions(self):
        """Test trigonometric functions."""
        import math

        # Test with pi/4 (45 degrees)
        angle = math.pi / 4

        assert abs(cos_func(angle) - math.cos(angle)) < 1e-10
        assert abs(sin_func(angle) - math.sin(angle)) < 1e-10
        assert abs(tan_func(angle) - math.tan(angle)) < 1e-10

    def test_logarithmic_functions(self):
        """Test logarithmic and exponential functions."""
        import math

        assert abs(log_func(math.e) - 1.0) < 1e-10
        assert abs(exp_func(1) - math.e) < 1e-10
        assert abs(sqrt_func(9) - 3.0) < 1e-10

    def test_rounding_functions(self):
        """Test rounding functions."""
        assert round_func(3.14159, 2) == 3.14
        assert round_func(3.7) == 4

        assert ceil_func(3.2) == 4
        assert ceil_func(3.0) == 3

        assert floor_func(3.8) == 3
        assert floor_func(3.0) == 3

    def test_conversion_functions(self):
        """Test number conversion functions."""
        assert toDecimal(5) == 5.0
        assert isinstance(toDecimal(5), float)

        assert toHex(15) == "0xf"
        assert toHex(255) == "0xff"

    def test_random_number(self):
        """Test random number generation."""
        # Test default range
        for _ in range(10):
            num = randomNumber()
            assert 0 <= num < 2000000000

        # Test custom range
        for _ in range(10):
            num = randomNumber(10, 5)
            assert 5 <= num < 10


class TestUtilityFunctions:
    """Test utility functions."""

    def test_info_function(self, capsys):
        """Test info logging function."""
        info("Test message", 123, "another arg")
        captured = capsys.readouterr()
        assert "INFO: Test message 123 another arg" in captured.out

    def test_ifnull_function(self):
        """Test ifnull function."""
        assert ifnull(None, "default") == "default"
        assert ifnull("value", "default") == "value"
        assert ifnull(0, "default") == 0
        assert ifnull("", "default") == ""

    def test_replaceAll_function(self):
        """Test replaceAll function."""
        result = replaceAll("hello world hello", "hello", "hi")
        assert str(result) == "hi world hi"
        assert result.__class__.__name__ == "DelugeString"


class TestBuiltinFunctionsList:
    """Test that all functions are properly exposed."""

    def test_all_functions_in_builtin_dict(self):
        """Test that BUILTIN_FUNCTIONS contains expected functions."""
        expected_functions = [
            "getUrl",
            "postUrl",
            "encodeUrl",
            "urlEncode",
            "urlDecode",
            "base64Encode",
            "base64Decode",
            "aesEncode",
            "aesDecode",
            "abs",
            "cos",
            "sin",
            "tan",
            "log",
            "min",
            "max",
            "exp",
            "power",
            "round",
            "sqrt",
            "toDecimal",
            "toHex",
            "ceil",
            "floor",
            "randomNumber",
            "info",
            "Map",
            "List",
            "ifnull",
            "replaceAll",
            "Collection",
        ]

        for func_name in expected_functions:
            assert func_name in BUILTIN_FUNCTIONS, f"Function {func_name} not in BUILTIN_FUNCTIONS"

    def test_builtin_functions_callable(self):
        """Test that all functions in BUILTIN_FUNCTIONS are callable."""
        for name, func in BUILTIN_FUNCTIONS.items():
            if name not in ["NULL", "null", "true", "false", "True", "False"]:
                assert callable(func), f"{name} is not callable"

    def test_collection_constructor(self):
        """Test Collection constructor."""
        collection = BUILTIN_FUNCTIONS["Collection"]()
        assert isinstance(collection, Map)
        assert collection.isEmpty() is True
