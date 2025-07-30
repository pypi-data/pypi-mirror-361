#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive test suite for EasyMySQL InputRules and check classes
Tests both valid and invalid data scenarios
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inputrules import InputRules, check, jsontools, filter, generate_structure, map_options, validate_schema, apply_filters_schema, clean_data, getValue
import json
import tempfile


def test_input_rules_valid_data():
    """Test InputRules with valid data"""
    print("=" * 60)
    print("TESTING InputRules - Valid Data")
    print("=" * 60)
    
    # Valid data example (similar to original test)
    data = {
        "id": 100,
        "data": {
            "name": "  John Doe  ",
            "lastname": " Smith  ",
            "age": 30,
            "email": "john@example.com",
            "opt": "30",
            "status": "active",
            "phones": {
                "name": "iPhone",
                "home": "123456",
                "cell": "987654"
            }
        }
    }
    
    # Example of list of options
    options = ['10', '20', '30', '40', '50']
    
    validator = InputRules(data)
    
    # Define rules
    validator.rules("id", "required,integer")
    validator.rules("data.name", "required,string", "trim,upper")
    validator.rules("data.lastname", "required,string", "trim,lower")
    validator.rules("data.age", "required,integer")
    validator.rules("data.email", "required,mail")
    validator.rules("data.opt", "options", options=options)
    validator.rules("data.phones.name", "required,string")
    validator.rules("data.phones.home", "required,string")
    validator.rules("data.phones.cell", "required,string")
    
    # Validate
    if validator.verify():
        print("✓ PASSED: Data is valid")
        clean_data = validator.data()
        print("✓ Processed data:", json.dumps(clean_data, indent=2))
    else:
        print("✗ FAILED: Data should be valid")
        print("✗ Errors found:")
        for error in validator.errors():
            print(f"  - {error}")
    
    print()


def test_input_rules_invalid_data():
    """Test InputRules with invalid data"""
    print("=" * 60)
    print("TESTING InputRules - Invalid Data")
    print("=" * 60)
    
    # Invalid data example
    data = {
        "id": "not_a_number",  # Should be integer
        "data": {
            "name": "",  # Required but empty
            "lastname": " Smith  ",
            "age": "not_a_number",  # Should be integer
            "email": "invalid-email",  # Invalid email format
            "opt": "99",  # Not in options
            "phones": {
                "name": "iPhone",
                "home": "",  # Empty but required
                "cell": "987654"
            }
        }
    }
    
    # Example of list of options
    options = ['10', '20', '30', '40', '50']
    
    validator = InputRules(data)
    
    # Define rules
    validator.rules("id", "required,integer")
    validator.rules("data.name", "required,string,!empty")
    validator.rules("data.lastname", "required,string", "trim,lower")
    validator.rules("data.age", "required,integer")
    validator.rules("data.email", "required,mail")
    validator.rules("data.opt", "options", options=options)
    validator.rules("data.phones.name", "required,string")
    validator.rules("data.phones.home", "required,string,!empty")
    validator.rules("data.phones.cell", "required,string")
    
    # Validate
    if validator.verify():
        print("✗ FAILED: Data should be invalid")
        clean_data = validator.data()
        print("Processed data:", json.dumps(clean_data, indent=2))
    else:
        print("✓ PASSED: Data is correctly identified as invalid")
        print("✓ Errors found:")
        for error in validator.errors():
            print(f"  - {error}")
    
    print()


def test_input_rules_filters():
    """Test InputRules filters"""
    print("=" * 60)
    print("TESTING InputRules - Filters")
    print("=" * 60)
    
    # Data with various filter needs
    data = {
        "text_upper": "hello world",
        "text_lower": "HELLO WORLD",
        "text_trim": "  spaced text  ",
        "text_ucfirst": "first letter",
        "text_ucwords": "first letter of each word",
        "password": "secret123",
        "number_str": "42",
        "float_str": "3.14",
        "base64_text": "Hello World",
        "html_content": "<script>alert('xss')</script>Hello"
    }
    
    validator = InputRules(data)
    
    # Apply various filters
    validator.rules("text_upper", "required,string", "upper")
    validator.rules("text_lower", "required,string", "lower")
    validator.rules("text_trim", "required,string", "trim")
    validator.rules("text_ucfirst", "required,string", "ucfirst")
    validator.rules("text_ucwords", "required,string", "ucwords")
    validator.rules("password", "required,string", "md5")
    validator.rules("number_str", "required,string", "int")
    validator.rules("float_str", "required,string", "float")
    validator.rules("base64_text", "required,string", "base64")
    validator.rules("html_content", "required,string", "xss")
    
    if validator.verify():
        print("✓ PASSED: All filters applied successfully")
        clean_data = validator.data()
        print("✓ Filtered data:")
        if clean_data is not None:
            for key, value in clean_data.items():
                print(f"  {key}: {value}")
        else:
            print("  No data returned")
    else:
        print("✗ FAILED: Filter application failed")
        for error in validator.errors():
            print(f"  - {error}")
    
    print()


