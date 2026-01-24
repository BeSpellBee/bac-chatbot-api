from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allows requests from your github.io website

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple in-memory conversation history with limit
conversation_history = []
MAX_HISTORY_LENGTH = 20

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "BAC French Literature Chatbot API",
        "endpoint": "/chat (POST)"
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
        del conversation_history[0:2]

    system_message = {
        "role": "system",
        "content": (
            "You are a BAC French literature and art analysis assistant.\n"
            "Always respond using the following structure:\n\n"
            "Introduction:\n"
            "- Identify the author or artist, genre, and main theme\n\n"
            "Analysis:\n"
            "- Explain literary or visual techniques\n"
            "- Analyze symbolism and meaning\n"
            "- Link to historical or cultural context\n\n"
            "Conclusion:\n"
            "- Summarize the main ideas\n"
            "- Provide a final interpretation suitable for a BAC exam\n\n"
            "Keep responses concise but thorough, suitable for exam preparation."
        )
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                system_message,
                *conversation_history[:-1]
            ]
        )
        
        bot_reply = response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return jsonify({
            "error": "Failed to generate response",
            "details": str(e)
        }), 500

    # Save assistant reply to memory
    conversation_history.append({"role": "assistant", "content": bot_reply})

    return jsonify({
        "reply": bot_reply,
        "history_length": len(conversation_history)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
