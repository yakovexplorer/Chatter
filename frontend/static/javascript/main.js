const API_URL = 'http://localhost:80';
const USERNAME_PROMPT = "Please enter your name before proceeding. We need that so we know who you are.";
const USERNAME_ERROR_PROMPT = "An error occurred. Maybe it is because this name exists. If so, please choose another one. Please enter your name.";

let lastMessageId = 0;
let lastUserId = 0;
let Username;

window.addEventListener('load', async () => {
    await login();
    setupEventListeners();
    loadMessages();
    loadActiveUsers();
    setInterval(loadMessages, 1000);
    setInterval(loadActiveUsers, 1000);
});

window.addEventListener('beforeunload', () => {
    fetch(`${API_URL}/leave/${Username}`, {
        method: 'POST', headers: {
            'Access-Control-Allow-Origin': '*'
        }
    });
});

async function login() {
    let message = USERNAME_PROMPT;
    while (!Username) {
        let inputname = prompt(message);

        inputname = sanitizeInput(inputname);

        try {
            const response = await fetch(`${API_URL}/join/${inputname}`, {
                method: 'POST', headers: {
                    'Access-Control-Allow-Origin': '*'
                }
            });

            if (response.ok) {
                alert("Successfully logged in! Enjoy.")
                const usersDiv = document.querySelector('.user-list');
                Username = inputname;
                usersDiv.innerHTML = ""
            } else if (response.status === 429) {
                alert("You have exceeded the rate limit. Please wait before trying again.");
            } else {
                message = USERNAME_ERROR_PROMPT;
            }
        } catch (error) {
            alert("An error occurred while trying to join the chat. Please check your network connection and try again.");
        }
    }
}

function sanitizeInput(input) {
    return input.replace(/</g, "<").replace(/>/g, ">");
}

function setupEventListeners() {
    document.querySelector('.chatroom-textarea').addEventListener('keydown', (e) => {
        if (e.keyCode === 13) {
            e.preventDefault();
            sendMessage();
        }
    });

    document.querySelector('.button-v2').addEventListener('click', sendMessage);
}

function displaySystemMessage(msg) {
    const messagesDiv = document.querySelector('.main-contents');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<span class="chatroom-system chat-system">${msg}</span>`;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollBy(0, messagesDiv.scrollHeight);
}

async function sendMessage() {
    const content = document.querySelector('.chatroom-textarea').value;

    if (!content.trim()) {
        alert('Message must be provided.');
        return;
    }

    let message = {
        name: Username, content: content
    };

    try {
        const response = await fetch(`${API_URL}/messages`, {
            method: 'POST', headers: {
                'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'
            }, body: JSON.stringify(message)
        });

        if (response.ok) {
            document.querySelector('.chatroom-textarea').value = '';
            loadMessages();
        } else if (response.status === 429) {
            alert("You have exceeded the rate limit. Please wait before trying again.");
        } else {
            alert("An error occurred while trying to send your message. Please try again.");
        }
    } catch (error) {
        alert("An error occurred while trying to send your message. Please check your network connection and try again.");
    }
}

async function loadMessages() {
    const response = await fetch(`${API_URL}/messages`);
    const messages = await response.json();

    const messagesDiv = document.querySelector('.main-contents');

    for (const message of messages.slice(lastMessageId)) {

        let messageContent;

        if (/[_*~`#]/.test(message.content)) {
            // The message content contains characters used in Markdown (like *, _, ~, `)
            // Let's parse it as Markdown
            messageContent = marked.parse(message.content);
        } else {
            // No special Markdown characters found in the message content,
            // Let's display it as plain text
            messageContent = sanitizeInput(message.content);
        }

        const messageElement = document.createElement('div');

        if (message.name === Username) {
            messageElement.classList.add('chat-you');
            messageElement.innerHTML = `<div class="chat-you-container">
                                <div class="chat-you-message">
                                    <span class="chatroom-text4">${messageContent}</span>
                                </div>
                            </div>`;

            messagesDiv.appendChild(messageElement);
            messagesDiv.scrollBy(0, messagesDiv.scrollHeight);

            continue;
        } else if (message.name === 'System') {
            displaySystemMessage(messageContent);
            continue;
        }

        messageElement.classList.add('chat-user');

        messageElement.innerHTML = `<span class="chat-user-name">${message.name}</span>
                            <div class="chat-user-container">
                                <div class="chat-user-message">
                                    <span class="chatroom-text5">${messageContent}</span>
                                </div>
                            </div>`;

        messagesDiv.appendChild(messageElement);

        messagesDiv.scrollBy(0, messagesDiv.scrollHeight);
    }

    lastMessageId = messages.length;
}

async function loadActiveUsers() {
    const response = await fetch(`${API_URL}/active_users`);
    const users = await response.json();

    const usersDiv = document.querySelector('.user-list');
    usersDiv.innerHTML = '';

    for (const user of users) {
        if (user === Username) continue;

        const userElement = document.createElement('div');
        userElement.classList.add('chatroom-user', 'user');
        userElement.innerHTML = `<div class="chatroom-text2">
                                    <span class="chatroom-text3">${user}</span>
                                </div>`;

        usersDiv.appendChild(userElement);
    }
}
