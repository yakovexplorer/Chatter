# Chatter - A basic chatting room

Chatter is a simple chat room application that allows users to join and leave chat rooms, send messages, and view active
users. The backend is built with [FastAPI](https://fastapi.tiangolo.com/) and the frontend is built
with [Flask](https://flask.palletsprojects.com/en/2.1.x/).

## ⚡️ Quick start

To get started with Chatter, follow these steps:

First, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/chatter.git
```

Next, navigate to the cloned repository:

```bash
cd chatter
```

Then, install the required dependencies:

```bash
pip install -r requirements.txt
```

After that, start the backend server by navigating to the `backend` directory and running `uvicorn`:

```bash
cd backend
uvicorn main:app --port 80
```

Finally, start the frontend server by navigating to the `frontend` directory and running `python` (in a new terminal
window):

```bash
cd frontend
python main.py
```

After starting both servers, open your web browser and navigate to `http://localhost:8000` to access the chat room.

>❗️ Note: Make sure you have Python 3.x installed on your machine.

## 🔔 Short wiki

- **What is Chatter?**
  Chatter is a simple chat room application that allows multiple users to join a chat room and communicate with each
  other in real-time.

- **What technologies are used in Chatter?**
  The backend is built with [FastAPI](https://fastapi.tiangolo.com/), a modern, fast (high-performance), web framework
  for building APIs with Python 3.7+ based on standard Python type hints. The frontend is built
  with [Flask](https://flask.palletsprojects.com/en/2.1.x/), a micro web framework written in Python.

## 📖 Endpoints

The following table lists the available endpoints for the Chatter API:

| Endpoint        | Method | Description                                                    |
|-----------------|--------|----------------------------------------------------------------|
| `/messages`     | GET    | Returns a list of all messages in the chat room.               |
| `/messages`     | POST   | Creates a new message in the chat room.                        |
| `/join/{name}`  | POST   | Adds a new user to the list of active users in the chat room.  |
| `/leave/{name}` | POST   | Removes a user from the list of active users in the chat room. |
| `/active_users` | GET    | Returns a list of all active users in the chat room.           |

## 📝 Project structure

The project has the following file structure:

- `backend/`: Contains the backend code for the application.
    - `main.py`: The main file for running the backend server.
- `frontend/`: Contains the frontend code for the application.
    - `main.py`: The main file for running the frontend server.
    - `templates/`: Contains HTML templates for rendering pages.
        - `index.html`: The main template for rendering the chat room page.
    - `static/`: Contains static files such as stylesheets and JavaScript files.
        - `styles/`: Contains CSS stylesheets.
            - `styles.css`: The main stylesheet for styling the chat room page.
        - `javascript/`: Contains JavaScript files.
            - `main.js`: The main JavaScript file for handling user interactions on the chat room page.

## ⭐️ Contributing

If you would like to contribute to this project, here are some ways you can help:

- Report bugs or issues by opening an issue on GitHub.
- Suggest new features or improvements by opening an issue on GitHub.
- Submit pull requests with bug fixes or new features.

## ⚠️ Rate limits

Chatter uses rate limiting to prevent abuse of its API. The rate limit is set at 1 request per second per IP address.

## ⚠️ License

This project is licensed under the GNU GENERAL PUBLIC LICENSE. See [LICENSE](LICENSE) for more information.

[//]: # (## 👥 Contributors)

[//]: # (<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->)

[//]: # (<!-- prettier-ignore-start -->)

[//]: # (<!-- markdownlint-disable -->)

[//]: # ()

[//]: # (<!-- markdownlint-restore -->)

[//]: # (<!-- prettier-ignore-end -->)

[//]: # ()

[//]: # (<!-- ALL-CONTRIBUTORS-LIST:END -->)