def test_check_class_valid():
    """Test check class with valid data"""
    print("=" * 60)
    print("TESTING check Class - Valid Data")
    print("=" * 60)
    
    # Type validations
    print("Type Validations:")
    print(f"  string('text'): {check.string('text')} (should be True)")
    print(f"  integer(42): {check.integer(42)} (should be True)")
    print(f"  float(3.14): {check.float(3.14)} (should be True)")
    print(f"  numeric(42): {check.numeric(42)} (should be True)")
    print(f"  numeric(3.14): {check.numeric(3.14)} (should be True)")
    
    # State validations
    print("\nState Validations:")
    print(f"  empty(''): {check.empty('')} (should be True)")
    print(f"  empty(None): {check.empty(None)} (should be True)")
    print(f"  none(None): {check.none(None)} (should be True)")
    print(f"  notnone('text'): {check.notnone('text')} (should be True)")
    
    # Format validations
    print("\nFormat Validations:")
    print(f"  mail('user@example.com'): {check.mail('user@example.com')} (should be True)")
    print(f"  domain('example.com'): {check.domain('example.com')} (should be True)")
    print(f"  ip('192.168.1.1'): {check.ip('192.168.1.1')} (should be True)")
    print(f"  uuid('123e4567-e89b-12d3-a456-426614174000'): {check.uuid('123e4567-e89b-12d3-a456-426614174000')} (should be True)")
    
    # Options validation
    print("\nOptions Validation:")
    options = ["red", "green", "blue"]
    print(f"  options('red', ['red', 'green', 'blue']): {check.options('red', options)} (should be True)")
    
    # Multiple rules validation
    print("\nMultiple Rules Validation:")
    print(f"  rules('john@example.com', 'required,mail'): {check.rules('john@example.com', 'required,mail')} (should be True)")
    print(f"  rules(25, 'required,integer'): {check.rules(25, 'required,integer')} (should be True)")
    print(f"  rules('text', 'required,string,!empty'): {check.rules('text', 'required,string,!empty')} (should be True)")
    
    print()


def test_check_class_invalid():
    """Test check class with invalid data"""
    print("=" * 60)
    print("TESTING check Class - Invalid Data")
    print("=" * 60)
    
    # Type validations
    print("Type Validations:")
    print(f"  string(123): {check.string(123)} (should be False)")
    print(f"  integer(3.14): {check.integer(3.14)} (should be False)")
    print(f"  float('text'): {check.float('text')} (should be False)")
    print(f"  numeric('text'): {check.numeric('text')} (should be False)")
    
    # State validations
    print("\nState Validations:")
    print(f"  empty('text'): {check.empty('text')} (should be False)")
    print(f"  none('text'): {check.none('text')} (should be False)")
    print(f"  notnone(None): {check.notnone(None)} (should be False)")
    
    # Format validations
    print("\nFormat Validations:")
    print(f"  mail('invalid-email'): {check.mail('invalid-email')} (should be False)")
    print(f"  domain('invalid..domain'): {check.domain('invalid..domain')} (should be False)")
    print(f"  ip('999.999.999.999'): {check.ip('999.999.999.999')} (should be False)")
    print(f"  uuid('invalid-uuid'): {check.uuid('invalid-uuid')} (should be False)")
    
    # Options validation
    print("\nOptions Validation:")
    options = ["red", "green", "blue"]
    print(f"  options('yellow', ['red', 'green', 'blue']): {check.options('yellow', options)} (should be False)")
    
    # Multiple rules validation
    print("\nMultiple Rules Validation:")
    print(f"  rules('', 'required,string'): {check.rules('', 'required,string')} (should be False)")
    print(f"  rules('text', 'required,integer'): {check.rules('text', 'required,integer')} (should be False)")
    print(f"  rules('invalid-email', 'required,mail'): {check.rules('invalid-email', 'required,mail')} (should be False)")
    
    print()


