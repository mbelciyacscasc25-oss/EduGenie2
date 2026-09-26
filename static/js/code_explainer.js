const codeInput = document.getElementById("code-input");
const explainButton = document.getElementById("explain-button");
const result = document.getElementById("result");

explainButton.addEventListener("click", async function () {

    const code = codeInput.value.trim();

    if (!code) {
        alert("Please enter some code.");
        return;
    }

    result.innerHTML = `
        <div class="result-box">
            <h2>🤔 Explaining...</h2>
            <p>Please wait.</p>
        </div>
    `;

    try {
        const response = await fetch("/explain-code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: code
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Explanation failed");
        }

        result.innerHTML = `
            <div class="result-box">
                <h2>📚 Explanation</h2>
                <p>${escapeHtml(data.explanation)}</p>
            </div>
        `;

    } catch (error) {

        result.innerHTML = `
            <div class="result-box error">
                <h2>❌ Error</h2>
                <p>${escapeHtml(error.message)}</p>
            </div>
        `;
    }
});

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}