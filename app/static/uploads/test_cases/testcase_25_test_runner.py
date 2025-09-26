# test_runner.py
import sys
import importlib.util

# This script expects the path to the student's submission as a command-line argument.
if len(sys.argv) != 2:
    print("Usage: python test_runner.py <path_to_student_solution.py>")
    sys.exit(1)

student_file_path = sys.argv[1]

try:
    # Dynamically import the student's solution file
    spec = importlib.util.spec_from_file_location("student_solution", student_file_path)
    student_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(student_module)

    # --- TEST CASES ---
    # Test Case 1: Check if the 'add' function exists
    assert hasattr(student_module, 'add'), "Function 'add' not found in your solution."

    # Test Case 2: Test the 'add' function with positive numbers
    assert student_module.add(5, 5) == 10, f"Test failed: add(5, 5) returned {student_module.add(5, 5)}, expected 10."

    # Test Case 3: Test the 'add' function with negative numbers
    assert student_module.add(-1, -1) == -2, f"Test failed: add(-1, -1) returned {student_module.add(-1, -1)}, expected -2."

    # If all asserts pass, we print "OK" to signal success to the Celery task.
    print("OK: All test cases passed!")

except AssertionError as e:
    # Print the specific assertion error to stderr so the student can see it
    print(f"Assertion failed: {e}", file=sys.stderr)
    sys.exit(1)  # Exit with a non-zero code to indicate failure
except Exception as e:
    # Catch any other errors, like syntax errors in the student's code
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)