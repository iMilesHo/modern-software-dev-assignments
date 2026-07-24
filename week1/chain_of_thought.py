import os
import re
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
You are a master in mathmatics and calculation. You can calculate a math expression to get its final value.
You can transform the expression to a simpler that is easier to calculate when necessary. Or you can just
calculate the final answer correctly.
 
Examples:
2^{3} (mod 3)
process: 2^{3} = 8, 8 (mod 3) = 2
Answer: 2
 
3^{4} (mod 5)
process: 3^{4} = 81, 81 (mod 5) = 1
Answer: 1
 
2^{3} (mod 3)
process: 2^{3} = 8, 8 (mod 3) = 2
Answer: 2
 
3^{4} (mod 5)
process: 3^{4} = 81, 81 (mod 5) = 1
Answer: 1
 
2^{3} (mod 3)
process: 2^{3} = 8, 8 (mod 3) = 2
Answer: 2
 
3^{4} (mod 5)
process: 3^{4} = 81, 81 (mod 5) = 1
Answer: 1
 
2^{3} (mod 3)
process: 2^{3} = 8, 8 (mod 3) = 2
Answer: 2
 
3^{4} (mod 5)
process: 3^{4} = 81, 81 (mod 5) = 1
Answer: 1
 
 
 
Remember that give the final answer on the last line as "Answer: <number>"!!!!
Remember that give the final answer on the last line as "Answer: <number>"!!!!
Remember that give the final answer on the last line as "Answer: <number>"!!!!
Remember that give the final answer on the last line as "Answer: <number>"!!!!
Remember that give the final answer on the last line as "Answer: <number>"!!!!
"""


USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

what is 3^{12345} (mod 100)?
"""


# For this simple example, we expect the final numeric answer only
EXPECTED_OUTPUT = "Answer: 43"


def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        # Prefer a numeric normalization when possible (supports integers/decimals)
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """Run up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.3},
        )
        output_text = response.message.content
        final_answer = extract_final_answer(output_text)
        if final_answer.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {final_answer}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)


# The actual test results:
"""
Running test 1 of 5
Expected output: Answer: 43
Actual output: Answer: 61
Running test 2 of 5
SUCCESS
"""
 