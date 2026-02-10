import os
import google.generativeai as genai

# ---- FILE PATHS ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

API_KEY_FILE = os.path.join(BASE_DIR, "api_key.txt")
PLAYER_INPUT_FILE = os.path.join(BASE_DIR, "feedbackparsons.txt")
SAMPLE_SOLUTION_FILE = os.path.join(BASE_DIR, "samplesolutionparsons.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "ai_feedback.txt")


# ---- LOAD API KEY ----
def load_api_key():
    if not os.path.exists(API_KEY_FILE):
        raise ValueError(f"API key not found: {API_KEY_FILE}")

    with open(API_KEY_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


API_KEY = load_api_key()
print("key loaded")

# ---- INITIALIZE AI ----
genai.configure(api_key=API_KEY)
MODEL = genai.GenerativeModel("gemini-2.0-flash")


# ---- FILE UTILITIES ----
def read_file(path):
    if not os.path.exists(path):
        return "(file missing)"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---- PARSONS PROMPT ----
def build_prompt(player_input, sample_solution):
    return f"""
You are an AI tutor for a young beginner (age 8–12).

This is a PARSONS PROBLEM. The student reorders shuffled lines of code.

The game provides two text files:

FILE #1 — Player Input (student’s chosen order of lines):
=====================
{player_input}
=====================

FILE #2 — Sample Solution (contains the problem description AND the correct line order):
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
   - No intros
   - No emojis
   - No extra commentary

3. Do NOT output the correct solution code.

4. Use the problem description found inside the sample solution file.

5. Compare the student's code order to the correct order.

6. If correct:
   - Praise them briefly.
   - Explain why in simple words.

7. If incorrect:
   - Give **short, simple hints**
   - Explain what is out of order
   - Suggest what to try next
   - Do NOT reveal the correct order

8. Keep everything very short, friendly, and kid-safe.

You must ONLY produce the required three sections and nothing else.
"""


# ---- MAIN EVALUATION ----
def run_evaluator():
    print("Reading input files...")

    player_input = read_file(PLAYER_INPUT_FILE)
    sample_solution = read_file(SAMPLE_SOLUTION_FILE)

    prompt = build_prompt(player_input, sample_solution)

    print("Calling Gemini model...")

    try:
        response = MODEL.generate_content(prompt)
        feedback = response.text.strip()
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
