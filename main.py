from flask import Flask, render_template, render_template_string, request, send_file, redirect, url_for, session, jsonify
import qrcode
import os
import uuid
import json
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

UPLOAD_FOLDER = 'static/qrcodes'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Chat app data directory and file
DATA_DIR = 'static/chat_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

# Initialize messages file if it doesn't exist
if not os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, "w") as f:
        json.dump([], f)

def get_messages():
    try:
        with open(MESSAGES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading messages: {e}")
        return []

def save_message(username, content):
    messages = get_messages()
    message = {
        "username": username,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(message)
    try:
        with open(MESSAGES_FILE, "w") as f:
            json.dump(messages, f)
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text')
        fill_color = request.form.get('fill_color')
        back_color = request.form.get('back_color')
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        unique_filename = f"{uuid.uuid4()}.png"
        qr_code_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        img.save(qr_code_path)

        return render_template('index.html', qr_code_path=qr_code_path)

    return render_template('index.html', qr_code_path='')

@app.route('/download/<filename>')
def download(filename):
    print(filename)
    qr_code_path = f"static/qrcodes/{filename}"
    return send_file(path_or_file=qr_code_path, as_attachment=True)
    
@app.route('/download/Desi_Ide')
def desi_ide():
    return send_file(path_or_file="static/DESI IDE.zip", as_attachment=True)

@app.route('/cleanup')
def cleanup():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return redirect(url_for('index'))

# Chat application routes
@app.route('/chat')
def chat():
    messages = get_messages()
    return render_template_string(CHAT_HTML_TEMPLATE, messages=messages)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username:
        session['username'] = username
    return redirect(url_for('chat'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('chat'))

@app.route('/send', methods=['POST'])
def send():
    if 'username' not in session:
        return jsonify({"status": "error", "message": "Not logged in"})
    
    data = request.get_json()
    content = data.get('content')
    
    if content:
        if save_message(session['username'], content):
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Failed to save message"})
    
    return jsonify({"status": "error", "message": "Empty message"})

@app.route('/messages')
def messages():
    if 'username' not in session:
        return jsonify([])
    return jsonify(get_messages())

# HTML template for the chat app
CHAT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PARV GLOBAL CHAT</title>
    <style>
        :root {
            --primary-color: #4a6fa5;
            --secondary-color: #6c8bbf;
            --background-color: #f5f7fa;
            --text-color: #333;
            --light-text: #7a7a7a;
            --border-color: #e1e5eb;
            --message-bg: #fff;
            --my-message-bg: #e1f0ff;
            --success-color: #4CAF50;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--background-color);
            color: var(--text-color);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            width: 100%;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        header {
            background-color: var(--primary-color);
            color: white;
            padding: 15px 0;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            position: relative;
        }

        header h1 {
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        header h1 svg {
            margin-right: 10px;
        }

        .status-indicator {
            position: absolute;
            top: 15px;
            right: 20px;
            display: flex;
            align-items: center;
            font-size: 14px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }

        .status-dot.online {
            background-color: var(--success-color);
        }

        .status-dot.offline {
            background-color: #ff4d4d;
        }

        .login-container {
            max-width: 400px;
            margin: 50px auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .form-control {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .form-control:focus {
            border-color: var(--primary-color);
            outline: none;
        }

        .btn {
            background-color: var(--primary-color);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: background-color 0.3s;
            width: 100%;
        }

        .btn:hover {
            background-color: var(--secondary-color);
        }

        .chat-container {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 150px);
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .message-container {
            flex-grow: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 8px;
            background-color: var(--message-bg);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            max-width: 80%;
            word-break: break-word;
            position: relative;
        }

        .message.own-message {
            margin-left: auto;
            background-color: var(--my-message-bg);
        }

        .message .username {
            font-weight: bold;
            margin-bottom: 5px;
            color: var(--primary-color);
        }

        .message .timestamp {
            font-size: 12px;
            color: var(--light-text);
            position: absolute;
            bottom: 5px;
            right: 10px;
        }

        .input-area {
            padding: 15px;
            background-color: #f9f9f9;
            border-top: 1px solid var(--border-color);
            display: flex;
        }

        .message-input {
            flex-grow: 1;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 16px;
            margin-right: 10px;
        }

        .message-input:focus {
            outline: none;
            border-color: var(--primary-color);
        }

        .send-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0 20px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }

        .send-btn:hover {
            background-color: var(--secondary-color);
        }

        .logout-btn {
            background-color: transparent;
            color: white;
            border: 1px solid white;
            border-radius: 4px;
            padding: 5px 10px;
            position: absolute;
            left: 20px;
            top: 15px;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .logout-btn:hover {
            background-color: rgba(255,255,255,0.2);
        }

        .home-btn {
            background-color: transparent;
            color: white;
            border: 1px solid white;
            border-radius: 4px;
            padding: 5px 10px;
            position: absolute;
            left: 100px;
            top: 15px;
            cursor: pointer;
            transition: background-color 0.3s;
            text-decoration: none;
            display: flex;
            align-items: center;
        }

        .home-btn:hover {
            background-color: rgba(255,255,255,0.2);
        }

        .notification {
            padding: 10px;
            background-color: var(--success-color);
            color: white;
            text-align: center;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            transform: translateY(-100%);
            transition: transform 0.3s;
        }

        .notification.show {
            transform: translateY(0);
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div id="notification" class="notification"></div>
    <header>
        <h1>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            PARV GLOBAL CHAT
        </h1>
        {% if session.username %}
        <form action="/logout" method="post">
            <button type="submit" class="logout-btn">Logout</button>
        </form>
        <a href="/" class="home-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            Home
        </a>
        <div class="status-indicator">
            <div class="status-dot online"></div>
            <span>Online</span>
        </div>
        {% else %}
        <a href="/" class="home-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            Home
        </a>
        {% endif %}
    </header>

    <div class="container">
        {% if not session.username %}
        <div class="login-container">
            <h2 style="margin-bottom: 20px; text-align: center;">Login to PARV GLOBAL CHAT</h2>
            <form action="/login" method="post">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" class="form-control" placeholder="Enter your username" required>
                </div>
                <button type="submit" class="btn">Join Chat</button>
            </form>
        </div>
        {% else %}
        <div class="chat-container">
            <div class="message-container" id="message-container">
                {% for message in messages %}
                <div class="message {% if message.username == session.username %}own-message{% endif %}">
                    <div class="username">{{ message.username }}</div>
                    <div class="content">{{ message.content }}</div>
                    <div class="timestamp">{{ message.timestamp }}</div>
                </div>
                {% endfor %}
            </div>
            <div class="input-area">
                <input type="text" id="message-input" class="message-input" placeholder="Type your message here..." autocomplete="off">
                <button id="send-btn" class="send-btn">Send</button>
            </div>
        </div>
        {% endif %}
    </div>

    {% if session.username %}
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const messageContainer = document.getElementById('message-container');
            const messageInput = document.getElementById('message-input');
            const sendBtn = document.getElementById('send-btn');
            const notification = document.getElementById('notification');
            
            // Scroll to bottom of messages
            messageContainer.scrollTop = messageContainer.scrollHeight;
            
            // Function to show notification
            function showNotification(message) {
                notification.textContent = message;
                notification.classList.add('show');
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 3000);
            }

            // Function to send message
            function sendMessage() {
                const content = messageInput.value.trim();
                if (content) {
                    fetch('/send', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({content: content})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            messageInput.value = '';
                            loadMessages();
                        }
                    })
                    .catch(error => {
                        console.error('Error sending message:', error);
                        showNotification('Failed to send message. Please try again.');
                    });
                }
            }
            
            // Function to load messages
            function loadMessages() {
                fetch('/messages')
                .then(response => response.json())
                .then(data => {
                    messageContainer.innerHTML = '';
                    data.forEach(message => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = `message ${message.username === '{{ session.username }}' ? 'own-message' : ''}`;
                        
                        const usernameDiv = document.createElement('div');
                        usernameDiv.className = 'username';
                        usernameDiv.textContent = message.username;
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'content';
                        contentDiv.textContent = message.content;
                        
                        const timestampDiv = document.createElement('div');
                        timestampDiv.className = 'timestamp';
                        timestampDiv.textContent = message.timestamp;
                        
                        messageDiv.appendChild(usernameDiv);
                        messageDiv.appendChild(contentDiv);
                        messageDiv.appendChild(timestampDiv);
                        
                        messageContainer.appendChild(messageDiv);
                    });
                    
                    messageContainer.scrollTop = messageContainer.scrollHeight;
                })
                .catch(error => {
                    console.error('Error loading messages:', error);
                });
            }
            
            // Event listeners
            sendBtn.addEventListener('click', sendMessage);
            
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Use a shorter polling interval for faster updates
            setInterval(loadMessages, 500);  // Check for new messages every 500ms
            
            // Initial load
            loadMessages();
            
            // Show welcome notification
            showNotification('Welcome to PARV GLOBAL CHAT, {{ session.username }}!');
        });
    </script>
    {% endif %}
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=False)