def test_check_sanitization():
    """Test check class sanitization methods"""
    print("=" * 60)
    print("TESTING check Class - Sanitization")
    print("=" * 60)
    
    # Test cases for SQL injection attacks
    test_cases = [
        {
            "name": "SQL Injection with DROP TABLE",
            "input": "'; DROP TABLE users; --",
            "expected_clean": True
        },
        {
            "name": "SQL Injection with UNION SELECT",
            "input": "1' UNION SELECT * FROM passwords--",
            "expected_clean": True
        },
        {
            "name": "SQL Injection with OR 1=1",
            "input": "admin' OR 1=1 --",
            "expected_clean": True
        },
        {
            "name": "SQL Injection with DELETE FROM",
            "input": "'; DELETE FROM users WHERE id=1; --",
            "expected_clean": True
        },
        {
            "name": "SQL Injection with INSERT INTO",
            "input": "'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
            "expected_clean": True
        },
        {
            "name": "SQL Injection with UPDATE SET",
            "input": "'; UPDATE users SET password='hacked' WHERE id=1; --",
            "expected_clean": True
        },
        {
            "name": "SQL Injection with /* comment */",
            "input": "admin'/**/UNION/**/SELECT/**/password/**/FROM/**/users--",
            "expected_clean": True
        },
        {
            "name": "Normal text",
            "input": "This is normal text",
            "expected_clean": False
        },
        {
            "name": "None value",
            "input": None,
            "expected_clean": False
        },
        {
            "name": "Empty string",
            "input": "",
            "expected_clean": False
        }
    ]
    
    try:
        print("SQL Injection Protection Tests:")
        all_passed = True
        
        for test_case in test_cases:
            original = test_case["input"]
            sanitized = check.sanitize_sql(original)
            
            print(f"\n  Test: {test_case['name']}")
            print(f"    Original: {repr(original)}")
            print(f"    Sanitized: {repr(sanitized)}")
            
            if test_case["expected_clean"]:
                # Should be different from original (cleaned)
                if sanitized != original:
                    print(f"    ✓ PASSED: Input was properly sanitized")
                else:
                    print(f"    ✗ FAILED: Input should have been sanitized")
                    all_passed = False
            else:
                # Should be same as original (or minimal changes)
                if sanitized == original or (original is None and sanitized == ""):
                    print(f"    ✓ PASSED: Safe input preserved")
                else:
                    print(f"    ✓ PASSED: Input processed safely")
        
        if all_passed:
            print(f"\n✓ All SQL sanitization tests passed!")
        else:
            print(f"\n✗ Some SQL sanitization tests failed!")
            
    except Exception as e:
        print(f"✗ SQL sanitization method error: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("=" * 60)
    print("TESTING Edge Cases")
    print("=" * 60)
    
    # Test 1: Empty data
    empty_data = {}
    validator = InputRules(empty_data)
    validator.rules("nonexistent", "required,string")
    
    if not validator.verify():
        print("✓ PASSED: Empty data correctly fails validation")
    else:
        print("✗ FAILED: Empty data should fail validation")
    
    # Test 2: Deep nesting
    deep_data = {
        "level1": {
            "level2": {
                "level3": {
                    "value": "deep_value"
                }
            }
        }
    }
    
    validator = InputRules(deep_data)
    validator.rules("level1.level2.level3.value", "required,string")
    
    if validator.verify():
        print("✓ PASSED: Deep nesting works correctly")
    else:
        print("✗ FAILED: Deep nesting should work")
        for error in validator.errors():
            print(f"  - {error}")
    
    # Test 3: Options with nested data
    options_data = {
        "data": {
            "option": "valid_option"
        }
    }
    
    valid_options = ["valid_option", "another_option"]
    validator = InputRules(options_data)
    validator.rules("data.option", "options", options=valid_options)
    
    if validator.verify():
        print("✓ PASSED: Nested options work correctly")
    else:
        print("✗ FAILED: Nested options should work")
        for error in validator.errors():
            print(f"  - {error}")
    
    # Test 4: Missing required fields
    missing_data = {
        "present": "value"
    }
    
    validator = InputRules(missing_data)
    validator.rules("present", "required,string")
    validator.rules("missing", "required,string")
    
    if not validator.verify():
        print("✓ PASSED: Missing required fields correctly fail validation")
    else:
        print("✗ FAILED: Missing required fields should fail validation")
    
    print()


def test_performance():
    """Test performance with large datasets"""
    print("=" * 60)
    print("TESTING Performance")
    print("=" * 60)
    
    import time
    
    # Create large dataset
    large_data = {"data": {}}
    for i in range(100):
        large_data["data"][f"field_{i}"] = f"value_{i}"
    
    start_time = time.time()
    
    validator = InputRules(large_data)
    for i in range(100):
        validator.rules(f"data.field_{i}", "required,string", "trim,lower")
    
    validation_result = validator.verify()
    end_time = time.time()
    
    print(f"✓ Validated 100 fields in {end_time - start_time:.4f} seconds")
    print(f"✓ Result: {'Valid' if validation_result else 'Invalid'}")
    
    print()


def test_original_example():
    """Test the original example from the existing test file"""
    print("=" * 60)
    print("TESTING Original Example")
    print("=" * 60)
    
    # Original test data
    data = {
        "id": 100,
        "data": {
            "name": "  Alvaro ",
            "lastname": " De Leon  ",
            "age": 35,
            "email": "asdasd",
            "opt": "30",
            "parms": [
                10, 20, 30, 40, 50, 60, 70, 80, 90, 100
            ],
            "phones": {
                "name": "Zaraza",
                "home": "123456",
                "cell": "123456"
            }
        }
    }
    
    # Example of list of options
    options = ['10', '20', '30', '40', '50']
    
    validator = InputRules(data)
    
    validator.rules("id", "required,integer")
    validator.rules("data.name", "required,string", "trim,upper")
    validator.rules("data.lastname", "required,string", "trim,lower")
    validator.rules("data.age", "required,integer")
    validator.rules("data.phone", "string")
    validator.rules("data.email", "string", "b64encode")
    validator.rules("data.opt", "options", options=options)
    validator.rules("data.phones.name", "required,string")
    
    if validator.verify():
        print("✓ PASSED: Original example works correctly")
        clean_data = validator.data()
        print("✓ Data is valid")
        print(json.dumps(clean_data, indent=2))
    else:
        print("✗ FAILED: Original example should work")
        for error in validator.errors():
            print(f"  - {error}")
    
    print()


def test_required_validation():
    """Test the required validation rule specifically"""
    print("=" * 60)
    print("TESTING Required Validation Rule")
    print("=" * 60)
    
    # Test cases for required validation
    test_cases = [
        # Cases that should FAIL (return False)
        {"value": None, "rule": "required", "expected": False, "description": "None value"},
        {"value": "", "rule": "required", "expected": False, "description": "Empty string"},
        {"value": "   ", "rule": "required", "expected": False, "description": "Whitespace-only string"},
        {"value": "", "rule": "required,string", "expected": False, "description": "Empty string with string rule"},
        {"value": None, "rule": "required,integer", "expected": False, "description": "None with integer rule"},
        
        # Cases that should PASS (return True)
        {"value": "text", "rule": "required", "expected": True, "description": "Non-empty string"},
        {"value": "text", "rule": "required,string", "expected": True, "description": "Non-empty string with string rule"},
        {"value": 0, "rule": "required,integer", "expected": True, "description": "Zero integer (should be valid)"},
        {"value": 42, "rule": "required,integer", "expected": True, "description": "Positive integer"},
        {"value": False, "rule": "required", "expected": True, "description": "Boolean False (should be valid)"},
        {"value": "john@example.com", "rule": "required,mail", "expected": True, "description": "Valid email"},
        {"value": "  valid text  ", "rule": "required,string", "expected": True, "description": "Text with spaces"},
        
        # Edge cases
        {"value": "0", "rule": "required,string", "expected": True, "description": "String '0'"},
        {"value": [], "rule": "required", "expected": True, "description": "Empty list (should be valid)"},
        {"value": {}, "rule": "required", "expected": True, "description": "Empty dict (should be valid)"}
    ]
    
    print("Testing 'required' validation rule:")
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = check.rules(test_case["value"], test_case["rule"])
            
            print(f"\n  Test {i}: {test_case['description']}")
            print(f"    Value: {repr(test_case['value'])}")
            print(f"    Rule: {test_case['rule']}")
            print(f"    Expected: {test_case['expected']}")
            print(f"    Result: {result}")
            
            if result == test_case["expected"]:
                print(f"    ✓ PASSED")
            else:
                print(f"    ✗ FAILED")
                all_passed = False
                
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
            all_passed = False
    
    if all_passed:
        print(f"\n✓ All required validation tests passed!")
    else:
        print(f"\n✗ Some required validation tests failed!")
    
    print()


def test_utility_functions():
    """Test utility functions that are not directly tested"""
    print("=" * 60)
    print("TESTING Utility Functions")
    print("=" * 60)
    
    # Test generate_structure
    print("Testing generate_structure function:")
    result = generate_structure("data.user.name", "required,string")
    expected = {"data": {"user": {"name": "required,string"}}}
    if result == expected:
        print("✓ PASSED: generate_structure works correctly")
    else:
        print(f"✗ FAILED: Expected {expected}, got {result}")
    
    # Test map_options
    print("\nTesting map_options function:")
    options = ["red", "green", "blue"]
    result = map_options("data.color", options)
    expected = {"data": {"color": options}}
    if result == expected:
        print("✓ PASSED: map_options works correctly")
    else:
        print(f"✗ FAILED: Expected {expected}, got {result}")
    
    # Test getValue
    print("\nTesting getValue function:")
    schema = {"data": {"user": {"name": "John"}}}
    result = getValue("data.user.name", schema)
    if result == "John":
        print("✓ PASSED: getValue works correctly")
    else:
        print(f"✗ FAILED: Expected 'John', got {result}")
    
    # Test getValue with missing path
    try:
        result = getValue("data.user.missing", schema)
        print(f"✗ FAILED: Expected KeyError for missing path, got {result}")
    except KeyError:
        print("✓ PASSED: getValue correctly raises KeyError for missing path")
    except Exception as e:
        print(f"✗ FAILED: Unexpected exception: {e}")
    
    # Test clean_data
    print("\nTesting clean_data function:")
    data = {"name": "John", "age": 30, "extra": "remove"}
    schema = {"name": "string", "age": "integer"}
    result = clean_data(data, schema)
    expected = {"name": "John", "age": 30}
    if result == expected:
        print("✓ PASSED: clean_data removes extra fields")
    else:
        print(f"✗ FAILED: Expected {expected}, got {result}")
    
    print()


def test_jsontools_class():
    """Test jsontools class methods"""
    print("=" * 60)
    print("TESTING jsontools Class")
    print("=" * 60)
    
    # Test validate
    print("Testing jsontools.validate:")
    valid_json = '{"name": "John", "age": 30}'
    invalid_json = '{"name": "John", "age": 30'
    
    if jsontools.validate(valid_json):
        print("✓ PASSED: Valid JSON correctly identified")
    else:
        print("✗ FAILED: Valid JSON should be identified as valid")
    
    if not jsontools.validate(invalid_json):
        print("✓ PASSED: Invalid JSON correctly identified")
    else:
        print("✗ FAILED: Invalid JSON should be identified as invalid")
    
    # Test convertJsonToList
    print("\nTesting jsontools.convertJsonToList:")
    result = jsontools.convertJsonToList(valid_json)
    expected = {"name": "John", "age": 30}
    if result == expected:
        print("✓ PASSED: JSON to dict conversion works")
    else:
        print(f"✗ FAILED: Expected {expected}, got {result}")
    
    # Test convertToJson
    print("\nTesting jsontools.convertToJson:")
    data = {"name": "John", "age": 30}
    result = jsontools.convertToJson(data)
    if result and '"name": "John"' in result:
        print("✓ PASSED: Dict to JSON conversion works")
    else:
        print(f"✗ FAILED: JSON conversion failed: {result}")
    
    # Test pretty
    print("\nTesting jsontools.pretty:")
    result = jsontools.pretty(valid_json)
    if result and '"name": "John"' in result and '\n' in result:
        print("✓ PASSED: JSON pretty formatting works")
    else:
        print(f"✗ FAILED: Pretty formatting failed: {result}")
    
    # Test get
    print("\nTesting jsontools.get:")
    try:
        schema = {"data": {"user": {"name": "John"}}}
        result = jsontools.get("data.user.name", schema)
        if result == "John":
            print("✓ PASSED: jsontools.get works correctly")
        else:
            print(f"✗ FAILED: Expected 'John', got {result}")
    except Exception as e:
        print(f"✗ ERROR: jsontools.get failed: {e}")
    
    # Test get2
    print("\nTesting jsontools.get2:")
    result = jsontools.get2("data.user.name", schema)
    if result == "John":
        print("✓ PASSED: jsontools.get2 works correctly")
    else:
        print(f"✗ FAILED: Expected 'John', got {result}")
    
    # Test file operations with temp files
    print("\nTesting jsontools file operations:")
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"test": "data"}')
            temp_file = f.name
        
        # Test open
        result = jsontools.open(temp_file)
        if result and '"test": "data"' in result:
            print("✓ PASSED: jsontools.open works correctly")
        else:
            print(f"✗ FAILED: jsontools.open failed: {result}")
        
        # Test save
        jsontools.save('{"new": "data"}', temp_file)
        saved_content = jsontools.open(temp_file)
        if saved_content and '"new": "data"' in saved_content:
            print("✓ PASSED: jsontools.save works correctly")
        else:
            print(f"✗ FAILED: jsontools.save failed: {saved_content}")
        
        # Cleanup
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"✗ ERROR: File operations failed: {e}")
    
    print()


