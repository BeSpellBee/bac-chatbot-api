from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Set Gemini API key (GET FREE: https://aistudio.google.com/apikey)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Fallback for local testing
    GEMINI_API_KEY = "your-gemini-key-here"  # Replace locally only
    
genai.configure(api_key=GEMINI_API_KEY)

# Simple in-memory conversation history
conversation_history = []
MAX_HISTORY_LENGTH = 20

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "BAC French Literature Chatbot API (Gemini)",
        "endpoint": "/chat (POST)",
        "model": "gemini-1.5-flash"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "JSON data is required"}), 400
    
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Add user message to memory
    conversation_history.append({"role": "user", "content": user_message})
    
    # Trim history if too long
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        # Keep most recent messages
        del conversation_history[0:2]

    # Build conversation context for Gemini
    system_prompt = """You are a BAC French literature and art analysis assistant.
    Always respond using the following structure:

    Introduction:
    - Identify the author or artist, genre, and main theme

    Analysis:
    - Explain literary or visual techniques
    - Analyze symbolism and meaning
    - Link to historical or cultural context

    Conclusion:
    - Summarize the main ideas
    - Provide a final interpretation suitable for a BAC exam

    Keep responses concise but thorough, suitable for exam preparation."""

    try:
        # Prepare full conversation for Gemini
        full_conversation = system_prompt + "\n\n"
        
        # Add conversation history (except current message)
        for msg in conversation_history[:-1]:
            role = "User" if msg["role"] == "user" else "Assistant"
            full_conversation += f"{role}: {msg['content']}\n"
        
        full_conversation += f"User: {user_message}\nAssistant:"
        
        # Call Gemini API
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_conversation)
        
        bot_reply = response.text

    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        # Fallback response if API fails
        bot_reply = f"""Introduction: Analysis of the query
Analysis: The assistant encountered a technical issue but will provide a structured response. Consider discussing literary techniques relevant to French literature.
Conclusion: Further analysis available when the API service is fully operational."""

    # Save assistant reply to memory
    conversation_history.append({"role": "assistant", "content": bot_reply})

    return jsonify({
        "reply": bot_reply,
        "history_length": len(conversation_history)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
