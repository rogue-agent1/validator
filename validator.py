#!/usr/bin/env python3
"""validator - Composable validation with error accumulation."""
import sys, re

class ValidationError:
    def __init__(self, path, message):
        self.path, self.message = path, message
    def __repr__(self): return f"{self.path}: {self.message}"

class Result:
    def __init__(self): self.errors = []
    def add(self, path, msg): self.errors.append(ValidationError(path, msg))
    @property
    def ok(self): return len(self.errors) == 0

def required(val, path, result):
    if val is None or val == "":
        result.add(path, "required")
        return False
    return True

def min_len(n):
    def check(val, path, result):
        if isinstance(val, (str, list)) and len(val) < n:
            result.add(path, f"min length {n}")
    return check

def max_len(n):
    def check(val, path, result):
        if isinstance(val, (str, list)) and len(val) > n:
            result.add(path, f"max length {n}")
    return check

def matches(pattern):
    def check(val, path, result):
        if isinstance(val, str) and not re.fullmatch(pattern, val):
            result.add(path, f"must match {pattern}")
    return check

def in_range(lo, hi):
    def check(val, path, result):
        if isinstance(val, (int, float)) and not (lo <= val <= hi):
            result.add(path, f"must be {lo}-{hi}")
    return check

def validate(data, rules):
    result = Result()
    for path, checks in rules.items():
        val = data.get(path)
        for check in checks:
            if check is required:
                if not required(val, path, result): break
            else:
                if val is not None:
                    check(val, path, result)
    return result

def test():
    rules = {
        "name": [required, min_len(2), max_len(50)],
        "email": [required, matches(r"[^@]+@[^@]+\.[^@]+")],
        "age": [required, in_range(0, 150)],
    }
    r = validate({"name": "Al", "email": "a@b.com", "age": 30}, rules)
    assert r.ok
    r2 = validate({"name": "", "email": "bad", "age": 200}, rules)
    assert not r2.ok
    assert len(r2.errors) == 3
    r3 = validate({}, rules)
    assert len(r3.errors) == 3
    print("validator: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: validator.py --test")
