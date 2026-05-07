const botSelect = document.getElementById('botSelect');
const botSubtitle = document.getElementById('botSubtitle');
const samplePrompts = document.getElementById('samplePrompts');
const chatTitle = document.getElementById('chatTitle');
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');

function formatBotKey(key) {
    return key.replace(/_/g, ' ');
}

function updateBotView() {
    const botKey = botSelect.value;
    const bot = window.BOT_DATA[botKey];

    chatTitle.textContent = bot.title;
    botSubtitle.textContent = bot.subtitle;
    samplePrompts.innerHTML = '';

    bot.sample_prompts.forEach((prompt) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'prompt-chip';
        button.textContent = prompt;
        button.addEventListener('click', () => {
            messageInput.value = prompt;
            messageInput.focus();
        });
        samplePrompts.appendChild(button);
    });
}

function scrollChatToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(text, role) {
    const wrapper = document.createElement('div');
    wrapper.className = `message ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollChatToBottom();
}

async function sendMessage(message) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            bot: botSelect.value,
            message,
        }),
    });

    return response.json();
}

botSelect.addEventListener('change', () => {
    updateBotView();
    addMessage(`Switched to ${window.BOT_DATA[botSelect.value].title}. Ask me a question.`, 'bot');
});

chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();
    if (!message) {
        return;
    }

    addMessage(message, 'user');
    messageInput.value = '';

    try {
        const data = await sendMessage(message);
        addMessage(data.reply, 'bot');
    } catch (error) {
        addMessage('The chatbot is temporarily unavailable. Please try again.', 'bot');
    }
});

updateBotView();
