# Basic Usage Guide

This guide covers the fundamental features of deluge-compat for running and testing Deluge scripts in Python.

## Quick Start

### Installation

```bash
pip install deluge-compat
```

### Your First Deluge Script

Create a simple Deluge script (`hello.dg`):

```deluge
response = Map();
name = "World";
message = "Hello " + name + "!";
response.put("greeting", message);
return response;
```

Run it with:

```bash
deluge-run hello.dg
```

## Core Data Types

deluge-compat provides Python implementations of Deluge's core data types with all their methods.

### Map

Maps are key-value containers similar to Python dictionaries but with Deluge-specific methods:

```deluge
// Creating maps
userMap = Map();
userMap.put("name", "John Doe");
userMap.put("email", "john@example.com");
userMap.put("age", 30);

// Accessing values
name = userMap.get("name");
email = userMap.getJSON("email");

// Map operations
size = userMap.size();
keys = userMap.keys();
isEmpty = userMap.isEmpty();

// Checking for keys
hasName = userMap.containsKey("name");

// Removing values
userMap.remove("age");
userMap.clear(); // Remove all
```

#### JSON Operations

```deluge
// Convert to JSON string
jsonString = userMap.toJSONString();

// Create from JSON
dataMap = Map();
dataMap.putJSON("config", "{\"theme\": \"dark\", \"notifications\": true}");
```

### List

Lists are ordered collections with Deluge-specific methods:

```deluge
// Creating lists
fruits = List();
fruits.add("apple");
fruits.add("banana");
fruits.add("orange");

// Or create with initial values
numbers = List([1, 2, 3, 4, 5]);

// Accessing elements
firstFruit = fruits.get(0);
lastFruit = fruits.get(fruits.size() - 1);

// List operations
size = fruits.size();
isEmpty = fruits.isEmpty();
contains = fruits.contains("apple");

// Modifying lists
fruits.insert(1, "grape");
fruits.remove("banana");
fruits.clear();

// Converting
text = fruits.toString(); // Comma-separated string
```

#### Advanced List Operations

```deluge
// Sorting
numbers.sort(); // Ascending
numbers.reverse(); // Reverse order

// Sublists
subset = numbers.subList(1, 3); // Elements from index 1 to 3

// Distinct values
uniqueList = numbers.distinct();
```

### Deluge Strings

Strings in deluge-compat have extensive text manipulation methods:

```deluge
text = "Hello, World!";

// Case operations
upper = text.toUpperCase();
lower = text.toLowerCase();

// String information
length = text.length();
isEmpty = text.isEmpty();

// Searching
contains = text.contains("World");
startsWith = text.startsWith("Hello");
endsWith = text.endsWith("!");
index = text.indexOf("o");
lastIndex = text.lastIndexOf("o");

// Substring operations
substring = text.substring(0, 5); // "Hello"
subText = text.subText(7, 5); // "World"

// Trimming and cleaning
trimmed = text.trim();
alphaNumeric = text.getAlphaNumeric();
onlyAlpha = text.getAlpha();
```

#### String Replacement

```deluge
text = "Hello World Hello";

// Replace operations
allReplaced = text.replaceAll("Hello", "Hi");
firstReplaced = text.replaceFirst("Hello", "Hi");

// Regular expressions
hasNumbers = text.matches(".*\\d.*");
```

#### String Conversion

```deluge
// To other types
number = "123".toLong();
decimal = "123.45".toDecimal();

// To collections
charList = text.toList(); // List of characters
```

## Built-in Functions

deluge-compat includes implementations of common Deluge functions.

### HTTP Functions

#### GET Requests

```deluge
// Simple GET request
response = getUrl("https://api.example.com/data");

// GET with headers
headers = Map();
headers.put("Authorization", "Bearer token123");
headers.put("Content-Type", "application/json");
response = getUrl("https://api.example.com/data", headers);
```

#### POST Requests

```deluge
// Simple POST
data = Map();
data.put("name", "John");
data.put("email", "john@example.com");
response = postUrl("https://api.example.com/users", data);

// POST with headers
headers = Map();
headers.put("Authorization", "Bearer token123");
response = postUrl("https://api.example.com/users", data, headers);
```

#### Advanced HTTP with invokeurl

