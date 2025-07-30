"""Integration tests for the complete Deluge compatibility layer."""

from unittest.mock import Mock, patch

import pytest

from deluge_compat import List, Map, run_deluge_script
from deluge_compat.runtime import DelugeRuntimeError

# Integration tests for complete Deluge compatibility scenarios


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    def test_data_processing_pipeline(self):
        """Test a complete data processing pipeline."""
        script = """
        // Input data
        raw_data = List();

        // Add some sample data
        user1 = Map();
        user1.put("name", "Alice Johnson");
        user1.put("email", "alice@example.com");
        user1.put("age", 28);
        raw_data.add(user1);

        user2 = Map();
        user2.put("name", "Bob Smith");
        user2.put("email", "bob@test.com");
        user2.put("age", 35);
        raw_data.add(user2);

        user3 = Map();
        user3.put("name", "Charlie Brown");
        user3.put("email", "charlie@example.com");
        user3.put("age", 22);
        raw_data.add(user3);

        // Process the data
        processed = List();
        example_emails = List();
        adults = List();

        for each user in raw_data {
            // Extract name parts
            full_name = user.get("name");
            email = user.get("email");
            age = user.get("age");

            // Create processed record
            record = Map();
            record.put("full_name", full_name);
            record.put("first_name", full_name.getPrefix(" "));
            record.put("email_domain", email.getSuffix("@"));
            record.put("age", age);
            record.put("is_adult", age >= 18);

            processed.add(record);

            // Collect example.com emails
            if(email.contains("@example.com")) {
                example_emails.add(email);
            }

            // Collect adults
            if(age >= 21) {
                adults.add(full_name);
            }
        }

        // Create summary
        summary = Map();
        summary.put("total_users", raw_data.size());
        summary.put("processed_users", processed);
        summary.put("example_emails", example_emails);
        summary.put("adults", adults);
        summary.put("adult_count", adults.size());

        return summary;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        assert result.get("total_users") == 3

        processed = result.get("processed_users")
        assert isinstance(processed, List)
        assert processed.size() == 3

        # Check first processed record
        first_record = processed.get(0)
        assert first_record.get("first_name") == "Alice"
        assert first_record.get("email_domain") == "example.com"
        assert first_record.get("is_adult") is True

        # Check example emails
        example_emails = result.get("example_emails")
        assert example_emails.size() == 2
        assert "alice@example.com" in example_emails
        assert "charlie@example.com" in example_emails

    def test_text_processing_scenario(self):
        """Test text processing capabilities."""
        script = """
        // Input text
        text = "The Quick Brown Fox Jumps Over The Lazy Dog";

        result = Map();

        // Basic analysis
        result.put("original", text);
        result.put("length", text.length());
        result.put("upper", text.toUpperCase());
        result.put("lower", text.toLowerCase());

        // Word processing
        words = text.toList(" ");
        result.put("word_count", words.size());

        // Find specific words
        long_words = List();
        for each word in words {
            if(word.length() > 4) {
                long_words.add(word.toLowerCase());
            }
        }
        result.put("long_words", long_words);

        // Count specific letters
        result.put("vowel_a_count", text.getOccurence("a") + text.getOccurence("A"));
        result.put("contains_fox", text.contains("Fox"));
        result.put("starts_with_the", text.startsWith("The"));

        // Text transformations
        no_the = text.replaceAll("The ", "");
        result.put("without_the", no_the);

        first_sentence = text.substring(0, 20);
        result.put("first_20_chars", first_sentence);

        return result;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        assert result.get("length") == 43
        assert result.get("word_count") == 9
        assert result.get("contains_fox") is True
        assert result.get("starts_with_the") is True

        long_words = result.get("long_words")
        assert "brown" in long_words
        assert "jumps" in long_words

    @patch("requests.get")
    def test_api_integration_scenario(self, mock_get):
        """Test API integration scenario."""
        # Mock API response
        mock_response = Mock()
        mock_response.text = (
            '{"users": [{"name": "John", "active": true}, {"name": "Jane", "active": false}]}'
        )
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        script = """
        // Fetch data from API
        api_url = "https://api.example.com/users";
        response = getUrl(api_url);

        // Parse JSON response
        data = response.toMap();
        users = data.get("users");

        // Process users
        result = Map();
        active_users = List();
        inactive_users = List();

        for each user in users {
            user_map = user;  // In real scenario, this would be proper casting
            if(user_map.get("active")) {
                active_users.add(user_map.get("name"));
            } else {
                inactive_users.add(user_map.get("name"));
            }
        }

        result.put("total_users", users.size());
        result.put("active_users", active_users);
        result.put("inactive_users", inactive_users);
        result.put("active_count", active_users.size());

        return result;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        mock_get.assert_called_once_with("https://api.example.com/users", headers={})

    def test_mathematical_computation_scenario(self):
        """Test mathematical computations."""
        script = """
        // Generate some numbers
        numbers = List();
        numbers.add(10);
        numbers.add(25);
        numbers.add(15);
        numbers.add(30);
        numbers.add(5);

        result = Map();

        // Basic statistics
        total = 0;
        count = numbers.size();

        for each num in numbers {
            total = total + num;
        }

        average = total / count;
        result.put("total", total);
        result.put("count", count);
        result.put("average", average);

        // Mathematical operations
        result.put("sqrt_of_25", sqrt(25));
        result.put("power_2_3", power(2, 3));
        result.put("abs_neg_10", abs(-10));
        result.put("min_5_15", min(5, 15));
        result.put("max_5_15", max(5, 15));

        // Random number (just check it's generated)
        random_num = randomNumber(100, 1);
        result.put("random_generated", random_num >= 1 && random_num < 100);

        return result;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        assert result.get("total") == 85
        assert result.get("count") == 5
        assert result.get("average") == 17.0
        assert result.get("sqrt_of_25") == 5.0
        assert result.get("power_2_3") == 8
        assert result.get("abs_neg_10") == 10
        assert result.get("min_5_15") == 5
        assert result.get("max_5_15") == 15
        assert result.get("random_generated") is True

    def test_encoding_decoding_scenario(self):
        """Test encoding and decoding operations."""
        script = """
        original_text = "Hello World! This is a test message.";
        result = Map();

        // Base64 encoding/decoding
        base64_encoded = base64Encode(original_text);
        base64_decoded = base64Decode(base64_encoded);
        result.put("base64_round_trip", base64_decoded.equals(original_text));

        // URL encoding/decoding
        url_text = "hello world & special chars!";
        url_encoded = encodeUrl(url_text);
        url_decoded = urlDecode(url_encoded);
        result.put("url_round_trip", url_decoded.equals(url_text));

        // AES encoding/decoding
        secret_key = "my_secret_key";
        aes_encrypted = aesEncode(secret_key, original_text);
        aes_decrypted = aesDecode(secret_key, aes_encrypted);
        result.put("aes_round_trip", aes_decrypted.equals(original_text));

        // Store samples
        result.put("original", original_text);
        result.put("base64_sample", base64_encoded);
        result.put("url_sample", url_encoded);
        result.put("aes_sample", aes_encrypted);

        return result;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        assert result.get("base64_round_trip") is True
        assert result.get("url_round_trip") is True
        assert result.get("aes_round_trip") is True

        # Check that encoded values are different from original
        original = str(result.get("original"))
        assert str(result.get("base64_sample")) != original
        assert str(result.get("url_sample")) != original
        assert str(result.get("aes_sample")) != original

    def test_complex_data_structure_scenario(self):
        """Test working with complex nested data structures."""
        script = """
        // Create a complex data structure
        company = Map();
        company.put("name", "Tech Corp");
        company.put("founded", 2020);

        departments = List();

        // Engineering department
        engineering = Map();
        engineering.put("name", "Engineering");
        engineering.put("budget", 500000);

        eng_employees = List();
        eng_employees.add("Alice");
        eng_employees.add("Bob");
        eng_employees.add("Charlie");
        engineering.put("employees", eng_employees);

        departments.add(engineering);

        // Marketing department
        marketing = Map();
        marketing.put("name", "Marketing");
        marketing.put("budget", 200000);

        marketing_employees = List();
        marketing_employees.add("David");
        marketing_employees.add("Eve");
        marketing.put("employees", marketing_employees);

        departments.add(marketing);

        company.put("departments", departments);

        // Analyze the structure
        result = Map();
        result.put("company_name", company.get("name"));
        result.put("total_departments", departments.size());

        total_budget = 0;
        total_employees = 0;
        employee_names = List();

        for each dept in departments {
            dept_budget = dept.get("budget");
            dept_employees = dept.get("employees");

            total_budget = total_budget + dept_budget;
            total_employees = total_employees + dept_employees.size();

            for each employee in dept_employees {
                employee_names.add(employee);
            }
        }

        result.put("total_budget", total_budget);
        result.put("total_employees", total_employees);
        result.put("all_employees", employee_names);
        result.put("company_structure", company);

        return result;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        assert result.get("company_name") == "Tech Corp"
        assert result.get("total_departments") == 2
        assert result.get("total_budget") == 700000
        assert result.get("total_employees") == 5

        all_employees = result.get("all_employees")
        assert all_employees.size() == 5
        assert "Alice" in all_employees
        assert "David" in all_employees


class TestErrorScenarios:
    """Test error handling in integration scenarios."""

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON."""
        script = """
        bad_json = "{ invalid json }";
        try_parse = bad_json.toMap();
        """

        with pytest.raises(
            (ValueError, RuntimeError, DelugeRuntimeError)
        ):  # Should raise some kind of error
            run_deluge_script(script)

    def test_list_index_out_of_bounds(self):
        """Test graceful handling of list index errors."""
        script = """
        small_list = List();
        small_list.add("only_item");

        result = Map();
        result.put("valid_item", small_list.get(0));
        result.put("invalid_item", small_list.get(10));  # Should return None

        return result;
        """

        result = run_deluge_script(script)

        assert isinstance(result, Map)
        assert result.get("valid_item") == "only_item"
        assert result.get("invalid_item") is None