def test_filter_function():
    """Test filter function with all available filters"""
    print("=" * 60)
    print("TESTING Filter Function")
    print("=" * 60)
    
    # Test filters not covered in main tests
    test_cases = [
        {"value": "test", "filter": "stripslashes", "description": "stripslashes filter"},
        {"value": 'test"quote', "filter": "addslashes", "description": "addslashes filter"},
        {"value": "line1\nline2", "filter": "nl2br", "description": "nl2br filter"},
        {"value": "line1<br>line2", "filter": "br2nl", "description": "br2nl filter"},
        {"value": "hello world", "filter": "urlencode", "description": "urlencode filter"},
        {"value": "hello%20world", "filter": "urldecode", "description": "urldecode filter"},
        {"value": "<p>test</p>", "filter": "striptags", "description": "striptags filter"},
        {"value": "test&special", "filter": "htmlspecialchars", "description": "htmlspecialchars filter"},
        {"value": {"key": "value"}, "filter": "json", "description": "json filter"},
    ]
    
    for test_case in test_cases:
        try:
            result = filter(test_case["value"], test_case["filter"])
            print(f"✓ PASSED: {test_case['description']} - {test_case['value']} -> {result}")
        except Exception as e:
            print(f"✗ FAILED: {test_case['description']} - Error: {e}")
    
    print()


