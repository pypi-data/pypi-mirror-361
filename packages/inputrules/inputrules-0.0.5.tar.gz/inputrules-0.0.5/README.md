# InputRules - Input Rules Library 

**Version 0.0.5** - Enhanced security and stability improvements

Is an Alpha version, develop in progress, do not use it in production

---

## Installation

```bash
pip install inputrules
```
| **Total** | **Last Month** | **Last Week** |
|-----------|----------------|---------------|
| [![Downloads](https://static.pepy.tech/badge/inputrules)](https://pepy.tech/project/inputrules) | [![Downloads](https://static.pepy.tech/badge/inputrules/month)](https://pepy.tech/project/inputrules) | [![Downloads](https://static.pepy.tech/badge/inputrules/week)](https://pepy.tech/project/inputrules) |

---

A robust Python library for validating and sanitizing input data from Forms, JSON, and HTTP Requests with predefined rules and filters.

## Example
```python
from inputrules import InputRules

#JSON Example
data = {
        "id":100,
        "data": {
            "name":"  Alvaro ",
            "lastname":" De Leon  ",
            "age":35,
            "email": "asdasd",
            "opt":"30",
            "parms":[
                10,20,30,40,50,60,70,80,90,100
            ],
            "phones": {
                "name":"Zaraza",
                "home":"123456",
                "cell":"123456"
            }
        }
    }
#Example of list of options
options = ['10','20','30','40','50']

o = InputRules(data)

o.rules("id","required,integer")
o.rules("data.name","required,string","trim,upper")
o.rules("data.lastname","required,string","trim,lower")
o.rules("data.age","required,integer")
o.rules("data.phone","string")
o.rules("data.email","string","b64encode")
o.rules("data.opt","options",options=options)
o.rules("data.phones.name","required,string")

if o.verify():
    print("Data is valid")
    data = o.data()
    print(data)
```

## Data Validation with InputRules

InputRules provides a powerful data validation system through the `InputRules` class. This class allows you to validate input data in a structured way and apply filters automatically.

### Importing

```python
from inputrules import InputRules, check
```

### Basic Usage

```python
# Example data
data = {
    "id": 100,
    "name": "  John  ",
    "email": "john@example.com",
    "age": 25,
    "status": "active"
}

# Create InputRules instance
validator = InputRules(data)

# Define validation rules
validator.rules("id", "required,integer")
validator.rules("name", "required,string", "trim,upper")
validator.rules("email", "required,mail")
validator.rules("age", "required,integer")
validator.rules("status", "required,options", options=["active", "inactive"])

# Validate data
if validator.verify():
    print("Data is valid")
    validated_data = validator.data()
    print(validated_data)
else:
    print("Errors found:")
    for error in validator.errors():
        print(f"- {error}")
```

### Available Validation Rules

#### Basic Rules
- `required`: Field is required
- `string`: Must be a string
- `integer`: Must be an integer
- `float`: Must be a decimal number
- `numeric`: Must be a number (integer or decimal)
- `empty`: Must be empty
- `!empty`: Must not be empty
- `none`: Must be None
- `!none`: Must not be None

#### Format Rules
- `mail`: Must be a valid email address
- `domain`: Must be a valid domain
- `ip`: Must be a valid IP address
- `uuid`: Must be a valid UUID
- `options`: Must be in a list of valid options

### Available Filters

Filters are automatically applied to data after validation:

#### Text Filters
- `trim` or `strip`: Removes whitespace from beginning and end
- `lower`: Converts to lowercase
- `upper`: Converts to uppercase
- `ucfirst`: First letter uppercase
- `ucwords`: First letter of each word uppercase

#### Conversion Filters
- `int` or `integer`: Converts to integer
- `float`: Converts to decimal
- `str` or `string`: Converts to string

#### Encoding Filters
- `base64` or `b64encode`: Encodes in base64
- `b64decode`: Decodes from base64
- `md5`: Generates MD5 hash
- `urlencode`: Encodes for URL
- `urldecode`: Decodes from URL

#### Security Filters
- `xss` or `escape`: Escapes HTML characters
- `sql`: Sanitizes SQL input (removes dangerous SQL injection patterns)
- `htmlentities`: Converts characters to HTML entities
- `htmlspecialchars`: Converts special characters to HTML entities
- `striptags`: Removes HTML tags
- `addslashes`: Escapes quotes and backslashes
- `stripslashes`: Removes backslashes

#### Format Filters
- `nl2br`: Converts line breaks to `<br>`
- `br2nl`: Converts `<br>` to line breaks
- `json`: Converts to JSON

**Note**: The `serialize` and `unserialize` filters have been removed for security reasons.

### Nested Structure Validation

`InputRules` supports validation of nested data structures using dot notation:

```python
data = {
    "user": {
        "profile": {
            "name": "  Maria  ",
            "email": "maria@example.com",
            "age": 30
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
}

validator = InputRules(data)

# Validate nested fields
validator.rules("user.profile.name", "required,string", "trim,ucfirst")
validator.rules("user.profile.email", "required,mail")
validator.rules("user.profile.age", "required,integer")
validator.rules("user.settings.theme", "required,options", options=["light", "dark"])
validator.rules("user.settings.notifications", "required")

if validator.verify():
    validated_data = validator.data()
    print(validated_data)
```

### Complete Example with Options

```python
from inputrules import InputRules

# Form data
form_data = {
    "username": "  admin  ",
    "password": "123456",
    "email": "admin@example.com",
    "role": "admin",
    "profile": {
        "first_name": "  john  ",
        "last_name": "  doe  ",
        "age": 35,
        "country": "US"
    }
}

# Valid options
role_options = ["admin", "user", "moderator"]
country_options = ["US", "CA", "UK", "DE", "FR"]

# Create validator
validator = InputRules(form_data)

# Define rules
validator.rules("username", "required,string", "trim,lower")
validator.rules("password", "required,string", "md5")
validator.rules("email", "required,mail")
validator.rules("role", "required,options", options=role_options)
validator.rules("profile.first_name", "required,string", "trim,ucfirst")
validator.rules("profile.last_name", "required,string", "trim,ucfirst")
validator.rules("profile.age", "required,integer")
validator.rules("profile.country", "required,options", options=country_options)

# Validate
if validator.verify():
    print("✓ Valid data")
    clean_data = validator.data()
    print("Processed data:", clean_data)
else:
    print("✗ Validation errors:")
    for error in validator.errors():
        print(f"  - {error}")
```

## check Class - Individual Validations

The `check` class provides static methods for validating individual values. It's useful for specific validations without needing to create a complete schema.

### Importing

```python
from inputrules import check
```

### Validation Methods

#### Type Validation
```python
# Validate if it's a string
check.string("text")        # True
check.string(123)           # False

# Validate if it's an integer
check.integer(42)           # True
check.integer(3.14)         # False

# Validate if it's a decimal
check.float(3.14)           # True
check.float(42)             # False

# Validate if it's numeric (integer or decimal)
check.numeric(42)           # True
check.numeric(3.14)         # True
check.numeric("text")       # False
```

#### State Validation
```python
# Validate if it's empty
check.empty("")             # True
check.empty(None)           # True
check.empty(0)              # True
check.empty("text")         # False

# Validate if it's None
check.none(None)            # True
check.none("")              # False

# Validate if it's NOT None
check.notnone("text")       # True
check.notnone(None)         # False
```

#### Format Validation
```python
# Validate email
check.mail("user@example.com")      # True
check.mail("invalid-email")         # False

# Validate domain
check.domain("example.com")         # True
check.domain("invalid..domain")     # False

# Validate IP
check.ip("192.168.1.1")            # True
check.ip("999.999.999.999")        # False

# Validate UUID
check.uuid("123e4567-e89b-12d3-a456-426614174000")  # True
check.uuid("invalid-uuid")                          # False
```

#### Options Validation
```python
# Validate if it's in a list of options
options = ["red", "green", "blue"]
check.options("red", options)       # True
check.options("yellow", options)    # False
```

#### Validation with Multiple Rules
```python
# Use multiple rules separated by commas
check.rules("john@example.com", "required,mail")    # True
check.rules("", "required,string")                  # False
check.rules(25, "required,integer")                 # True
check.rules("test", "required,string,!empty")       # True
```

### Data Sanitization

```python
# Sanitize SQL input
user_input = "'; DROP TABLE users; --"
safe_input = check.sanitize_sql(user_input)
print(safe_input)  # " DROP TABLE users "
```

### Practical Examples

#### Registration Form Validation
```python
from inputrules import check

def validate_registration(form_data):
    errors = []
    
    # Validate username
    if not check.rules(form_data.get('username'), 'required,string,!empty'):
        errors.append("Username is required and must be valid")
    
    # Validate email
    if not check.rules(form_data.get('email'), 'required,mail'):
        errors.append("Email must be a valid address")
    
    # Validate age
    if not check.rules(form_data.get('age'), 'required,integer'):
        errors.append("Age must be an integer")
    
    # Validate role
    valid_roles = ['admin', 'user', 'moderator']
    if not check.options(form_data.get('role'), valid_roles):
        errors.append("Role must be admin, user or moderator")
    
    return len(errors) == 0, errors

# Usage
form_data = {
    'username': 'john_doe',
    'email': 'john@example.com',
    'age': 28,
    'role': 'user'
}

is_valid, errors = validate_registration(form_data)
if is_valid:
    print("Valid form")
else:
    print("Errors:", errors)
```

#### Configuration Validation
```python
from inputrules import check

def validate_config(config):
    """Validates system configuration"""
    
    # Validate database host
    if not check.rules(config.get('db_host'), 'required,string,!empty'):
        return False, "Database host is required"
    
    # Validate port
    port = config.get('db_port')
    if not check.integer(port) or port <= 0 or port > 65535:
        return False, "Port must be an integer between 1 and 65535"
    
    # Validate admin email
    admin_email = config.get('admin_email')
    if not check.mail(admin_email):
        return False, "Admin email is not valid"
    
    # Validate log level
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if not check.options(config.get('log_level'), log_levels):
        return False, "Log level must be DEBUG, INFO, WARNING or ERROR"
    
    return True, "Valid configuration"

# Usage
config = {
    'db_host': 'localhost',
    'db_port': 3306,
    'admin_email': 'admin@company.com',
    'log_level': 'INFO'
}

is_valid, message = validate_config(config)
print(message)
```

### Integration Example

```python
from inputrules import InputRules, check

# User data
user_data = {
    'name': '  John Doe  ',
    'email': 'john@example.com',
    'age': 30,
    'status': 'active'
}

# Validate data
validator = InputRules(user_data)
validator.rules("name", "required,string", "trim,ucfirst")
validator.rules("email", "required,mail")
validator.rules("age", "required,integer")
validator.rules("status", "required,options", options=["active", "inactive"])

if validator.verify():
    # Valid data, process it
    clean_data = validator.data()
    print(f"Validated data: {clean_data}")
else:
    print("Validation errors:")
    for error in validator.errors():
        print(f"- {error}")
```

## Security Improvements

### Version 0.0.5 Security Enhancements

- **Removed unsafe `serialize`/`unserialize` filters**: These filters used Python's `pickle` module which could execute arbitrary code with untrusted input
- **Enhanced SQL injection protection**: The `sql` filter now removes more dangerous patterns including:
  - DROP TABLE, DELETE FROM, INSERT INTO, UPDATE SET
  - SQL comments (-- and /* */)
  - UNION SELECT attacks
  - OR 1=1 patterns
- **Improved `addslashes` filter**: Now properly escapes single quotes, double quotes, and backslashes
- **Fixed `urlencode` filter**: Removed double encoding issue

### Empty Function Improvements

The `empty()` function now correctly handles all data types:
- Collections (lists, dicts, tuples, sets): empty if length is 0
- Booleans: `False` is considered a valid value, not empty
- Numbers: 0 and 0.0 are considered empty
- Strings: empty or whitespace-only strings are considered empty

## Bug Fixes in Version 0.0.4

- **Fixed class variable sharing**: Each `InputRules` instance now has independent variables
- **Improved error handling**: Better handling of missing keys in nested structures
- **Enhanced `getValue()` function**: Now returns `None` instead of raising exceptions
- **Fixed validation schema**: Better handling of nested structures and missing data




This documentation provides a complete guide for using both `InputRules` and the `check` class, allowing you to validate and sanitize data robustly and securely.
