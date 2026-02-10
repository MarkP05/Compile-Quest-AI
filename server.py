from fastapi import FastAPI
from pydantic import BaseModel
import inputs
import parsons  # optional

app = FastAPI(title="Python Tutor Backend")

# ---- Request model ----
class Submission(BaseModel):
    player_input: str
    sample_solution: str

# ---- Test route ----
@app.get("/test")
def test_server():
    return {"status": "ok", "message": "Server is running!"}

# ---- Main endpoint ----
@app.post("/submit-code")
def submit_code(submission: Submission):
    feedback = inputs.get_feedback(submission.player_input, submission.sample_solution)
    status = "ok" if not feedback.startswith("(AI Error") else "error"
    return {"status": status, "feedback": feedback}

# ---- Run test from browser ----
@app.get("/run-test")
def run_test():
    feedback = inputs.get_feedback("print('Hello World')", "print('Hello World')")
    status = "ok" if not feedback.startswith("(AI Error") else "error"
    return {"status": status, "feedback": feedback}
# http://127.0.0.1:8000/test