```deluge
// Complex HTTP requests
apiResponse = invokeurl
[
    url: "https://api.example.com/webhook"
    type: POST
    body: {
        "event": "user_signup",
        "user_id": userId,
        "timestamp": currentTime
    }
    headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + apiKey
    }
];
```

### Encoding Functions

```deluge
// Base64 encoding/decoding
originalText = "Hello World";
encoded = base64Encode(originalText);
decoded = base64Decode(encoded);

// URL encoding/decoding
url = "https://example.com/search?q=hello world";
encodedUrl = urlEncode(url);
decodedUrl = urlDecode(encodedUrl);

// HTML encoding/decoding
htmlText = "<div>Hello & welcome!</div>";
encodedHtml = htmlEncode(htmlText);
decodedHtml = htmlDecode(encodedHtml);
```

### Mathematical Functions

```deluge
// Basic math
result = randomNumber(1, 100); // Random between 1-100
absolute = abs(-42);
ceiling = ceil(3.14);
floor = floor(3.99);

// String to number conversion
intValue = toInt("123");
longValue = toLong("9876543210");
decimalValue = toDecimal("123.45");
hexValue = toHex(255); // "0xff"
```

### Utility Functions

```deluge
// Null checking
value = ifnull(possiblyNullValue, "default");

// Information logging
info("Processing user:", userId);
info("Current step:", stepNumber);

// Email (mock in testing)
sendmail
[
    from: "system@company.com"
    to: "admin@company.com"
    subject: "Process Complete"
    message: "The user signup process has completed successfully."
]
```

## Script Translation

deluge-compat can translate Deluge scripts to Python for inspection or integration.

### Command Line Translation

```bash
# Translate a script to Python
deluge-translate my_script.dg

# Save translated output
deluge-translate my_script.dg --output my_script.py

# Generate with PEP 723 metadata
deluge-translate my_script.dg --pep723
```

### Programmatic Translation

```python
from deluge_compat import DelugeTranslator

translator = DelugeTranslator()

deluge_code = '''
response = Map();
response.put("status", "success");
return response;
'''

python_code = translator.translate(deluge_code)
print(python_code)
```

## Error Handling

### Common Patterns

```deluge
// Safe value access
user = getUser(userId);
if(user != null) {
    name = user.get("name");
    if(name != null && name != "") {
        // Process name
        processUserName(name);
    }
}

// Safe API calls
try {
    apiResponse = getUrl("https://api.example.com/data");
    if(apiResponse != null) {
        data = apiResponse.getJSON("data");
        // Process data
    }
} catch(e) {
    info("API call failed:", e);
    // Handle error gracefully
}
```

### Validation Helpers

```deluge
// Check if collections are empty
if(!userList.isEmpty()) {
    // Process users
    for each user in userList {
        processUser(user);
    }
}

// Validate strings
if(!email.isEmpty() && email.contains("@")) {
    // Valid email format
    sendWelcomeEmail(email);
}
```

## Control Flow

### Conditional Logic

```deluge
age = user.get("age").toInt();

if(age < 18) {
    category = "minor";
} else if(age < 65) {
    category = "adult";
} else {
    category = "senior";
}

// Complex conditions
if(user.get("verified") == true && age >= 18 && !email.isEmpty()) {
    allowAccess = true;
} else {
    allowAccess = false;
}
```

### Loops

```deluge
// For each loop
users = getUserList();
for each user in users {
    name = user.get("name");
    email = user.get("email");
    sendNotification(email, "Welcome " + name);
}

// While loop
counter = 0;
while(counter < 10) {
    info("Processing step:", counter);
    counter = counter + 1;
}
```

## Best Practices

### 1. Data Validation

```deluge
// Always validate input data
function processUser(userData) {
    if(userData == null) {
        return Map({"error": "No user data provided"});
    }

    email = userData.get("email");
    if(email == null || email.isEmpty()) {
        return Map({"error": "Email is required"});
    }

    // Process valid data
    return Map({"status": "success"});
}
```

### 2. Error Handling

```deluge
// Graceful error handling
function fetchUserData(userId) {
    try {
        response = getUrl("https://api.example.com/users/" + userId);
        if(response != null) {
            return response;
        } else {
            return Map({"error": "No response from API"});
        }
    } catch(e) {
        info("API Error:", e);
        return Map({"error": "Failed to fetch user data"});
    }
}
```

### 3. Code Organization

