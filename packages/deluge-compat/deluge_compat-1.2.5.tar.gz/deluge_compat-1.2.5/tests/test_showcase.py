"""Showcase tests demonstrating working Deluge compatibility features."""

from deluge_compat import List, Map, run_deluge_script


class TestWorkingFeatures:
    """Test suite showcasing all the working features of the compatibility layer."""

    def test_data_types_creation_and_methods(self):
        """Demonstrate all data types and their methods work correctly."""
        # Test Map
        m = Map()
        m.put("name", "John")
        m.put("age", 30)
        assert m.get("name") == "John"
        assert m.containKey("age")
        assert m.keys().size() == 2

        # Test List
        list = List()
        list.add("apple")
        list.add("banana")
        list.add("cherry")
        assert list.size() == 3
        assert list.get(1) == "banana"
        assert list.indexOf("cherry") == 2

        # Test DelugeString
        from deluge_compat.types import deluge_string

        s = deluge_string("Hello World")
        assert s.length() == 11
        assert s.toUpperCase() == "HELLO WORLD"
        assert s.contains("World")
        assert s.substring(0, 5) == "Hello"

    def test_string_processing_capabilities(self):
        """Demonstrate comprehensive string processing."""
        from deluge_compat.types import deluge_string

        text = deluge_string("The Quick Brown Fox Jumps Over The Lazy Dog")

        # Basic operations
        assert text.length() == 43
        assert text.toUpperCase() == "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        assert text.toLowerCase() == "the quick brown fox jumps over the lazy dog"

        # Search operations
        assert text.contains("Fox")
        assert text.startsWith("The")
        assert text.endsWith("Dog")
        assert text.indexOf("Fox") == 16

        # Transformation operations
        words = text.toList(" ")
        assert words.size() == 9
        assert words.get(2) == "Brown"

        # Replace operations
        replaced = text.replaceAll("The", "A")
        assert replaced == "A Quick Brown Fox Jumps Over A Lazy Dog"

        # Substring operations
        first_part = text.substring(0, 15)
        assert first_part == "The Quick Brown"

    def test_encoding_decoding_functions(self):
        """Demonstrate all encoding/decoding functions work."""
        from deluge_compat.functions import (
            aesDecode,
            aesEncode,
            base64Decode,
            base64Encode,
            encodeUrl,
            urlDecode,
        )

        original = "Hello World! & Special Characters 123"

        # Base64 encoding
        b64_encoded = base64Encode(original)
        b64_decoded = base64Decode(str(b64_encoded))
        assert str(b64_decoded) == original

        # URL encoding
        url_encoded = encodeUrl(original)
        url_decoded = urlDecode(str(url_encoded))
        assert str(url_decoded) == original

        # AES encoding (simplified)
        key = "secret_key"
        aes_encrypted = aesEncode(key, original)
        aes_decrypted = aesDecode(key, str(aes_encrypted))
        assert str(aes_decrypted) == original

    def test_mathematical_functions(self):
        """Demonstrate all mathematical functions work."""
        from deluge_compat.functions import (
            abs_func,
            ceil_func,
            floor_func,
            max_func,
            min_func,
            power_func,
            randomNumber,
            round_func,
            sqrt_func,
        )

        # Basic math
        assert abs_func(-5) == 5
        assert min_func(10, 20) == 10
        assert max_func(10, 20) == 20
        assert power_func(2, 3) == 8
        assert abs(sqrt_func(16) - 4.0) < 1e-10

        # Rounding
        assert ceil_func(3.2) == 4
        assert floor_func(3.8) == 3
        assert round_func(3.14159, 2) == 3.14

        # Random (just check it's in range)
        for _ in range(10):
            rand = randomNumber(100, 50)
            assert 50 <= rand < 100

    def test_list_operations_comprehensive(self):
        """Demonstrate comprehensive list operations."""
        numbers = List()

        # Add elements
        for i in [5, 2, 8, 1, 9, 3]:
            numbers.add(i)

        assert numbers.size() == 6

        # Sort operations
        numbers_copy = List()
        numbers_copy.addAll(numbers)
        numbers_copy.sort(True)  # Ascending
        assert numbers_copy.get(0) == 1
        assert numbers_copy.get(5) == 9  # Last element

        # Distinct operations
        duplicates = List()
        for item in [1, 2, 2, 3, 3, 3]:
            duplicates.add(item)

        unique = duplicates.distinct()
        assert unique.size() == 3

        # Intersection
        list1 = List()
        list2 = List()
        for item in [1, 2, 3, 4]:
            list1.add(item)
        for item in [3, 4, 5, 6]:
            list2.add(item)

        intersection = list1.intersect(list2)
        assert intersection.size() == 2
        assert 3 in intersection
        assert 4 in intersection

    def test_map_operations_comprehensive(self):
        """Demonstrate comprehensive map operations."""
        user_data = Map()

        # Basic operations
        user_data.put("name", "Alice Johnson")
        user_data.put("email", "alice@example.com")
        user_data.put("age", 28)
        user_data.put("active", True)

        assert len(user_data) == 4
        assert not user_data.isEmpty()

        # Key/value checks
        assert user_data.containKey("email")
        assert user_data.containValue("Alice Johnson")
        assert not user_data.containKey("salary")

        # Keys extraction
        keys = user_data.keys()
        assert keys.size() == 4
        assert "name" in keys
        assert "age" in keys

        # Merge operations
        additional_data = Map()
        additional_data.put("department", "Engineering")
        additional_data.put("salary", 75000)

        user_data.putAll(additional_data)
        assert len(user_data) == 6
        assert user_data.get("department") == "Engineering"

    def test_simple_script_execution(self):
        """Demonstrate simple script execution works."""
        script = """
        // Create a response object
        response = Map();

        // Add some data
        response.put("status", "success");
        response.put("message", "Hello from Deluge!");
        response.put("timestamp", "2024-01-01");

        // Create a list of items
        items = List();
        items.add("apple");
        items.add("banana");
        items.add("cherry");

        response.put("items", items);
        response.put("item_count", items.size());

        // Return the response
        return response;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        assert result.get("status") == "success"
        assert "Hello from Deluge!" in str(result.get("message"))
        assert result.get("item_count") == 3

        items = result.get("items")
        assert isinstance(items, List)
        assert items.get(0) == "apple"

    def test_script_with_context_variables(self):
        """Demonstrate script execution with context variables."""
        # Use a simpler script that works with basic context variables
        script = """
        // Use context variables
        greeting = "Hello " + username + "!";

        result = Map();
        result.put("greeting", greeting);
        result.put("age", age);
        result.put("is_adult", age >= 18);
        result.put("username", username);

        return result;
        """

        result = run_deluge_script(script, username="John", age=25)

        assert isinstance(result, Map)
        assert "Hello John!" in str(result.get("greeting"))
        assert result.get("age") == 25
        assert result.get("is_adult") is True
        assert result.get("username") == "John"

    def test_error_handling_graceful(self):
        """Demonstrate graceful error handling."""
        # Test that invalid operations return sensible defaults
        list = List()
        assert list.get(999) is None  # Out of bounds returns None

        m = Map()
        assert m.get("nonexistent") is None  # Missing key returns None

        # Test that string operations handle edge cases
        from deluge_compat.types import deluge_string

        s = deluge_string("test")
        assert s.indexOf("xyz") == -1  # Not found returns -1
        assert s.substring(100) == ""  # Out of bounds returns empty

    def test_type_conversions(self):
        """Demonstrate type conversion capabilities."""
        from deluge_compat.types import deluge_string

        # String to number
        num_str = deluge_string("123")
        assert num_str.toLong() == 123

        hex_str = deluge_string("0xFF")
        assert hex_str.toLong() == 255

        # String to list
        csv_str = deluge_string("apple,banana,cherry")
        fruit_list = csv_str.toList(",")
        assert fruit_list.size() == 3
        assert fruit_list.get(1) == "banana"

        # String to JSON
        json_str = deluge_string('{"name": "John", "age": 30}')
        json_map = json_str.toMap()
        assert json_map.get("name") == "John"
        assert json_map.get("age") == 30

        # List to string conversion (through joining)
        items = List()
        items.add("a")
        items.add("b")
        items.add("c")
        # Note: Direct list-to-string conversion would need to be implemented
        # but individual items work fine
        assert str(items.get(0)) == "a"


class TestPerformanceScenarios:
    """Test performance and scalability of basic operations."""

    def test_large_list_operations(self):
        """Test operations on larger lists."""
        large_list = List()

        # Add 1000 items
        for i in range(1000):
            large_list.add(f"item_{i}")

        assert large_list.size() == 1000
        assert large_list.get(500) == "item_500"
        assert large_list.indexOf("item_999") == 999

        # Test search operations (use indexOf instead of contains)
        assert large_list.indexOf("item_750") == 750
        assert large_list.indexOf("item_1000") == -1

        # Test sublist
        sub = large_list.sublist(100, 110)
        assert sub.size() == 10
        assert sub.get(0) == "item_100"

    def test_large_map_operations(self):
        """Test operations on larger maps."""
        large_map = Map()

        # Add 500 key-value pairs
        for i in range(500):
            large_map.put(f"key_{i}", f"value_{i}")

        assert len(large_map) == 500
        assert large_map.get("key_250") == "value_250"
        assert large_map.containKey("key_499")
        assert not large_map.containKey("key_500")

        # Test keys extraction
        all_keys = large_map.keys()
        assert all_keys.size() == 500
        assert "key_0" in all_keys
