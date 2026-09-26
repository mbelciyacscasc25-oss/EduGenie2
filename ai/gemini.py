import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None


def generate_ai_quiz(topic, count):

    if client is None:
        raise Exception("Gemini API key not configured.")

    prompt = f"""
Create {count} multiple-choice educational quiz questions about "{topic}".

Return ONLY valid JSON.

Format:
[
  {{
    "question": "Question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Correct option"
  }}
]

Rules:
- Exactly {count} questions
- Exactly 4 options per question
- One correct answer per question
- Questions should be suitable for students
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    text = response.text.strip()

    return json.loads(text)


def generate_ai_answer(question):

    if client is None:
        raise Exception("Gemini API key not configured.")

    prompt = f"""
You are EduGenie, an educational AI assistant.

Answer the student's question clearly and simply.

Question:
{question}

Give a helpful educational explanation.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text.strip()


def generate_ai_summary(text):

    if client is None:
        raise Exception("Gemini API key not configured.")

    text = text[:15000]

    prompt = f"""
You are EduGenie, an educational assistant.

Summarize the following study notes clearly.

Rules:
- Use simple language
- Keep important concepts
- Use headings and bullet points
- Do not add information that is not in the notes

Study notes:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text.strip()


def generate_code_explanation(code):

    if client is None:
        raise Exception("Gemini API key not configured.")

    prompt = f"""
You are EduGenie, a programming tutor.

Explain the following code in simple language.

Include:
1. What the code does
2. How it works
3. Important concepts used
4. Possible improvements

Code:

{code}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text.strip()