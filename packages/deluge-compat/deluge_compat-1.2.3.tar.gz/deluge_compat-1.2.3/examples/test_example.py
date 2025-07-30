#!/usr/bin/env python3
"""Test example showing how to use the Deluge compatibility layer."""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from deluge_compat import Map, run_deluge_script


def test_simple_script():
    """Test a simple Deluge script."""
    print("=== Testing Simple Deluge Script ===")

    script = """
    response = Map();
    name = "Python";
    message = "Hello from " + name + "!";
    response.put("greeting", message);
    response.put("success", true);

    // Test list operations
    items = List();
    items.add("apple");
    items.add("banana");
    items.add("cherry");

    response.put("items", items);
    response.put("item_count", items.size());

    info "Script executed successfully";

    return response;
    """

    try:
        result = run_deluge_script(script)
        print("Result:", result)
        print("Type:", type(result))

        if isinstance(result, Map):
            print("Greeting:", result.get("greeting"))
            print("Success:", result.get("success"))
            print("Items:", result.get("items"))
            print("Item count:", result.get("item_count"))

    except Exception as e:
        print(f"Error: {e}")


def test_string_operations():
    """Test string operations."""
    print("\n=== Testing String Operations ===")

    script = """
    text = "Hello World";
    result = Map();

    result.put("original", text);
    result.put("upper", text.toUpperCase());
    result.put("lower", text.toLowerCase());
    result.put("length", text.length());
    result.put("contains_world", text.contains("World"));
    result.put("starts_with_hello", text.startsWith("Hello"));
    result.put("substring", text.substring(0, 5));

    return result;
    """

    try:
        result = run_deluge_script(script)
        print("String operations result:", result)

        for key, value in result.items():
            print(f"  {key}: {value} ({type(value).__name__})")

    except Exception as e:
        print(f"Error: {e}")


def test_conditional_logic():
    """Test conditional logic."""
    print("\n=== Testing Conditional Logic ===")

    script = """
    score = 85;
    result = Map();

    if(score >= 90) {
        grade = "A";
    } else if(score >= 80) {
        grade = "B";
    } else if(score >= 70) {
        grade = "C";
    } else {
        grade = "F";
    }

    result.put("score", score);
    result.put("grade", grade);

    return result;
    """

    try:
        result = run_deluge_script(script)
        print("Conditional logic result:", result)

    except Exception as e:
        print(f"Error: {e}")


def test_loops():
    """Test loop structures."""
    print("\n=== Testing Loops ===")

    script = """
    numbers = List();
    numbers.add(1);
    numbers.add(2);
    numbers.add(3);
    numbers.add(4);
    numbers.add(5);

    sum = 0;
    squares = List();

    for each num in numbers {
        sum = sum + num;
        square = num * num;
        squares.add(square);
    }

    result = Map();
    result.put("numbers", numbers);
    result.put("sum", sum);
    result.put("squares", squares);

    return result;
    """

    try:
        result = run_deluge_script(script)
        print("Loop result:", result)

    except Exception as e:
        print(f"Error: {e}")


def test_with_context():
    """Test script execution with additional context."""
    print("\n=== Testing with Additional Context ===")

    script = """
    result = Map();
    result.put("username", username);
    result.put("age", age);
    result.put("is_adult", age >= 18);

    greeting = "Hello " + username + "!";
    if(age >= 18) {
        greeting = greeting + " You are an adult.";
    } else {
        greeting = greeting + " You are a minor.";
    }

    result.put("greeting", greeting);

    return result;
    """

    try:
        result = run_deluge_script(script, username="Alice", age=25)
        print("Context result:", result)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_simple_script()
    test_string_operations()
    test_conditional_logic()
    test_loops()
    test_with_context()

    print("\n=== All Tests Completed ===")