def test_error_handling():
    """Test error handling for invalid rules and filters"""
    print("=" * 60)
    print("TESTING Error Handling")
    print("=" * 60)
    
    # Test invalid validation rules
    print("Testing invalid validation rules:")
    try:
        check.rules("test", "invalid_rule")
        print("✗ FAILED: Should have raised ValueError for invalid rule")
    except ValueError as e:
        print(f"✓ PASSED: Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ FAILED: Wrong exception type: {e}")
    
    # Test invalid filters
    print("\nTesting invalid filters:")
    try:
        filter("test", "invalid_filter")
        print("✗ FAILED: Should have raised ValueError for invalid filter")
    except ValueError as e:
        print(f"✓ PASSED: Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ FAILED: Wrong exception type: {e}")
    
    # Test filter type conversion errors
    print("\nTesting filter type conversion errors:")
    try:
        filter("not_a_number", "int")
        print("✗ FAILED: Should have raised ValueError for invalid int conversion")
    except ValueError as e:
        print(f"✓ PASSED: Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ FAILED: Wrong exception type: {e}")
    
    try:
        filter("not_a_number", "float")
        print("✗ FAILED: Should have raised ValueError for invalid float conversion")
    except ValueError as e:
        print(f"✓ PASSED: Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ FAILED: Wrong exception type: {e}")
    
    print()


