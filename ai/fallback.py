def fallback_response(question):
    question = question.lower()

    if "python" in question:
        return (
            "Python is a high-level programming language used "
            "for web development, automation, data science and AI."
        )

    if "html" in question:
        return (
            "HTML stands for HyperText Markup Language. "
            "It is used to structure web pages."
        )

    if "css" in question:
        return (
            "CSS stands for Cascading Style Sheets. "
            "It is used to style and design web pages."
        )

    if "javascript" in question or "js" in question:
        return (
            "JavaScript is a programming language commonly used "
            "to make web pages interactive."
        )

    if "hello" in question or "hi" in question:
        return "Hello! 👋 I'm EduGenie. What would you like to learn?"

    return (
        "That's a great question! 🤖 "
        "I'm currently running in fallback mode. "
        "Once the AI service is connected, I can provide a more "
        "detailed answer."
    )
def fallback_quiz(topic, count):
    quiz = []

    for i in range(count):
        quiz.append({
            "question": f"What is an important concept in {topic}?",
            "options": [
                f"Basic concept of {topic}",
                "Unrelated concept",
                "Random value",
                "None of these"
            ],
            "answer": f"Basic concept of {topic}"
        })

    return quiz