```deluge
// Use functions for reusable logic
function buildUserResponse(user) {
    response = Map();
    response.put("id", user.get("id"));
    response.put("name", user.get("name"));
    response.put("email", user.get("email"));
    response.put("status", "active");
    return response;
}

// Main script logic
userId = request.get("user_id");
if(userId != null) {
    user = fetchUser(userId);
    if(user != null) {
        response = buildUserResponse(user);
    } else {
        response = Map({"error": "User not found"});
    }
} else {
    response = Map({"error": "User ID required"});
}

return response;
```

### 4. Performance Considerations

```deluge
// Batch operations when possible
userIds = List(["1", "2", "3", "4", "5"]);
users = List();

// Instead of individual API calls
for each userId in userIds {
    user = getUser(userId);
    if(user != null) {
        users.add(user);
    }
}

// Consider bulk operations when available
bulkUsers = getBulkUsers(userIds);
```

## Testing Your Scripts

### Using deluge-run

```bash
# Basic execution
deluge-run script.dg

# With debug output
deluge-run script.dg --debug

# Capture output
deluge-run script.dg > output.json
```

### Unit Testing Pattern

Create test scripts that validate your functions:

```deluge
// test_user_functions.dg
function testValidateEmail() {
    // Test valid email
    result = validateEmail("user@example.com");
    if(result.get("valid") != true) {
        return Map({"error": "Valid email test failed"});
    }

    // Test invalid email
    result = validateEmail("invalid-email");
    if(result.get("valid") != false) {
        return Map({"error": "Invalid email test failed"});
    }

    return Map({"status": "All email tests passed"});
}

// Run tests
emailTests = testValidateEmail();
info("Email tests:", emailTests);
```

## Common Patterns

### API Response Handling

```deluge
function processApiResponse(response) {
    result = Map();

    if(response == null) {
        result.put("success", false);
        result.put("error", "No response received");
        return result;
    }

    statusCode = response.get("statusCode");
    if(statusCode != null && statusCode == 200) {
        data = response.getJSON("data");
        result.put("success", true);
        result.put("data", data);
    } else {
        result.put("success", false);
        result.put("error", "API returned status: " + statusCode);
    }

    return result;
}
```

### Data Transformation

```deluge
function transformUserData(rawUser) {
    user = Map();

    // Extract and transform fields
    user.put("id", rawUser.get("user_id"));
    user.put("fullName", rawUser.get("first_name") + " " + rawUser.get("last_name"));
    user.put("email", rawUser.get("email_address").toLowerCase());

    // Handle optional fields
    phone = rawUser.get("phone_number");
    if(phone != null && !phone.isEmpty()) {
        user.put("phone", phone);
    }

    // Computed fields
    user.put("initials", getInitials(user.get("fullName")));

    return user;
}

function getInitials(fullName) {
    if(fullName == null || fullName.isEmpty()) {
        return "";
    }

    parts = fullName.split(" ");
    initials = "";

    for each part in parts {
        if(!part.isEmpty()) {
            initials = initials + part.substring(0, 1).toUpperCase();
        }
    }

    return initials;
}
```

## Troubleshooting

### Common Issues

1. **Null Reference Errors**
   ```deluge
   // Always check for null
   user = getUser(id);
   if(user != null) {
       name = user.get("name");
   }
   ```

2. **Type Conversion Issues**
   ```deluge
   // Ensure proper type conversion
   ageStr = user.get("age");
   if(ageStr != null && !ageStr.isEmpty()) {
       age = ageStr.toInt();
   }
   ```

3. **Empty Collection Handling**
   ```deluge
   // Check before iterating
   if(!users.isEmpty()) {
       for each user in users {
           processUser(user);
       }
   }
   ```

### Debug Output

```deluge
// Use info statements for debugging
info("Processing user ID:", userId);
info("User data:", user.toString());
info("Response size:", response.size());
```

## Next Steps

- For Zobot and SalesIQ development, see [Zobot Support Guide](ZOBOT_SUPPORT.md)
- For advanced features and API reference, see the project README
- For contributing to the project, see the development documentation

## Examples

Check the `examples/` directory for:
- `basic_operations.dg` - Data type operations
- `api_integration.dg` - HTTP API examples
- `data_processing.dg` - Common data patterns
- `error_handling.dg` - Error handling patterns