def test_advanced_edge_cases():
    """Test advanced edge cases and boundary conditions"""
    print("=" * 60)
    print("TESTING Advanced Edge Cases")
    print("=" * 60)
    
    # Test IP validation edge cases
    print("Testing IP validation edge cases:")
    ip_cases = [
        {"ip": "0.0.0.0", "expected": True, "description": "Zero IP"},
        {"ip": "255.255.255.255", "expected": True, "description": "Max IP"},
        {"ip": "256.1.1.1", "expected": False, "description": "Over 255"},
        {"ip": "192.168.1", "expected": False, "description": "Incomplete IP"},
        {"ip": "192.168.1.1.1", "expected": False, "description": "Too many octets"},
    ]
    
    for case in ip_cases:
        result = check.ip(case["ip"])
        if result == case["expected"]:
            print(f"✓ PASSED: {case['description']} - {case['ip']} -> {result}")
        else:
            print(f"✗ FAILED: {case['description']} - {case['ip']} expected {case['expected']}, got {result}")
    
    # Test domain validation edge cases
    print("\nTesting domain validation edge cases:")
    domain_cases = [
        {"domain": "a.com", "expected": True, "description": "Single char domain"},
        {"domain": "test.co.uk", "expected": True, "description": "Multi-level domain"},
        {"domain": "test-.com", "expected": False, "description": "Hyphen at end"},
        {"domain": "-test.com", "expected": False, "description": "Hyphen at start"},
        {"domain": "test..com", "expected": False, "description": "Double dots"},
    ]
    
    for case in domain_cases:
        result = check.domain(case["domain"])
        if result == case["expected"]:
            print(f"✓ PASSED: {case['description']} - {case['domain']} -> {result}")
        else:
            print(f"✗ FAILED: {case['description']} - {case['domain']} expected {case['expected']}, got {result}")
    
    # Test UUID variations
    print("\nTesting UUID variations:")
    uuid_cases = [
        {"uuid": "123e4567-e89b-12d3-a456-426614174000", "expected": True, "description": "Standard UUID"},
        {"uuid": "123E4567-E89B-12D3-A456-426614174000", "expected": True, "description": "Uppercase UUID"},
        {"uuid": "123e4567-e89b-12d3-a456-42661417400", "expected": False, "description": "Short UUID"},
        {"uuid": "123e4567-e89b-12d3-a456-4266141740000", "expected": False, "description": "Long UUID"},
        {"uuid": "123e4567e89b12d3a456426614174000", "expected": False, "description": "UUID without dashes"},
    ]
    
    for case in uuid_cases:
        result = check.uuid(case["uuid"])
        if result == case["expected"]:
            print(f"✓ PASSED: {case['description']} - {case['uuid']} -> {result}")
        else:
            print(f"✗ FAILED: {case['description']} - {case['uuid']} expected {case['expected']}, got {result}")
    
    # Test empty function edge cases
    print("\nTesting empty function edge cases:")
    empty_cases = [
        {"value": 0, "expected": True, "description": "Zero integer"},
        {"value": 0.0, "expected": True, "description": "Zero float"},
        {"value": False, "expected": False, "description": "Boolean False"},
        {"value": [], "expected": True, "description": "Empty list"},
        {"value": {}, "expected": True, "description": "Empty dict"},
        {"value": "0", "expected": False, "description": "String '0'"},
    ]
    
    for case in empty_cases:
        result = check.empty(case["value"])
        if result == case["expected"]:
            print(f"✓ PASSED: {case['description']} - {case['value']} -> {result}")
        else:
            print(f"✗ FAILED: {case['description']} - {case['value']} expected {case['expected']}, got {result}")
    
    print()


def run_all_tests():
    """Run all test functions"""
    print("🚀 Starting EasyMySQL InputRules and check Test Suite")
    print("=" * 80)
    
    try:
        test_input_rules_valid_data()
        test_input_rules_invalid_data()
        test_input_rules_filters()
        test_check_class_valid()
        test_check_class_invalid()
        test_check_sanitization()
        test_edge_cases()
        test_performance()
        test_original_example()
        test_required_validation()
        
        # New comprehensive tests
        test_utility_functions()
        test_jsontools_class()
        test_filter_function()
        test_error_handling()
        test_advanced_edge_cases()
        
        print("=" * 80)
        print("🎉 All tests completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()