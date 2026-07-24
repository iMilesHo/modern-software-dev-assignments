import os
import re
from typing import Callable, List, Tuple
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 1

SYSTEM_PROMPT = """
You are a coding assistant. Output ONLY a single fenced Python code block that defines
the function is_valid_password(password: str) -> bool. No prose or comments.
Keep the implementation minimal.
"""

# TODO: Fill this in!
YOUR_REFLEXION_PROMPT = """
Please review the current code and the test failures we got, and fix the problems, and provide
the correct code.
For this function `is_valid_password(password: str) -> bool`, we should follow rules:
1. the password should have uppercase and lowercase
2. the password should have digit
3. the password should have special characters from the "!@#$%^&*()-_"
4. the password shuoldn't have space character.
"""


# Ground-truth test suite used to evaluate generated code
SPECIALS = set("!@#$%^&*()-_")
TEST_CASES: List[Tuple[str, bool]] = [
    ("Password1!", True),       # valid
    ("password1!", False),      # missing uppercase
    ("Password!", False),       # missing digit
    ("Password1", False),       # missing special
]


def extract_code_block(text: str) -> str:
    m = re.findall(r"```python\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m[-1].strip()
    m = re.findall(r"```\n([\s\S]*?)```", text)
    if m:
        return m[-1].strip()
    return text.strip()


def load_function_from_code(code_str: str) -> Callable[[str], bool]:
    namespace: dict = {}
    exec(code_str, namespace)  # noqa: S102 (executing controlled code from model for exercise)
    func = namespace.get("is_valid_password")
    if not callable(func):
        raise ValueError("No callable is_valid_password found in generated code")
    return func


def evaluate_function(func: Callable[[str], bool]) -> Tuple[bool, List[str]]:
    failures: List[str] = []
    for pw, expected in TEST_CASES:
        try:
            result = bool(func(pw))
        except Exception as exc:
            failures.append(f"Input: {pw} → raised exception: {exc}")
            continue

        if result != expected:
            # Compute diagnostic based on ground-truth rules
            reasons = []
            if len(pw) < 8:
                reasons.append("length < 8")
            if not any(c.islower() for c in pw):
                reasons.append("missing lowercase")
            if not any(c.isupper() for c in pw):
                reasons.append("missing uppercase")
            if not any(c.isdigit() for c in pw):
                reasons.append("missing digit")
            if not any(c in SPECIALS for c in pw):
                reasons.append("missing special")
            if any(c.isspace() for c in pw):
                reasons.append("has whitespace")

            failures.append(
                f"Input: {pw} → expected {expected}, got {result}. Failing checks: {', '.join(reasons) or 'unknown'}"
            )

    return (len(failures) == 0, failures)


def generate_initial_function(system_prompt: str) -> str:
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Provide the implementation now."},
        ],
        options={"temperature": 0.2},
    )
    return extract_code_block(response.message.content)


def your_build_reflexion_context(prev_code: str, failures: List[str]) -> str:
    """TODO: Build the user message for the reflexion step using prev_code and failures.

    Return a string that will be sent as the user content alongside the reflexion system prompt.
    """
    failuresStr = ""
    for s in failures:
        failuresStr += (s + "\n")
 
    return (
        "Here is the current code we have to solve the task:\n"
        "```Python\n"
        f"{prev_code}\n"
        "```\n\n"
        "Also here is the failures when we are executing the code above:\n"
        f"{failuresStr}"
    )


def apply_reflexion(
    reflexion_prompt: str,
    build_context: Callable[[str, List[str]], str],
    prev_code: str,
    failures: List[str],
) -> str:
    reflection_context = build_context(prev_code, failures)
    print(f"REFLECTION CONTEXT: {reflection_context}, {reflexion_prompt}")
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": reflexion_prompt},
            {"role": "user", "content": reflection_context},
        ],
        options={"temperature": 0.2},
    )
    return extract_code_block(response.message.content)


def run_reflexion_flow(
    system_prompt: str,
    reflexion_prompt: str,
    build_context: Callable[[str, List[str]], str],
) -> bool:
    # 1) Generate initial function
    initial_code = generate_initial_function(system_prompt)
    print("Initial code:\n" + initial_code)
    func = load_function_from_code(initial_code)
    passed, failures = evaluate_function(func)
    if passed:
        print("SUCCESS (initial implementation passed all tests)")
        return True
    else:
        print(f"FAILURE (initial implementation failed some tests): {failures}")

    # 2) Single reflexion iteration
    improved_code = apply_reflexion(reflexion_prompt, build_context, initial_code, failures)
    print("\nImproved code:\n" + improved_code)
    improved_func = load_function_from_code(improved_code)
    passed2, failures2 = evaluate_function(improved_func)
    if passed2:
        print("SUCCESS")
        return True

    print("Tests still failing after reflexion:")
    for f in failures2:
        print("- " + f)
    return False


if __name__ == "__main__":
    run_reflexion_flow(SYSTEM_PROMPT, YOUR_REFLEXION_PROMPT, your_build_reflexion_context)


# ---test results---
# Initial code:
# def is_valid_password(password: str) -> bool:
#     return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)
# FAILURE (initial implementation failed some tests): ['Input: password1! → expected False, got True. Failing checks: missing uppercase', 'Input: Password1 → expected False, got True. Failing checks: missing special']
# REFLECTION CONTEXT: Here is the current code we have to solve the task:
# ```Python
# def is_valid_password(password: str) -> bool:
#     return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)
# ```
 
# Also here is the failures when we are executing the code above:
# Input: password1! → expected False, got True. Failing checks: missing uppercase
# Input: Password1 → expected False, got True. Failing checks: missing special
# ,
# Please review the current code and the test failures we got, and fix the problems, and provide
# the correct code.
# For this function `is_valid_password(password: str) -> bool`, we should follow rules:
# 1. the password should have uppercase and lowercase
# 2. the password should have digit
# 3. the password should have special characters from the "!@#$%^&*()-_"
# 4. the password shuoldn't have space character.
 
 
# Improved code:
# def is_valid_password(password: str) -> bool:
#     """
#     Checks if a password meets certain criteria.
   
#     A valid password should have at least 8 characters,
#     contain both uppercase and lowercase letters,
#     contain at least one digit,
#     contain at least one special character (!@#$%^&*()-_),
#     and not contain any spaces.
 
#     Args:
#         password (str): The password to check.
 
#     Returns:
#         bool: True if the password is valid, False otherwise.
#     """
   
#     # Check for length
#     if len(password) < 8:
#         return False
   
#     # Check for uppercase letters
#     if not any(c.isupper() for c in password):
#         return False
   
#     # Check for lowercase letters
#     if not any(c.islower() for c in password):
#         return False
   
#     # Check for digits
#     if not any(c.isdigit() for c in password):
#         return False
   
#     # Check for special characters
#     special_chars = "!@#$%^&*()-_"
#     if not any(c in special_chars for c in password):
#         return False
   
#     # Check for spaces
#     if ' ' in password:
#         return False
   
#     # If all checks pass, the password is valid
#     return True
# SUCCESS
 