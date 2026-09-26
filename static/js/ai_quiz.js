const quizForm = document.getElementById("quiz-form");
const topicInput = document.getElementById("topic");
const questionCountInput = document.getElementById("question-count");
const quizResult = document.getElementById("quiz-result");
const submitQuizButton = document.getElementById("submit-quiz");

let currentQuiz = [];

quizForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const topic = topicInput.value.trim();
    const count = Number(questionCountInput.value);

    if (!topic) {
        return;
    }

    quizResult.innerHTML = `
        <div class="quiz-question">
            <h3>Generating quiz... 🤔</h3>
            <p>Please wait.</p>
        </div>
    `;

    submitQuizButton.style.display = "none";

    try {

        const response = await fetch("/generate-quiz", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                topic: topic,
                count: count
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Quiz generation failed");
        }

        currentQuiz = data.quiz;

        displayQuiz(currentQuiz);

        submitQuizButton.style.display = "inline-block";

    } catch (error) {

        console.error("Quiz Error:", error);

        quizResult.innerHTML = `
            <div class="quiz-question">
                <h3>Something went wrong 😕</h3>
                <p>${escapeHtml(error.message)}</p>
            </div>
        `;
    }
});


function displayQuiz(quiz) {

    quizResult.innerHTML = "";

    quiz.forEach((item, index) => {

        const questionDiv = document.createElement("div");

        questionDiv.className = "quiz-question";

        questionDiv.innerHTML = `
            <h3>
                ${index + 1}. ${escapeHtml(item.question)}
            </h3>

            ${item.options.map((option) => `
                <label class="option">
                    <input
                        type="radio"
                        name="question${index}"
                        value="${escapeHtml(option)}"
                    >
                    ${escapeHtml(option)}
                </label>
            `).join("")}
        `;

        quizResult.appendChild(questionDiv);
    });
}


submitQuizButton.addEventListener("click", async function() {

    if (!currentQuiz.length) {
        return;
    }

    const answers = currentQuiz.map((item, index) => {

        const selected = document.querySelector(
            `input[name="question${index}"]:checked`
        );

        return selected ? selected.value : "";
    });

    const correctAnswers = currentQuiz.map(item => item.answer);

    try {

        const response = await fetch("/check-quiz", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                answers: answers,
                correct_answers: correctAnswers
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Quiz checking failed");
        }

        quizResult.innerHTML += `
            <div class="quiz-question">
                <h2>🎯 Quiz Result</h2>

                <p>
                    Your Score:
                    <strong>${data.score} / ${data.total}</strong>
                </p>

                <p>
                    ${getResultMessage(data.score, data.total)}
                </p>
            </div>
        `;

        submitQuizButton.style.display = "none";

        quizResult.scrollIntoView({
            behavior: "smooth"
        });

    } catch (error) {

        console.error("Score Error:", error);

        alert(error.message);
    }
});


function getResultMessage(score, total) {

    if (total === 0) {
        return "No questions available.";
    }

    const percentage = (score / total) * 100;

    if (percentage === 100) {
        return "Excellent! 🎉";
    }

    if (percentage >= 70) {
        return "Great job! 👍";
    }

    if (percentage >= 50) {
        return "Good effort! 📚";
    }

    return "Keep practicing! 💪";
}


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}