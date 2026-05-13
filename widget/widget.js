(function () {
    // Read config from script tag
    const scripts = document.querySelectorAll('script[data-chatbot-id]');
    const script = scripts[scripts.length - 1];
    const CHATBOT_ID = script.getAttribute("data-chatbot-id");
    const COLOR = script.getAttribute("data-color") || "#007bff";
    const WELCOME = script.getAttribute("data-welcome") || "Hi! How can I help you?";
    const API_URL = script.getAttribute("data-api-url");
  
    // Inject styles
    const style = document.createElement("style");
    style.innerHTML = `
      #cchat-btn {
        position: fixed; bottom: 24px; right: 24px;
        width: 56px; height: 56px; border-radius: 50%;
        background: ${COLOR}; color: white;
        border: none; font-size: 26px; cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 9999;
      }
      #cchat-box {
        display: none; position: fixed;
        bottom: 90px; right: 24px;
        width: 340px; height: 480px;
        background: white; border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        flex-direction: column; z-index: 9999;
        font-family: sans-serif; overflow: hidden;
      }
      #cchat-box.open { display: flex; }
      #cchat-header {
        background: ${COLOR}; color: white;
        padding: 16px; font-weight: bold; font-size: 15px;
      }
      #cchat-messages {
        flex: 1; overflow-y: auto;
        padding: 12px; display: flex;
        flex-direction: column; gap: 8px;
      }
      .cchat-msg {
        max-width: 80%; padding: 8px 12px;
        border-radius: 12px; font-size: 14px; line-height: 1.4;
      }
      .cchat-user {
        background: ${COLOR}; color: white;
        align-self: flex-end; border-bottom-right-radius: 2px;
      }
      .cchat-bot {
        background: #f0f0f0; color: #222;
        align-self: flex-start; border-bottom-left-radius: 2px;
      }
      #cchat-input-row {
        display: flex; padding: 10px;
        border-top: 1px solid #eee; gap: 8px;
      }
      #cchat-input {
        flex: 1; padding: 8px 12px;
        border: 1px solid #ddd; border-radius: 20px;
        font-size: 14px; outline: none;
      }
      #cchat-send {
        background: ${COLOR}; color: white;
        border: none; border-radius: 50%;
        width: 36px; height: 36px;
        cursor: pointer; font-size: 16px;
      }
    `;
    document.head.appendChild(style);
  
    // Build HTML
    document.body.insertAdjacentHTML("beforeend", `
      <button id="cchat-btn">💬</button>
      <div id="cchat-box">
        <div id="cchat-header">💬 Chat Assistant</div>
        <div id="cchat-messages">
          <div class="cchat-msg cchat-bot">${WELCOME}</div>
        </div>
        <div id="cchat-input-row">
          <input id="cchat-input" type="text" placeholder="Ask something..." />
          <button id="cchat-send">➤</button>
        </div>
      </div>
    `);
  
    // Toggle open/close
    document.getElementById("cchat-btn").onclick = function () {
      document.getElementById("cchat-box").classList.toggle("open");
    };
  
    // Send message
    function sendMessage() {
      const input = document.getElementById("cchat-input");
      const msg = input.value.trim();
      if (!msg) return;
  
      addMessage(msg, "user");
      input.value = "";
  
      const typing = addMessage("...", "bot");
  
      fetch(API_URL + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chatbot_id: CHATBOT_ID,
          session_id: "widget-" + Math.random().toString(36).substr(2, 9),
          message: msg
        })
      })
      .then(r => r.json())
      .then(data => {
        typing.textContent = data.answer || "Sorry, I couldn't get a response.";
      })
      .catch(() => {
        typing.textContent = "Connection error. Please try again.";
      });
    }
  
    function addMessage(text, role) {
      const div = document.createElement("div");
      div.className = "cchat-msg cchat-" + (role === "user" ? "user" : "bot");
      div.textContent = text;
      const messages = document.getElementById("cchat-messages");
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
      return div;
    }
  
    document.getElementById("cchat-send").onclick = sendMessage;
    document.getElementById("cchat-input").onkeydown = function (e) {
      if (e.key === "Enter") sendMessage();
    };
  })();  