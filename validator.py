#!/usr/bin/env python3
"""validator - Composable data validation with error accumulation."""
import sys, re

class ValidationError:
    def __init__(self, path, message):
        self.path = path
        self.message = message
    def __repr__(self):
        return f"{'.'.join(self.path)}: {self.message}" if self.path else self.message

class Result:
    def __init__(self, value=None, errors=None):
        self.value = value
        self.errors = errors or []
        self.valid = len(self.errors) == 0

def required():
    def v(value, path):
        if value is None or value == "":
            return [ValidationError(path, "is required")]
        return []
    return v

def min_length(n):
    def v(value, path):
        if isinstance(value, str) and len(value) < n:
            return [ValidationError(path, f"must be at least {n} chars")]
        return []
    return v

def max_length(n):
    def v(value, path):
        if isinstance(value, str) and len(value) > n:
            return [ValidationError(path, f"must be at most {n} chars")]
        return []
    return v

def matches(pattern, msg="invalid format"):
    def v(value, path):
        if isinstance(value, str) and not re.match(pattern, value):
            return [ValidationError(path, msg)]
        return []
    return v

def in_range(lo, hi):
    def v(value, path):
        if isinstance(value, (int, float)) and not (lo <= value <= hi):
            return [ValidationError(path, f"must be between {lo} and {hi}")]
        return []
    return v

def one_of(*choices):
    def v(value, path):
        if value not in choices:
            return [ValidationError(path, f"must be one of {choices}")]
        return []
    return v

class Schema:
    def __init__(self, fields=None):
        self.fields = fields or {}

    def field(self, name, *validators):
        self.fields[name] = list(validators)
        return self

    def validate(self, data, path=None):
        if path is None:
            path = []
        errors = []
        for name, validators in self.fields.items():
            value = data.get(name) if isinstance(data, dict) else None
            field_path = path + [name]
            for v in validators:
                errors.extend(v(value, field_path))
        return Result(data if not errors else None, errors)

def test():
    s = Schema()
    s.field("name", required(), min_length(2), max_length(50))
    s.field("email", required(), matches(r"^[^@]+@[^@]+\.[^@]+$", "invalid email"))
    s.field("age", required(), in_range(0, 150))
    r = s.validate({"name": "Alice", "email": "alice@test.com", "age": 30})
    assert r.valid
    r = s.validate({"name": "", "email": "bad", "age": 200})
    assert not r.valid
    assert len(r.errors) == 4
    r = s.validate({})
    assert not r.valid
    s2 = Schema().field("status", one_of("active", "inactive"))
    r = s2.validate({"status": "active"})
    assert r.valid
    r = s2.validate({"status": "unknown"})
    assert not r.valid
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("validator: Data validation. Use --test")
