# Zobot and SalesIQ Support

This document provides comprehensive information about using deluge-compat with Zoho SalesIQ Zobot scripts.

## Overview

deluge-compat includes full support for Zoho SalesIQ Zobot development and testing, allowing you to:

- Run and test Zobot scripts locally
- Mock visitor data and API responses
- Simulate interactive chat sessions
- Debug Zobot logic without affecting production

## Quick Start

### Basic Zobot Script

```deluge
response = Map();
msg = message.get("text");

// Get visitor information
visitor_name = visitor.getJSON("name");
visitor_email = visitor.getJSON("email");

// Simple greeting logic
if(msg.toLowerCase().contains("hello"))
{
    response.put("action", "reply");
    response.put("replies", List(["Hello " + visitor_name + "! How can I help you today?"]));
}
else if(msg.toLowerCase().contains("agent") || msg.toLowerCase().contains("human"))
{
    response.put("action", "forward");
    response.put("replies", List(["I'll connect you to a human agent right away."]));
}
else
{
    response.put("action", "reply");
    response.put("replies", List(["I understand you said: " + msg + ". Could you please be more specific?"]));
}

return response;
```

### Running the Script

```bash
# Interactive chat with auto-generated visitor data
deluge-chat my_zobot.dg --visitor-mock-source faker

# Use custom visitor data
deluge-chat my_zobot.dg --visitor-mock-source json --visitor-mock-file visitor_data.json
```

## SalesIQ Objects

### Visitor Object

The `visitor` object contains information about the website visitor:

#### Basic Information
- `name` - Visitor's name
- `email` - Email address
- `phone` - Phone number
- `active_conversation_id` - Current conversation ID

#### Location & Context
- `state` - Visitor's state/province
- `city` - Visitor's city
- `country` - Country
- `ip` - IP address
- `time_zone` - Timezone

#### Page Information
- `current_page_url` - Current page URL
- `current_page_title` - Current page title
- `landing_page_url` - First page visited
- `previous_page_url` - Previous page

#### Visit History
- `number_of_past_visits` - Number of previous visits
- `number_of_past_chats` - Number of previous chats
- `last_visit_time` - Last visit timestamp

#### Device & Browser
- `browser` - Browser name
- `os` - Operating system
- `channel` - Channel (Website, Mobile App, etc.)

#### Campaign Tracking
- `campaign_source` - Traffic source
- `campaign_medium` - Marketing medium
- `campaign_content` - Campaign content
- `referer` - Referring URL

#### Usage

```deluge
// Get visitor information
email = visitor.getJSON("email");
name = visitor.getJSON("name");
visits = visitor.getJSON("number_of_past_visits");

// Use in logic
if(visits.toLong() > 5)
{
    // VIP customer logic
    response.put("replies", List(["Welcome back, " + name + "! As a valued customer..."]));
}
```

### Message Object

The `message` object contains the user's input:

```deluge
msg = message.get("text");

// Process message
if(msg.contains("product"))
{
    // Handle product inquiry
}
```

### Response Object

Build responses using Map with specific structure:

#### Reply Action
```deluge
response = Map();
response.put("action", "reply");
response.put("replies", List(["Your message here", "Second message if needed"]));
return response;
```

#### Forward to Agent
```deluge
response = Map();
response.put("action", "forward");
response.put("replies", List(["Connecting you to an agent..."]));
return response;
```

#### End Conversation
```deluge
response = Map();
response.put("action", "end");
response.put("replies", List(["Thank you for chatting with us!"]));
return response;
```

#### With Suggestions
```deluge
response = Map();
response.put("action", "reply");
response.put("replies", List(["How can I help you?"]));
response.put("suggestions", List(["Product Info", "Pricing", "Support"]));
return response;
```

## Session Management

### Store Session Data

```deluge
// Store data for the session
session_data = Map();
session_data.put("user_interest", "chatbots");
session_data.put("quote_requested", true);

zoho.salesiq.visitorsession.set("portal_name", session_data, "connection_name");
```

### Retrieve Session Data

```deluge
// Get stored session data
interest_response = zoho.salesiq.visitorsession.get("portal_name", "user_interest", "connection_name");

if(interest_response.size() > 0)
{
    user_interest = interest_response.getJSON("user_interest_response");
    // Use the stored data
}
```

## Email Integration

Send emails from your Zobot:

