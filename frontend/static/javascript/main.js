let lastMessageId = 0;
let lastUserId = 0;
let Username;
let Message = "Please enter your name before proceed. We need that so we know who you are.";

window.onload = async function () {
    while (!Username) {
        let inputname = prompt(Message);

        const response = await fetch(`http://localhost:80/join/${inputname}`, {
            method: 'POST',
            headers: {
                'Access-Control-Allow-Origin': '*'
            }
        });

        if (response.ok) {
            alert("Successfully logged in! Enjoy.")
            const usersDiv = document.getElementById('activeUsers');
            Username = inputname;
            usersDiv.innerHTML = "<h2>Active Users (BETA)</h2>"
        } else {
            Message = "An error occured. Maybe it is because this name exists. If so, please choose another one. Please enter your name.";
        }
    }

    document.getElementById('message').addEventListener('keydown', function (e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            sendMessage();
        }
    });

    document.getElementById('emojiButton').addEventListener('click', function() {
        const emojiPicker = document.getElementById('emojiPicker');
        emojiPicker.style.display = emojiPicker.style.display === 'none' ? 'block' : 'none';
    });
      
    document.querySelector('emoji-picker')
        .addEventListener('emoji-click', event => {
          document.getElementById('message').value += event.detail.unicode;
    });  

    loadMessages();
    loadActiveUsers();
    setInterval(loadMessages, 1000);
    setInterval(loadActiveUsers, 1000);
};

window.onbeforeunload = function () {
    fetch(`http://localhost:80/leave/${Username}`, {
        method: 'POST',
        headers: {
            'Access-Control-Allow-Origin': '*'
        }
    });
};

window.reload

async function sendMessage() {
    const content = document.getElementById('message').value;

    if (!content.trim()) {
        alert('Message must be provided.');
        return;
    }

    let message = {
        name: Username,
        content: content
    };

    const response = await fetch('http://localhost:80/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify(message)
    });

    document.getElementById('message').value = '';
    loadMessages();
}

async function loadMessages() {
    const response = await fetch('http://localhost:80/messages');
    const messages = await response.json();

    const messagesDiv = document.getElementById('messages');

    for (const message of messages.slice(lastMessageId)) {
        message.content = message.content.replace(/</g, "&lt;").replace(/>/g, "&gt;");

        let messageContent;

        if (/[_*~`#]/.test(message.content)) {
            // The message content contains characters used in Markdown (like *, _, ~, `)
            // Let's parse it as Markdown
            messageContent = marked.parse(message.content);
        } else {
            // No special Markdown characters found in the message content,
            // Let's display it as plain text
            messageContent = message.content;
        }

        const messageElement = document.createElement('p');
        messageElement.innerHTML = `<strong>${message.name}</strong>: ${messageContent}`;
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollBy(0, messagesDiv.scrollHeight);
    }

    lastMessageId = messages.length;
}

async function loadActiveUsers() {
    const response = await fetch('http://localhost:80/active_users');
    const users = await response.json();

    const usersDiv = document.getElementById('activeUsers');
    
    for (const user of users.slice(lastUserId)) {
        const userElement = document.createElement('p');
        userElement.textContent = user;
        usersDiv.appendChild(userElement);
    }

    lastUserId = users.length;
}