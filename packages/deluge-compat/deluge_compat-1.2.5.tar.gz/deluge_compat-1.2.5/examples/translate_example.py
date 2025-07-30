#!/usr/bin/env python3
"""Example of translating Deluge scripts to Python code."""

from deluge_compat import translate_deluge_to_python


def main():
    # Example 1: Simple Deluge script
    deluge_script = """
    // Create a greeting message
    name = "World";
    greeting = "Hello " + name + "!";

    result = Map();
    result.put("message", greeting);
    result.put("timestamp", "2024-01-01");

    return result;
    """

    print("=== Example 1: Simple Script ===")
    print("Original Deluge script:")
    print(deluge_script)
    print("\nTranslated Python code:")
    python_code = translate_deluge_to_python(deluge_script)
    print(python_code)

    # Example 2: Script with control structures
    deluge_script2 = """
    numbers = List();
    numbers.add(1);
    numbers.add(2);
    numbers.add(3);
    numbers.add(4);
    numbers.add(5);

    sum = 0;
    evens = List();

    for each num in numbers {
        sum = sum + num;

        if(num % 2 == 0) {
            evens.add(num);
        }
    }

    result = Map();
    result.put("sum", sum);
    result.put("evens", evens);
    result.put("count", numbers.size());

    return result;
    """

    print("\n\n=== Example 2: Script with Control Structures ===")
    print("Original Deluge script:")
    print(deluge_script2)
    print("\nTranslated Python code (without wrapper):")
    python_code2 = translate_deluge_to_python(deluge_script2, wrap_in_function=False)
    print(python_code2)

    # Example 3: Save translated code to file
    output_file = "translated_script.py"
    with open(output_file, "w") as f:
        f.write(translate_deluge_to_python(deluge_script2))
    print("\n\n=== Example 3: Saved to File ===")
    print(f"Translated script saved to: {output_file}")
    print("You can now run it with: python translated_script.py")


if __name__ == "__main__":
    main()
