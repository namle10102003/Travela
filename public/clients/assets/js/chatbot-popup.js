document.addEventListener('DOMContentLoaded', function() {
    console.log('Chatbot script loaded'); // Debug log

    // Tạo container cho chatbot
    const chatbotContainer = document.createElement('div');
    chatbotContainer.className = 'chatbot-container';
    chatbotContainer.style.display = 'none';
    document.body.appendChild(chatbotContainer);

    // Thêm nội dung chatbot vào container
    chatbotContainer.innerHTML = `
        <div class="chatbot-header">
            <div class="chatbot-title">
                <div class="avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="info">
                    <h2>VoyaWay Assistant</h2>
                    <p>Trực tuyến</p>
                </div>
            </div>
            <button class="close-btn">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="chatbot-body">
            <div class="message bot">
                <div class="message-content">
                    Xin chào! 👋 Tôi là trợ lý du lịch của VoyaWay. Tôi có thể giúp gì cho bạn hôm nay?
                </div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        </div>
        <div class="chatbot-footer">
            <div class="chat-input">
                <input type="text" placeholder="Nhập tin nhắn của bạn..." id="chatbot-input">
                <button class="emoji-btn">
                    <i class="far fa-smile"></i>
                </button>
            </div>
            <button class="send-btn" id="chatbot-send">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
    `;

    // Thêm CSS cho chatbot popup
    const style = document.createElement('style');
    style.textContent = `
        .chatbot-container {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 380px;
            height: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            z-index: 10000;
            overflow: hidden;
        }

        .chatbot-header {
            background: linear-gradient(135deg, #ff7a00, #ff5252);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chatbot-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .chatbot-title .avatar {
            width: 35px;
            height: 35px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chatbot-title .avatar i {
            color: #ff7a00;
            font-size: 18px;
        }

        .chatbot-title .info h2 {
            font-size: 16px;
            margin-bottom: 2px;
        }

        .chatbot-title .info p {
            font-size: 11px;
            opacity: 0.8;
        }

        .close-btn {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 5px;
            transition: transform 0.3s ease;
        }

        .close-btn:hover {
            transform: scale(1.1);
        }

        .chatbot-body {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
        }

        .message.user {
            align-items: flex-end;
        }

        .message.bot {
            align-items: flex-start;
        }

        .message-content {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 15px;
            position: relative;
            font-size: 14px;
            line-height: 1.4;
        }

        .message.user .message-content {
            background: #ff7a00;
            color: white;
            border-bottom-right-radius: 5px;
        }

        .message.bot .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }

        .message-time {
            font-size: 11px;
            color: #999;
            margin-top: 5px;
        }

        .chatbot-footer {
            padding: 15px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .chat-input {
            flex: 1;
            position: relative;
        }

        .chat-input input {
            width: 100%;
            padding: 12px 45px 12px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .chat-input input:focus {
            border-color: #ff7a00;
            box-shadow: 0 0 0 2px rgba(255, 122, 0, 0.1);
        }

        .chat-input .emoji-btn {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 18px;
        }

        .send-btn {
            background: #ff7a00;
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .send-btn:hover {
            background: #ff5252;
            transform: scale(1.05);
        }

        .send-btn i {
            font-size: 16px;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .chatbot-container.show {
            display: flex !important;
            animation: slideIn 0.3s ease;
        }
    `;
    document.head.appendChild(style);

    // Xử lý sự kiện
    const chatbotButton = document.querySelector('.chatbot-button');
    const closeBtn = chatbotContainer.querySelector('.close-btn');
    const chatInput = chatbotContainer.querySelector('#chatbot-input');
    const sendBtn = chatbotContainer.querySelector('#chatbot-send');
    const chatBody = chatbotContainer.querySelector('.chatbot-body');

    // Tạo tooltip chỉ hiện khi hover (nếu chưa có trong HTML)
    if (chatbotButton && !chatbotButton.querySelector('.chatbot-tooltip')) {
        const tooltip = document.createElement('span');
        tooltip.className = 'chatbot-tooltip';
        tooltip.innerHTML = `Tôi là trợ lý hỗ trợ du lịch, hãy hỏi tôi bất cứ điều gì!<span class="chatbot-tooltip-arrow"></span>`;
        chatbotButton.appendChild(tooltip);
    }

    // Hàm lấy thời gian hiện tại
    function getCurrentTime() {
        const now = new Date();
        return `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    }

    // Hàm thêm tin nhắn
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        messageDiv.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${getCurrentTime()}</div>
        `;
        
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Hàm xử lý gửi tin nhắn
    function handleSend() {
        const message = chatInput.value.trim();
        if (message) {
            addMessage(message, true);
            chatInput.value = '';
            
            // Gọi đến backend
            fetch('chatbot.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'message=' + encodeURIComponent(message)
            })
            .then(response => response.text())
            .then(data => {
                if (data) {
                    addMessage(data);
                } else {
                    addMessage('Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Xin lỗi, đã xảy ra lỗi khi kết nối với server.');
            });
        }
    }

    // Event listeners
    chatbotButton.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Chatbot button clicked'); // Debug log
        chatbotContainer.classList.add('show');
        chatbotButton.classList.remove('new-message');
        chatbotButton.querySelector('.notification').style.display = 'none';
    });

    closeBtn.addEventListener('click', function() {
        console.log('Close button clicked'); // Debug log
        chatbotContainer.classList.remove('show');
    });

    sendBtn.addEventListener('click', function(e) {
        e.preventDefault();
        handleSend();
    });

    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSend();
        }
    });

    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!chatbotContainer.contains(e.target) && !chatbotButton.contains(e.target)) {
            chatbotContainer.classList.remove('show');
        }
    });
});