```deluge
sendmail
[
    from: "bot@company.com"
    to: "support@company.com"
    subject: "New Zobot Inquiry"
    message: "Visitor " + visitor.getJSON("email") + " asked: " + message.get("text")
]
```

## Mock Data Configuration

### Visitor Mock Sources

#### 1. Faker (Auto-generated)
```bash
deluge-chat script.dg --visitor-mock-source faker
```

Generates realistic visitor data automatically.

#### 2. JSON File
```bash
deluge-chat script.dg --visitor-mock-source json --visitor-mock-file visitor.json
```

Example `visitor.json`:
```json
{
  "default": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "state": "California",
    "city": "San Francisco",
    "current_page_url": "https://example.com/products",
    "number_of_past_visits": "3",
    "active_conversation_id": "conv_123"
  },
  "scenarios": {
    "new_visitor": {
      "name": "",
      "email": "",
      "number_of_past_visits": "1"
    },
    "vip_customer": {
      "name": "Jane Smith",
      "email": "jane@bigcorp.com",
      "number_of_past_visits": "15",
      "company_name": "Big Corp Inc"
    }
  }
}
```

Use scenarios:
```bash
deluge-chat script.dg --visitor-mock-source json --visitor-mock-file visitor.json --visitor-scenario vip_customer
```

#### 3. API Endpoint
```bash
deluge-chat script.dg --visitor-mock-source endpoint --visitor-mock-endpoint http://localhost:8080/visitor
```

### API Response Mocking

Mock external API calls for testing:

```bash
deluge-chat script.dg --api-mock-source json --api-mock-file api_responses.json
```

Example `api_responses.json`:
```json
{
  "https://api.chatbot.com/webhook": {
    "default": {
      "replies": {
        "text": "I'd be happy to help you!"
      },
      "thread_id": "thread_123"
    },
    "patterns": [
      {
        "request_contains": {
          "message": ".*product.*"
        },
        "response": {
          "replies": {
            "text": "Our products include chatbots, analytics, and automation tools."
          }
        }
      },
      {
        "request_contains": {
          "message": ".*pricing.*"
        },
        "response": {
          "replies": {
            "text": "Our pricing starts at $99/month. Would you like a detailed quote?"
          }
        }
      }
    ]
  }
}
```

### Message Mocking

#### Interactive (Default)
User types messages manually during testing.

#### JSON File
```bash
deluge-chat script.dg --message-mock-source json --message-mock-file messages.json
```

Example `messages.json`:
```json
{
  "messages": [
    "Hello, I'm interested in your chatbot",
    "What features does it have?",
    "How much does it cost?",
    "Can I see a demo?",
    "Thank you",
    "end chat"
  ]
}
```

## CLI Commands

### deluge-chat

Interactive chat testing for Zobot scripts.

```bash
deluge-chat [OPTIONS] SCRIPT_FILE
```

#### Options

**Visitor Options:**
- `--visitor-mock-source [faker|json|endpoint|none]` - Visitor data source
- `--visitor-mock-file PATH` - JSON file with visitor data
- `--visitor-mock-endpoint URL` - API endpoint for visitor data
- `--visitor-scenario NAME` - Scenario name for JSON files

**Message Options:**
- `--message-mock-source [interactive|json|endpoint]` - Message source
- `--message-mock-file PATH` - JSON file with messages

**API Options:**
- `--api-mock-source [json|endpoint|passthrough]` - API response source
- `--api-mock-file PATH` - JSON file with API responses
- `--api-mock-endpoint URL` - Mock API endpoint

**General Options:**
- `--debug` - Enable debug output
- `--session-limit INT` - Maximum messages per session (default: 50)

#### Examples

```bash
# Basic interactive testing
deluge-chat my_zobot.dg

# Automated testing with predefined messages
deluge-chat my_zobot.dg --message-mock-source json --message-mock-file test_messages.json

# Test with specific visitor type
deluge-chat my_zobot.dg --visitor-scenario new_visitor

# Full mock environment
deluge-chat my_zobot.dg \
  --visitor-mock-source json --visitor-mock-file visitors.json \
  --api-mock-source json --api-mock-file api_responses.json \
  --message-mock-source json --message-mock-file messages.json
```

## Advanced Features

### Configuration File

Create `.deluge-compat.yaml` for project defaults:

```yaml
salesiq:
  visitor:
    mock_source: faker
    faker_locale: en_US
    faker_seed: 12345

  message:
    mock_source: interactive

  api_responses:
    mock_source: json
    mock_file: api_responses.json

  session:
    storage: memory

  portals:
    default: my_portal
    connections:
      salesiq_conn:
        type: salesiq
        enabled: true
```

