const API_URL = 'ws://localhost:80/ws';
const USERNAME_PROMPT = "Please enter your name before proceeding. We need that so we know who you are.";
const USERNAME_ERROR_PROMPT = "An error occurred. Maybe it is because this name exists. If so, please choose another one. Please enter your name.";

let lastMessageId = 0;
let lastUserId = 0;
let Username;
let socket;
let csrfToken;

window.addEventListener('load', async () => {
    await login();
    setupEventListeners();
});

async function login() {
    let message = USERNAME_PROMPT;
    while (!Username) {
        let inputname = prompt(message);

        inputname = sanitizeInput(inputname);

        try {
            Username = inputname;
            socket = new WebSocket(`${API_URL}/${Username}`);
            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'message') {
                    displayMessage(data.message);
                } else if (data.type === 'join') {
                    displaySystemMessage(`${data.name} has joined the chat.`);
                } else if (data.type === 'leave') {
                    displaySystemMessage(`${data.name} has left the chat.`);
                } else if (data.type === 'active_users') {
                    displayActiveUsers(data.users);
                } else if (data.type === 'csrf_token') {
                    csrfToken = data.csrf_token;
                }
            }
            socket.onopen = (event) => {
                alert("Successfully logged in! Enjoy.")
            }
            socket.onclose = (event) => {
                if (event.code === 4000) {
                    alert("The username is invalid or already in use. Please choose another one.");
                    window.location.reload();
                } else if (event.code === 4001) {
                    alert("Invalid CSRF token. Please try again.");
                    window.location.reload();
                }
            }
            window.addEventListener('beforeunload', () => {
                socket.close();
            });
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
        socket.send(JSON.stringify({ type: 'message', message, csrf_token: csrfToken }));
        document.querySelector('.chatroom-textarea').value = '';
    } catch (error) {
        alert("An error occurred while trying to send your message. Please check your network connection and try again.");
    }
}

function displayMessage(message) {

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

    const messagesDiv = document.querySelector('.main-contents');

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

        return;
    } else if (message.name === 'System') {
        displaySystemMessage(messageContent);
        return;
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

function displayActiveUsers(users) {
    const usersDiv = document.querySelector('.user-list');
    usersDiv.innerHTML = '';

    for (const user of users) {
        const userElement = document.createElement('div');
        userElement.classList.add('chatroom-user', 'user');
        userElement.innerHTML = `<div class="chatroom-text2">
                                    <span class="chatroom-text3">${user}</span>
                                </div>`;

        usersDiv.appendChild(userElement);
    }
}
