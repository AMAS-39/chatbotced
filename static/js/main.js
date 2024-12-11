// Constants and Translations
const TRANSLATIONS = {
    'en': {
        'thinking': 'Thinking...',
        'language_label': 'Language',
        'placeholder': 'Type your message here...',
        'error': 'Error: ',
        'no_response': 'No response received.'
    },
    'ku': {
        'thinking': 'بیرکردنەوە...',
        'language_label': 'زمان',
        'placeholder': 'پەیامەکەت لێرە بنووسە...',
        'error': 'هەڵە: ',
        'no_response': 'هیچ وەڵامێک وەرنەگیرا.'
    },
    'ar': {
        'thinking': 'جاري التفكير...',
        'language_label': 'لغة',
        'placeholder': 'اكتب رسالتك هنا...',
        'error': 'خطأ: ',
        'no_response': 'لم يتم تلقي أي رد.'
    }
};

let currentLanguage = 'en';
let messages = [];
const body = document.body;

function createMessageElement(message) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${message.isUser ? 'user-message-wrapper' : 'bot-message-wrapper'}`;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.isUser ? 'user-message' : 'bot-message'}`;
    
    // Format message content
    if (typeof message.content === 'string') {
        messageDiv.innerHTML = message.content.replace(/\n/g, '<br>');
    } else {
        messageDiv.textContent = 'Invalid message content';
        console.error('Invalid message content:', message.content);
    }
    
    // Add language-specific classes
    if (!message.isUser) {
        if (currentLanguage === 'ar') {
            messageDiv.classList.add('arabic');
            wrapper.classList.add('rtl');
        } else if (currentLanguage === 'ku') {
            messageDiv.classList.add('kurdish');
            wrapper.classList.add('rtl');
        }
    }
    
    wrapper.appendChild(messageDiv);
    return wrapper;
}

function addMessage(content, isUser = false) {
    console.log('Adding message:', { content, isUser });
    const message = {
        content: content,
        isUser: isUser,
        timestamp: new Date().toISOString(),
        language: currentLanguage
    };
    messages.push(message);
    displayMessages();
}

function displayMessages() {
    const container = document.getElementById('messages-container');
    if (!container) {
        console.error('Messages container not found');
        return;
    }
    
    // Clear container
    container.innerHTML = '';
    
    // Add all messages
    messages.forEach(message => {
        const messageElement = createMessageElement(message);
        container.appendChild(messageElement);
    });
    
    // Scroll to bottom
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 100);
}

function showTypingIndicator() {
    const container = document.getElementById('messages-container');
    if (!container) return;

    removeTypingIndicator();
    
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-message-wrapper';
    wrapper.id = 'typing-indicator';
    
    const indicator = document.createElement('div');
    indicator.className = `message bot-message ${currentLanguage === 'ar' ? 'arabic' : currentLanguage === 'ku' ? 'kurdish' : ''}`;
    indicator.innerHTML = `<span class="loading-dots">${TRANSLATIONS[currentLanguage].thinking}</span>`;
    
    wrapper.appendChild(indicator);
    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const userInput = document.getElementById("user-input");
    if (!userInput) return;

    const userMessage = userInput.value.trim();
    if (!userMessage) return;
    
    // Disable input and button
    userInput.disabled = true;
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;
    
    // Add user message
    addMessage(userMessage, true);
    
    // Clear input
    userInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch("/ask-claude", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: userMessage,
                language: currentLanguage
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        removeTypingIndicator();
        
        if (data && data.response) {
            addMessage(data.response);
        } else {
            addMessage(TRANSLATIONS[currentLanguage].no_response);
        }
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage(TRANSLATIONS[currentLanguage].error + error.message);
    } finally {
        // Re-enable input and button
        userInput.disabled = false;
        if (submitButton) submitButton.disabled = false;
        userInput.focus();
    }
}

function setLanguage(lang) {
    if (lang === 'select') return;
    
    currentLanguage = lang;
    
    const elements = {
        en: document.getElementById('en-content'),
        ku: document.getElementById('ku-content'),
        ar: document.getElementById('ar-content')
    };

    // Update content visibility
    Object.keys(elements).forEach(key => {
        if (elements[key]) {
            elements[key].classList.toggle('hidden', key !== lang);
        }
    });

    // Update messages container
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
        messagesContainer.classList.toggle('rtl', lang === 'ku' || lang === 'ar');
        messagesContainer.classList.toggle('kurdish', lang === 'ku');
        messagesContainer.classList.toggle('arabic', lang === 'ar');
    }

    // Update textarea
    const textarea = document.getElementById('user-input');
    if (textarea) {
        textarea.placeholder = TRANSLATIONS[lang].placeholder;
        textarea.classList.toggle('rtl', lang === 'ku' || lang === 'ar');
    }

    // Update send button position
    const sendButton = document.querySelector('.fa-paper-plane')?.parentElement;
    if (sendButton) {
        if (lang === 'ku' || lang === 'ar') {
            sendButton.classList.remove('right-3');
            sendButton.classList.add('left-3');
            sendButton.querySelector('.fa-paper-plane').style.transform = 'scaleX(-1)';
        } else {
            sendButton.classList.remove('left-3');
            sendButton.classList.add('right-3');
            sendButton.querySelector('.fa-paper-plane').style.transform = 'none';
        }
    }

    // Store language preference
    localStorage.setItem('language', lang);
}

function toggleTheme() {
    body.classList.toggle('dark');
    localStorage.setItem('theme', body.classList.contains('dark') ? 'dark' : 'light');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    body.classList.remove('light', 'dark');
    body.classList.add(savedTheme);
    
    // Set language
    const savedLanguage = localStorage.getItem('language') || 'en';
    setLanguage(savedLanguage);
    
    // Add event listeners
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");

    if (chatForm) {
        chatForm.addEventListener("submit", handleSubmit);
    }

    if (userInput) {
        userInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
            }
        });
    }
});