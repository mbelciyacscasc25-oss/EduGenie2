from flask import Flask, render_template, request, redirect, url_for, session

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
import os

from PyPDF2 import PdfReader

from database.db import get_db, init_db

from ai.fallback import (
    fallback_response,
    fallback_quiz
)

from ai.gemini import (
    generate_ai_quiz,
    generate_ai_answer,
    generate_ai_summary,
    generate_code_explanation
)



app = Flask(__name__)

app.secret_key = "edugenie-development-key"

init_db()


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:

            connection = get_db()

            connection.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed_password)
            )

            connection.commit()
            connection.close()

            return redirect(url_for("login"))

        except Exception:

            return "Email already registered."

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# =========================
# AI ASSISTANT PAGE
# =========================

@app.route("/ai-assistant")
def ai_assistant():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template("ai_assistant.html")


# =========================
# ASK AI
# =========================

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    if "user_id" not in session:

        return {
            "response": "Please login first."
        }, 401

    data = request.get_json() or {}

    question = data.get("question", "").strip()

    if not question:

        return {
            "response": "Please enter a question."
        }, 400

    answer = fallback_response(question)

    return {
        "response": answer
    }


# =========================
# AI QUIZ PAGE
# =========================

@app.route("/ai-quiz")
def ai_quiz():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template("ai_quiz.html")
@app.route("/notes")
def notes():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("notes.html")
@app.route("/summarize-pdf", methods=["POST"])
def summarize_pdf():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if "pdf" not in request.files:
        return render_template(
            "notes.html",
            error="Please select a PDF."
        )

    file = request.files["pdf"]

    if file.filename == "":
        return render_template(
            "notes.html",
            error="Please select a PDF."
        )

    if not file.filename.lower().endswith(".pdf"):
        return render_template(
            "notes.html",
            error="Only PDF files are allowed."
        )

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join(
        "uploads",
        file.filename
    )

    file.save(file_path)

    try:

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        if not text.strip():

            return render_template(
                "notes.html",
                error="Could not extract text from this PDF."
            )

        # Temporary summary
        summary = text[:3000]

        return render_template(
            "notes.html",
            summary=summary
        )

    except Exception as error:

        print("PDF Error:", error)

        return render_template(
            "notes.html",
            error="Could not process the PDF."
        )
    

# =========================
# GENERATE QUIZ
# =========================

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():

    if "user_id" not in session:

        return {
            "error": "Please login first."
        }, 401

    data = request.get_json() or {}

    topic = data.get("topic", "").strip()

    try:

        count = int(data.get("count", 5))

    except (TypeError, ValueError):

        count = 5

    if not topic:

        return {
            "error": "Please enter a topic."
        }, 400

    # Allow between 1 and 10 questions

    count = max(1, min(count, 10))

    # Try Gemini first

    try:

        quiz = generate_ai_quiz(topic, count)

        return {
            "quiz": quiz,
            "source": "gemini"
        }

    # Use fallback if Gemini fails or quota is exhausted

    except Exception as error:

        print("Gemini unavailable:", error)

        quiz = fallback_quiz(topic, count)

        return {
            "quiz": quiz,
            "source": "fallback"
        }


# =========================
# CHECK QUIZ
# =========================

@app.route("/check-quiz", methods=["POST"])
def check_quiz():

    if "user_id" not in session:

        return {
            "error": "Please login first."
        }, 401

    data = request.get_json() or {}

    answers = data.get("answers", [])
    correct_answers = data.get("correct_answers", [])

    score = 0

    for user_answer, correct_answer in zip(
        answers,
        correct_answers
    ):

        if user_answer == correct_answer:

            score += 1

    return {
        "score": score,
        "total": len(correct_answers)
    }
# =========================
# CODE EXPLAINER
# =========================

@app.route("/code-explainer")
def code_explainer():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("code_explainer.html")


@app.route("/explain-code", methods=["POST"])
def explain_code():

    if "user_id" not in session:
        return {
            "error": "Please login first."
        }, 401

    data = request.get_json() or {}

    code = data.get("code", "").strip()

    if not code:
        return {
            "error": "Please enter some code."
        }, 400

    try:

        explanation = generate_code_explanation(code)

        return {
            "explanation": explanation,
            "source": "gemini"
        }

    except Exception as error:

        print("Gemini code explanation unavailable:", error)

        return {
            "explanation": (
                "AI explanation is currently unavailable. "
                "Please check your Gemini configuration."
            ),
            "source": "fallback"
        }



# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(debug=True)