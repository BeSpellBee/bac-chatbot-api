from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Set Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not set")

# Simple in-memory conversation history
conversation_history = []
MAX_HISTORY_LENGTH = 20

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "BAC French Literature Chatbot API",
        "endpoint": "/chat (POST)",
        "instructions": "Send POST request with JSON: {\"message\": \"Your question\"}"
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

    try:
        # Only try Gemini if API key is set
        if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-key-here":
            system_prompt = """You are a BAC French literature and art analysis assistant.
            Always respond using this structure:

            Introduction:
            - Identify author/artist, genre, main theme

            Analysis:
            - Explain literary/visual techniques
            - Analyze symbolism and meaning
            - Link to historical/cultural context

            Conclusion:
            - Summarize main ideas
            - Provide final interpretation for BAC exam

            Keep responses concise but thorough."""

            # Prepare conversation
            messages = [{"role": "user", "parts": [system_prompt]}]
            
            # Add history
            for msg in conversation_history[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                messages.append({"role": role, "parts": [msg["content"]]})
            
            # Add current message
            messages.append({"role": "user", "parts": [user_message]})
            
            # Call Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(messages)
            bot_reply = response.text
        else:
            # Provide REAL fallback (not error message)
            raise Exception("Gemini API key not configured")
            
    except Exception as e:
        print(f"API error: {str(e)}")
        
        # IMPROVED FALLBACK: Real structured responses based on keywords
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['hugo', 'victor', 'misérables']):
            bot_reply = """Introduction: Victor Hugo, French Romanticism, Social Justice
            
Analysis: Hugo uses vivid characterization and symbolism in "Les Misérables." Jean Valjean represents redemption, while Javert embodies rigid justice. The novel critiques post-Napoleonic French society through themes of poverty, law, and morality.

Conclusion: Essential for BAC, Hugo's work demonstrates Romantic techniques while addressing enduring social questions."""
        
        elif any(word in user_lower for word in ['baudelaire', 'fleurs du mal', 'symbolism']):
            bot_reply = """Introduction: Charles Baudelaire, Symbolist poetry, Modern Urban Life
            
Analysis: In "Les Fleurs du Mal," Baudelaire employs synesthesia (mixing senses), irony, and urban imagery. Poems like "L'Albatros" use metaphor to explore the poet's alienation. His work bridges Romanticism and Modernism.

Conclusion: Baudelaire's innovative techniques make him crucial for understanding 19th-century French literary evolution."""
        
        elif any(word in user_lower for word in ['zola', 'naturalism', 'germinal']):
            bot_reply = """Introduction: Émile Zola, Naturalism, Determinism and Society
            
Analysis: In "Germinal," Zola uses documentary detail and environmental determinism. The mine symbolizes industrial oppression. Characters' fates are shaped by heredity and social forces, exemplifying Naturalist technique.

Conclusion: Zola's scientific approach to literature provides important contrast to Romanticism in BAC studies."""
        
        elif any(word in user_lower for word in ['monet', 'impressionism', 'painting']):
            bot_reply = """Introduction: Claude Monet, Impressionism, Light and Perception
            
Analysis: Monet uses broken brushwork and complementary colors to capture changing light. Series like "Water Lilies" explore temporal perception. His work rejects academic precision for sensory immediacy.

Conclusion: Monet's techniques revolutionized visual art and connect to literary movements exploring subjective experience."""
        
        else:
            # Generic but still structured response
            bot_reply = f"""Introduction: Analysis of "{user_message}"
            
Analysis: For BAC French literature, consider examining:
1. Author's biographical and historical context
2. Literary techniques (metaphor, symbolism, narrative structure)
3. Philosophical and thematic dimensions
4. The work's reception and cultural impact

Conclusion: A comprehensive analysis should connect formal elements to broader cultural and historical significance, as required by the BAC examination format."""

    # Save assistant reply to memory
    conversation_history.append({"role": "assistant", "content": bot_reply})

    return jsonify({
        "reply": bot_reply,
        "history_length": len(conversation_history),
        "source": "gemini" if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-key-here" else "fallback"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
