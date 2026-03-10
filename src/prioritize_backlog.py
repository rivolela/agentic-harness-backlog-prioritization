import json
import requests
from dotenv import load_dotenv
import os

# 1. LOAD backlog (Tool: local JSON file)
backlog_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'backlog.json')
with open(backlog_path, "r") as f:
    backlog = json.load(f)

# 2. BUILD prompt (Orchestration: contextualize + rank)
prompt = f"""
You are a Product Owner assistant.
Given this backlog:

{json.dumps(backlog, indent=2)}

Rank these items by priority (highest first).
Consider: business value, effort, and urgency.
For each item, give a short rationale.

Output as a numbered markdown list.
"""

# 3. CALL LLM (Tool: Gemini API)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

headers = {
    "Content-Type": "application/json"
}

payload = {
    "contents": [
        {"parts": [{"text": prompt}]}
    ]
}

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")

response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
response.raise_for_status()
result = response.json()["candidates"][0]["content"]["parts"][0]["text"]

# 4. SAVE output (Guardrail: suggestion only, never auto-commit)
output_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'prioritized_backlog.md')
with open(output_path, "w") as f:
    f.write("# Prioritized Backlog (AI Suggestion)\n\n")
    f.write(result)
    f.write("\n\n---\n")
    f.write("> ⚠️ This is a suggestion. Final decision belongs to the PO.\n")

print(f"Done! Review {output_path}")