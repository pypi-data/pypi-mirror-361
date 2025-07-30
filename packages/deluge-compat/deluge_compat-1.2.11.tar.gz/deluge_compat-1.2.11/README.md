# Deluge Compatibility Layer

A Python compatibility layer that allows you to execute Deluge scripts within Python environments. This project provides a runtime environment and translator that converts Deluge language syntax to Python, enabling testing and execution of Deluge scripts outside of their native environment.

## Features

- **Complete Data Type Support**: Implements Deluge's Map, List, and String types with all their methods
- **Built-in Functions**: HTTP requests, encoding/decoding, mathematical operations, and utility functions
- **Script Translation**: Converts Deluge syntax to executable Python code
- **Runtime Environment**: Provides a sandboxed execution context for Deluge scripts
- **Zobot Support**: Full SalesIQ/Zobot development with interactive chat simulation
- **Easy Integration**: Simple API for running Deluge scripts from Python

## Installation

### Full Installation (Recommended)

Includes CLI tools, rich output formatting, and all features:

```bash
# Install from PyPI (when published)
pip install deluge-compat

# Or with uv
uv add deluge-compat

# Or from source
git clone git@github.com:jctosta/deluge-compat.git
cd deluge-compat
uv install
```

### Slim Installation

For minimal dependencies in environments where you only need the core compatibility layer:

```bash
pip install deluge-compat[slim]
# or
uv add deluge-compat[slim]
```

The slim version excludes CLI tools and rich formatting but retains all core translation and execution capabilities.

## Quick Start

### Command Line Tools

The package provides CLI tools for working with Deluge scripts:

#### Running Deluge Scripts

```bash
# Run a Deluge script file
deluge-run my_script.dg

# Run with JSON output
deluge-run my_script.dg --json

# Run with verbose output
deluge-run my_script.dg --verbose
```

#### Translating Deluge Scripts to Python

```bash
# Translate a Deluge script to Python
deluge-translate my_script.dg --output converted.py
```

#### Interactive Zobot Chat Testing

```bash
# Test Zobot scripts with interactive chat
deluge-chat my_zobot.dg

# Use specific visitor data
deluge-chat my_zobot.dg --visitor-mock-source json --visitor-mock-file visitor_data.json

# Automated testing with predefined messages
deluge-chat my_zobot.dg --message-mock-source json --message-mock-file test_messages.json
```

For detailed usage information, see our [documentation](#documentation).

### Basic Usage Examples

```python
from deluge_compat import run_deluge_script

# Simple script execution
result = run_deluge_script('''
    response = Map();
    response.put("greeting", "Hello World!");
    return response;
''')
print(result)  # {'greeting': 'Hello World!'}

# With context variables
result = run_deluge_script('''
    greeting = "Hello " + username + "!";
    return Map({"message": greeting});
''', username="Alice")
print(result['message'])  # "Hello Alice!"
```

### Translation to Python

```python
from deluge_compat import translate_deluge_to_python

# Generate PEP 723 compatible Python script
python_code = translate_deluge_to_python('''
    numbers = List([1, 2, 3]);
    sum = 0;
    for each num in numbers {
        sum = sum + num;
    }
    return Map({"sum": sum});
''')

# Save and run with: uv run script.py
with open("script.py", "w") as f:
    f.write(python_code)
```

## Documentation

### Core Features
- **[Basic Usage Guide](docs/BASIC_USAGE.md)** - Complete guide to data types, functions, and common patterns
- **[Zobot Support Guide](docs/ZOBOT_SUPPORT.md)** - SalesIQ/Zobot development with interactive testing

### Quick Reference

**Data Types**: Map, List, String with full Deluge method compatibility
**Functions**: HTTP, encoding, math, utilities, and SalesIQ session management
**CLI Tools**: `deluge-run`, `deluge-translate`, `deluge-chat`
**Testing**: Comprehensive test suite with 28 SalesIQ tests + 115 core tests

## Examples

Check the `examples/` directory and documentation for comprehensive examples:

- **Basic Operations**: Data manipulation, string processing, control flow
- **HTTP Integration**: API calls, data processing, error handling
- **Zobot Scripts**: Customer service bots, session management, interactive chat
- **Translation Examples**: Converting Deluge to Python with PEP 723 support

## Testing

Comprehensive test coverage with **143 total tests** (115 core + 28 SalesIQ) achieving **100% success rate**.

```bash
# Run all tests
uv run pytest

# Test specific functionality
uv run pytest tests/test_types.py      # Data types
uv run pytest tests/test_salesiq.py    # SalesIQ/Zobot features
uv run pytest tests/test_showcase.py   # Working features demo
```

✅ **Production Ready**: Complete Deluge language support with full SalesIQ/Zobot compatibility

## Project Structure

```
deluge-compat/
├── src/deluge_compat/
│   ├── __init__.py          # Main API
│   ├── types.py             # Deluge data types
│   ├── functions.py         # Built-in functions
│   ├── translator.py        # Deluge → Python translator
│   ├── runtime.py           # Execution environment
│   ├── cli_*.py             # CLI tools
│   └── salesiq/             # SalesIQ/Zobot support
├── docs/                    # Documentation
├── examples/                # Usage examples
└── tests/                   # Test suite
```

## Architecture

**Core Engine**: Types, Functions, Translator, Runtime
**SalesIQ Layer**: Visitor/Message objects, session management, mock system
**CLI Tools**: Interactive testing, script translation, chat simulation
**Testing**: Comprehensive validation with 143 tests

All core Deluge features are fully supported with complete SalesIQ/Zobot compatibility.

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all tests pass (`uv run pytest`)
5. Run code quality checks (`uv run ruff check .` and `uv run pyright .`)
6. Submit a pull request

See [development documentation](docs/) for detailed contribution guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the Deluge language specification and documentation
- Inspired by the [Deluge Language Parser](https://github.com/GuruDhanush/Deluge-Language-Parser) project
- Built with Python 3.12+ and modern tooling
- **Created with the assistance of Claude Code** - Anthropic's AI-powered coding assistant

---

## Disclaimer

**Deluge Language Ownership**: Deluge is a proprietary scripting language owned and developed by Zoho Corporation. This project is an independent, unofficial compatibility layer created for educational and development purposes. It is not affiliated with, endorsed by, or sponsored by Zoho Corporation.

**Usage Notice**: This compatibility layer is intended for testing, development, and educational purposes only. For production Deluge script execution, please use the official Deluge runtime environment provided by Zoho Corporation.

**Trademark Notice**: "Deluge" is a trademark of Zoho Corporation. This project respects all intellectual property rights and trademarks of Zoho Corporation.
