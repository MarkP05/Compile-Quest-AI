import os
import sys
print(sys.executable)
from groq import Groq


# ---- FILE PATHS ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

API_KEY_FILE = os.path.join(BASE_DIR, "api_key.txt")
PLAYER_INPUT_FILE = os.path.join(BASE_DIR, "player_input.txt")
SAMPLE_SOLUTION_FILE = os.path.join(BASE_DIR, "Sample_solution.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "ai_feedback.txt")


# ---- LOAD API KEY ----
def load_api_key():
    if not os.path.exists(API_KEY_FILE):
        raise ValueError(f"API key not found: {API_KEY_FILE}")

    with open(API_KEY_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def numbered_file(base_name, num, ext="txt"):
    return os.path.join(BASE_DIR, f"{base_name}{num}.{ext}")

if len(sys.argv) > 1:
    try:
        FILE_NUM = int(sys.argv[1])
    except:
        FILE_NUM = 1
else:
    FILE_NUM = 1

print(f"Using input set #{FILE_NUM}")

API_KEY = load_api_key()
print("key loaded")

# ---- INITIALIZE AI ----
client = Groq(api_key=API_KEY)


# ---- FILE UTILITIES ----
def read_file(path):
    if not os.path.exists(path):
        return "(file missing)"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---- PROMPT ----
def build_prompt(player_input, sample_solution):
    return f"""
You are an AI tutor for a young beginner (age 8–12).

The game provides two text files:

FILE #1 — Player Input:
(Problem + student's code)
=====================
{player_input}
=====================

FILE #2 — Sample Solution:
(Problem + correct code)
=====================
{sample_solution}
=====================

TASK:
You MUST follow these rules exactly:

1. Output ONLY these three sections, in this exact order:
   Problem:
   Your Code:
   Feedback:

2. Include NOTHING before, after, or between those sections.
   - No greetings
   - No introductions
   - No “Okay!” or “Let's see”
   - No emojis
   - No extra commentary

3. Do not output the sample solution code.

4. Compare the student's code to the problem and the sample solution.

5. Decide if the student solved the problem correctly.

6. If correct:
   - Praise them briefly.
   - Explain why in simple words.

7. If incorrect:
   - Give **short, simple hints**.
   - Explain every incorrect piece, don't leave anything out.
   - Suggest what to try next.
   - Do NOT reveal the correct answer.

8. Keep the feedback VERY short, friendly, and kid-safe.

9. Keep the preamble to a minimum.

10. Do NOT use the sample solution code in your response.

11. With numbers, don't give exact values for the feedback; use approximate terms like "more" or "less".

You must ONLY produce the required three sections and nothing else.
"""


# ---- MAIN EVALUATION ----
def run_evaluator():
    print("Reading input files...")

    sample_file = numbered_file("Sample_solution", FILE_NUM)
    print(sample_file)
    player_input = read_file(PLAYER_INPUT_FILE)
    sample_solution = read_file(sample_file)

    prompt = build_prompt(player_input, sample_solution)

    print("Calling Groq model...")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a middle school Python teacher."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=50,
        )
        feedback = response.choices[0].message.content.strip()
    except Exception as e:
        feedback = f"(AI Error: {e})"

    print("Writing ai_feedback.txt...")

    # ---- DELETE old file if it exists ----
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # ---- Write fresh file ----
    write_file(OUTPUT_FILE, feedback)

    print("Done.")


if __name__ == "__main__":
    run_evaluator()
    print("Evaluator run complete.")
