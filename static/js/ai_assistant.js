const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const chatMessages = document.getElementById("chat-messages");

chatForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    // Show user message
    chatMessages.innerHTML += `
        <div class="message user-message">
            <strong>You</strong>
            <p>${escapeHtml(question)}</p>
        </div>
    `;

    questionInput.value = "";

    // Show thinking message
    const thinkingMessage = document.createElement("div");

    thinkingMessage.className = "message bot-message";

    thinkingMessage.innerHTML = `
        <strong>EduGenie AI</strong>
        <p>Thinking... 🤔</p>
    `;

    chatMessages.appendChild(thinkingMessage);

    try {

        const response = await fetch("/ask-ai", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        thinkingMessage.innerHTML = `
            <strong>EduGenie AI</strong>
            <p>${escapeHtml(data.response)}</p>
        `;

    } catch (error) {

        console.error("AI Error:", error);

        thinkingMessage.innerHTML = `
            <strong>EduGenie AI</strong>
            <p>Sorry! Something went wrong. 😕</p>
        `;
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
});


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}