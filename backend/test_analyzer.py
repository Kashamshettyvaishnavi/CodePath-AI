
from code_analyzer import analyze_python_code

sample_code = """
import math
from os import path

def calculate_area(radius):
    return math.pi * radius * radius

def greet(name, message):
    print(message, name)

class Circle:
    pass
"""

result = analyze_python_code(sample_code)

print("=== AST ANALYSIS RESULTS ===")

print("\nImports:")
for item in result["imports"]:
    print(item)

print("\nFunctions:")
for function in result["functions"]:
    print(function)

print("\nClasses:")
for cls in result["classes"]:
    print(cls)