### Custom Mock Endpoints

Create your own mock server to provide dynamic data:

```python
# Simple Flask mock server
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/visitor')
def get_visitor():
    return jsonify({
        "name": "Dynamic User",
        "email": "user@example.com",
        "current_page_url": request.args.get('page', '/'),
        # ... other fields
    })

@app.route('/api-mock', methods=['POST'])
def mock_api():
    data = request.json
    # Process request and return appropriate response
    return jsonify({
        "replies": {"text": "Dynamic response based on: " + data['message']},
        "thread_id": "dynamic_thread"
    })
```

### Testing Workflows

#### 1. Unit Testing Approach
Test individual parts of your Zobot:

```bash
# Test greeting logic
echo "hello" | deluge-chat greeting_test.dg --visitor-scenario new_visitor

# Test agent transfer
echo "I need human help" | deluge-chat agent_transfer.dg
```

#### 2. Integration Testing
Test complete user journeys:

```bash
deluge-chat full_bot.dg --message-mock-file user_journey.json --visitor-scenario returning_customer
```

#### 3. Performance Testing
Test with high message volumes:

```bash
deluge-chat bot.dg --session-limit 100 --message-mock-file stress_test.json
```

## Best Practices

### 1. Visitor Data Handling
```deluge
// Always check if visitor data exists
email = visitor.getJSON("email");
if(email != null && email != "")
{
    // Use email
}
else
{
    // Handle anonymous visitor
}
```

### 2. Session Management
```deluge
// Store important state
session_data = Map();
session_data.put("step", "product_selection");
session_data.put("interest", product_type);
zoho.salesiq.visitorsession.set("portal", session_data, "conn");
```

### 3. Error Handling
```deluge
// Graceful fallbacks
try_response = zoho.salesiq.visitorsession.get("portal", "data", "conn");
if(try_response.size() == 0)
{
    // Handle missing session data
    response.put("replies", List(["Let me start fresh. How can I help you?"]));
}
```

### 4. Response Patterns
```deluge
// Clear action structure
response = Map();

if(should_end_chat)
{
    response.put("action", "end");
}
else if(needs_human_agent)
{
    response.put("action", "forward");
}
else
{
    response.put("action", "reply");
}

response.put("replies", List([message_text]));
return response;
```

## Troubleshooting

### Common Issues

#### 1. Translation Errors
- Ensure all Deluge syntax is supported
- Check for missing semicolons or braces
- Use `--debug` flag to see translation output

#### 2. Mock Data Not Loading
- Verify file paths are correct
- Check JSON syntax with a validator
- Use absolute paths if needed

#### 3. Session Data Issues
- Remember session data is cleared between script runs
- Use consistent portal and connection names
- Check if data exists before using

### Debug Mode

Use `--debug` to see detailed information:

```bash
deluge-chat script.dg --debug
```

This shows:
- Mock configuration
- Visitor context
- Script execution details
- Translation output
- Error traces

## Integration with Zoho SalesIQ

While deluge-compat is for testing and development, here's how it maps to production:

### Development → Production
1. **Test locally** with deluge-compat
2. **Validate logic** with various visitor scenarios
3. **Deploy to SalesIQ** Zobot environment
4. **Monitor and iterate** based on real interactions

### Key Differences
- **Session Storage**: Memory in deluge-compat vs. SalesIQ managed
- **Visitor Data**: Mocked vs. real visitor tracking
- **API Calls**: Mocked vs. actual external services
- **Email**: Logged vs. actually sent

## Examples Repository

Check the `examples/` directory for:
- `simple_zobot.dg` - Basic bot logic
- `advanced_zobot.dg` - Complex scenarios
- `visitor_scenarios.json` - Various visitor types
- `api_responses.json` - Mock API responses
- `test_conversations.json` - Automated test messages

## Contributing

To add new SalesIQ features:
1. Update `src/deluge_compat/salesiq/core.py` for new objects
2. Add functions in `src/deluge_compat/salesiq/functions.py`
3. Update mock system in `src/deluge_compat/salesiq/mocks.py`
4. Add tests in `tests/test_salesiq*.py`
5. Update this documentation

---

**Disclaimer**: This is a development and testing tool. For production Zobot deployment, use the official Zoho SalesIQ platform.
