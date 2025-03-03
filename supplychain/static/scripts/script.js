function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || "";
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function scrollToBottom() {
    let chatBox = document.getElementById("chat-box");

    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 100);
}

function sendMessage() {
    let inputField = document.getElementById("chat-input-field");
    let message = inputField.value.trim();
    if (message === "") return;

    let chatBox = document.getElementById("chat-box");

    // Add user message to chat
    let userMessage = document.createElement("div");
    userMessage.classList.add("message", "user");
    userMessage.innerText = message;
    chatBox.appendChild(userMessage);

    inputField.value = "";

    // Create a bot "Typing..." indicator
    let botTyping = document.createElement("div");
    botTyping.classList.add("message", "bot");
    botTyping.innerHTML = '<span class="typing-indicator">Thinking<span>.</span><span>.</span><span>.</span></span>';
    chatBox.appendChild(botTyping);

    scrollToBottom();

    // Start dot animation
    let dots = botTyping.querySelectorAll(".typing-indicator span");
    let dotIndex = 0;
    let typingInterval = setInterval(() => {
        dots.forEach((dot, index) => {
            dot.style.opacity = index === dotIndex ? "1" : "0.3";
        });
        dotIndex = (dotIndex + 1) % dots.length;
    }, 500);

    // Send message to backend
    fetch("/chatbot/query/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken(),
        },
        body: `question=${encodeURIComponent(message)}`,
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(typingInterval);
        chatBox.removeChild(botTyping);

        // Add bot response to chat
        let botMessage = document.createElement("div");
        botMessage.classList.add("message", "bot");
        botMessage.innerText = data.answer;
        chatBox.appendChild(botMessage);

        // Display chat history if available
        let chatHistory = data.chat_history;
        if (chatHistory && chatHistory.length > 0) {
            let historyMessage = document.createElement("div");
            historyMessage.classList.add("message", "history");
            historyMessage.innerText = "[Memory] Chat History:";
            chatBox.appendChild(historyMessage);

            chatHistory.forEach(entry => {
                let historyEntry = document.createElement("div");
                historyEntry.classList.add("message", "history");
                historyEntry.innerText = entry;
                chatBox.appendChild(historyEntry);
            });
        }

        scrollToBottom();
    })
    .catch(error => {
        console.error("Error:", error);
        clearInterval(typingInterval);
        chatBox.removeChild(botTyping);

        let errorMessage = document.createElement("div");
        errorMessage.classList.add("message", "bot");
        errorMessage.innerText = "Something went wrong. Try again.";
        chatBox.appendChild(errorMessage);

        scrollToBottom();
    });
}
