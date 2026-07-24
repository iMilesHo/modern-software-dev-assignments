import os
import re
from collections import Counter
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in! Try to get as close to 100% correctness across all runs as possible.
YOUR_SYSTEM_PROMPT = """
You are smart, confident and good at math. You can solve problems in an efficient way.
You can make it simple but correct. You don't need to review and recalculate.
 
Rules you need to follow:
1. Read the question carefully and understand the process.
2. Analyse the problem step by step, but keep it simple, don't make it too complex.
3. Calculate the final answer and output it on the last line as just "Answer: <number>"
without any other words.
4. Give the answer following the format requirements.
 
Example:
Tom have 10 apples. He give his little sister two apples. Also he give his little brother
three apples. How many does he have now?
 
Your output or anaslyse process and output format:
```
Tom have total 10 apples. -> n = 10
He gives 2 to his sister. And we have (10 - 2) now, which is 8. -> a = n - 2 = 8
He gives 3 to his brother. And we have (8 - 3) now, which is 5. -> b = a - 3 = n - 2 - 3 = 5
So the final answer is b, and b = 5. And we should output the final answer on the last line:
Answer: 5
```
 
Remeber give the final answer on the last line as "Answer: <number>"!!!
Remeber give the final answer on the last line as "Answer: <number>"!!!
Remeber give the final answer on the last line as "Answer: <number>"!!!
Remeber give the final answer on the last line as "Answer: <number>"!!!
Remeber give the final answer on the last line as "Answer: <number>"!!!
Remeber give the final answer on the last line as "Answer: <number>"!!!
 
"""

USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

Henry made two stops during his 60-mile bike trip. He first stopped after 20
miles. His second stop was 15 miles before the end of the trip. How many miles
did he travel between his first and second stops?
"""

EXPECTED_OUTPUT = "Answer: 25"


def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt NUM_RUNS_TIMES, majority-vote on the extracted 'Answer: ...' lines.

    Prints "SUCCESS" if the majority answer equals EXPECTED_OUTPUT.
    """
    answers: list[str] = []
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 1},
        )
        output_text = response.message.content
        final_answer = extract_final_answer(output_text)
        print(f"Run {idx + 1} answer: {final_answer}")
        answers.append(final_answer.strip())

    if not answers:
        print("No answers produced.")
        return False

    counts = Counter(answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    print(f"Majority answer: {majority_answer} ({majority_count}/{len(answers)})")

    if majority_answer.strip() == EXPECTED_OUTPUT.strip():
        print("SUCCESS")
        return True

    # Print distribution for debugging when majority does not match expected
    print(f"Expected output: {EXPECTED_OUTPUT}")
    print("Answer distribution:")
    for answer, count in counts.most_common():
        print(f"  {answer}: {count}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)




"""
Running test 1 of 5
Run 1 answer: Answer: 25
Running test 2 of 5
Run 2 answer: Answer: 25
Running test 3 of 5
Run 3 answer: Answer: 25
Running test 4 of 5
Run 4 answer: Answer: 25
Running test 5 of 5
Run 5 answer: Answer: 25
Majority answer: Answer: 25 (5/5)
SUCCESS
"""
 