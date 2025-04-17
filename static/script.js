function sendMessage() {
    const inputBox = document.getElementById("user-input");
    const message = inputBox.value.trim();
    const chatBox = document.getElementById("chat-box");
  
    if (!message) return;
  
    // Show user message
    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.textContent = message;
    chatBox.appendChild(userMsg);
    inputBox.value = "";
  
    fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
      const botMsg = document.createElement("div");
      botMsg.className = "bot-message";
      botMsg.textContent = data.answer;
      chatBox.appendChild(botMsg);
      chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(err => {
      const errorMsg = document.createElement("div");
      errorMsg.className = "bot-message";
      errorMsg.textContent = "❌ Error: " + err.message;
      chatBox.appendChild(errorMsg);
    });
  }
  
  // Enter key sends message
  document.getElementById("user-input").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });
  
  // Toggle chatbot visibility
  document.getElementById("chatbot-icon").addEventListener("click", function() {
    const chatWindow = document.getElementById("chat-container");
    if (chatWindow.style.display === "none") {
      chatWindow.style.display = "flex";
    } else {
      chatWindow.style.display = "none";
    }
  });  