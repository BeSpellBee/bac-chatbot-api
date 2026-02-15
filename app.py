from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

# ============ COMPLETE AUTHOR DATABASE ============
AUTHORS_DATABASE = {
    # Unit 1: Africa
    "chimamanda ngozi adichie": {
        "name": "Chimamanda Ngozi Adichie",
        "unit": "africa",
        "nationality": "Nigerian",
        "works": [
            {"title": "The Danger of a Single Story", "type": "TED Talk", "page": 25},
            {"title": "Purple Hibiscus", "type": "Novel", "page": 31},
            {"title": "Half of a Yellow Sun", "type": "Novel", "page": 31}
        ],
        "key_themes": ["Postcolonialism", "Feminism", "Identity", "Representation"],
        "biography": "Chimamanda Ngozi Adichie is a Nigerian writer whose work explores feminism, postcolonialism, and identity.",
        "fun_fact": "Her 2009 TED Talk 'The Danger of a Single Story' is one of the most-viewed TED Talks of all time.",
        "focus_sections": ["Postcolonialism"],
        "related_authors": ["Chinua Achebe"]
    },
    "chinua achebe": {
        "name": "Chinua Achebe",
        "unit": "africa",
        "nationality": "Nigerian",
        "works": [
            {"title": "Things Fall Apart", "type": "Novel", "page": 21}
        ],
        "key_themes": ["Colonialism", "Igbo culture", "Tradition vs change"],
        "biography": "Chinua Achebe was a Nigerian novelist, widely considered the father of modern African literature.",
        "fun_fact": "Things Fall Apart has sold over 20 million copies worldwide.",
        "focus_sections": ["From colonialism to postcolonialism"],
        "related_authors": ["Joseph Conrad"]
    },
    "joseph conrad": {
        "name": "Joseph Conrad",
        "unit": "africa",
        "nationality": "Polish-British",
        "works": [
            {"title": "Heart of Darkness", "type": "Novel", "page": 20}
        ],
        "key_themes": ["Colonialism", "Imperialism", "Darkness"],
        "biography": "Joseph Conrad was a Polish-British writer regarded as one of the greatest novelists in English.",
        "fun_fact": "The spaceship in Alien is named Nostromo after Conrad's novel.",
        "focus_sections": ["Colonialism"],
        "related_authors": ["Chinua Achebe"]
    },
    
    # Unit 2: Art (E.E. Cummings is here!)
    "e.e. cummings": {
        "name": "E.E. Cummings",
        "unit": "art",
        "nationality": "American",
        "works": [
            {"title": "the sky was can dy", "type": "Poem", "page": 40, "description": "Concrete poem about a sunset"},
            {"title": "birds here,in ven ting air", "type": "Poem", "page": 40, "description": "Poem about birds and creation"}
        ],
        "key_themes": ["Modernism", "Visual poetry", "Individualism"],
        "biography": "Edward Estlin Cummings was an American poet known for his unconventional punctuation and syntax.",
        "fun_fact": "Cummings was arrested by the French on suspicion of espionage during WWI.",
        "focus_sections": ["Modernist poetry"],
        "related_authors": ["Ezra Pound"]
    },
    "ee cummings": {
        "name": "E.E. Cummings",
        "unit": "art",
        "nationality": "American",
        "works": [
            {"title": "the sky was can dy", "type": "Poem", "page": 40},
            {"title": "birds here,in ven ting air", "type": "Poem", "page": 40}
        ],
        "key_themes": ["Modernism", "Visual poetry", "Individualism"],
        "biography": "Edward Estlin Cummings was an American poet known for his unconventional punctuation and syntax.",
        "fun_fact": "Cummings was arrested by the French on suspicion of espionage during WWI.",
        "focus_sections": ["Modernist poetry"],
        "related_authors": ["Ezra Pound"]
    },
    "j.m.w. turner": {
        "name": "J.M.W. Turner",
        "unit": "art",
        "nationality": "British",
        "works": [
            {"title": "The Fighting Temeraire", "type": "Painting", "page": 38},
            {"title": "Rain, Steam and Speed", "type": "Painting", "page": 51}
        ],
        "key_themes": ["Sublime", "Light", "Nature"],
        "biography": "J.M.W. Turner was a British landscape painter known as the 'Painter of Light'.",
        "fun_fact": "He had himself tied to a ship's mast during a storm to experience the sea's power.",
        "focus_sections": ["Romanticism"],
        "related_authors": []
    },
    "mae west": {
        "name": "Mae West",
        "unit": "art",
        "nationality": "American",
        "works": [
            {"title": "Sex", "type": "Play", "page": 45}
        ],
        "key_themes": ["Sexuality", "Censorship", "Female empowerment"],
        "biography": "Mae West was an American actress and playwright known for her bawdy double entendres.",
        "fun_fact": "She served eight days in jail for her play 'Sex'.",
        "focus_sections": ["Scandal in the arts"],
        "related_authors": []
    },
    
    # Unit 3: Debate
    "william shakespeare": {
        "name": "William Shakespeare",
        "unit": "debate",
        "nationality": "British",
        "works": [
            {"title": "Richard III", "type": "Play", "page": 60}
        ],
        "key_themes": ["Rhetoric", "Power", "Politics"],
        "biography": "William Shakespeare was an English playwright, widely regarded as the greatest writer in English.",
        "fun_fact": "Women's roles were always played by men in Shakespeare's time.",
        "focus_sections": ["The art of rhetoric"],
        "related_authors": []
    },
    "alexander hamilton": {
        "name": "Alexander Hamilton",
        "unit": "debate",
        "nationality": "American",
        "works": [
            {"title": "Cabinet Battle #2", "type": "Song", "page": 66}
        ],
        "key_themes": ["Debate", "Politics", "Constitution"],
        "biography": "Alexander Hamilton was a Founding Father and first Secretary of the Treasury.",
        "fun_fact": "He was killed in a duel by Vice President Aaron Burr.",
        "focus_sections": ["A great debater: Alexander Hamilton"],
        "related_authors": ["Lin-Manuel Miranda"]
    },
    "barack obama": {
        "name": "Barack Obama",
        "unit": "debate",
        "nationality": "American",
        "works": [
            {"title": "Immigration reform speech", "type": "Speech", "page": 62}
        ],
        "key_themes": ["Rhetoric", "Hope", "Change"],
        "biography": "Barack Obama was the 44th President of the United States.",
        "fun_fact": "He collects Spider-Man comics.",
        "focus_sections": ["The art of rhetoric"],
        "related_authors": []
    },
    
    # Unit 5: Emotions
    "jane austen": {
        "name": "Jane Austen",
        "unit": "emotions",
        "nationality": "British",
        "works": [
            {"title": "Sense and Sensibility", "type": "Novel", "page": 90}
        ],
        "key_themes": ["Reason vs emotion", "Social class", "Marriage"],
        "biography": "Jane Austen was an English novelist known for her social commentary.",
        "fun_fact": "The 'Janeties' fan club was created in 1870!",
        "focus_sections": ["Stiff upper lip"],
        "related_authors": ["Emily Brontë"]
    },
    "emily brontë": {
        "name": "Emily Brontë",
        "unit": "emotions",
        "nationality": "British",
        "works": [
            {"title": "Wuthering Heights", "type": "Novel", "page": 96}
        ],
        "key_themes": ["Passion", "Romanticism", "Nature"],
        "biography": "Emily Brontë was an English novelist, best known for Wuthering Heights.",
        "fun_fact": "She was one of three writing sisters, including Charlotte and Anne.",
        "focus_sections": ["Romanticism"],
        "related_authors": ["Jane Austen"]
    },
    
    # Unit 7: Bildungsroman
    "charles dickens": {
        "name": "Charles Dickens",
        "unit": "bildungsroman",
        "nationality": "British",
        "works": [
            {"title": "Oliver Twist", "type": "Novel", "page": 129}
        ],
        "key_themes": ["Social criticism", "Childhood", "Poverty"],
        "biography": "Charles Dickens was an English writer, regarded as the greatest novelist of the Victorian era.",
        "fun_fact": "His novels were first published in serialized form.",
        "focus_sections": ["Oliver Twist"],
        "related_authors": []
    },
    "maya angelou": {
        "name": "Maya Angelou",
        "unit": "bildungsroman",
        "nationality": "American",
        "works": [
            {"title": "Still I Rise", "type": "Poem", "page": 130}
        ],
        "key_themes": ["Resilience", "Identity", "Race"],
        "biography": "Maya Angelou was an American poet and civil rights activist.",
        "fun_fact": "She spoke six languages.",
        "focus_sections": ["Learning from role models"],
        "related_authors": []
    },
    
    # Unit 10: Music
    "bob dylan": {
        "name": "Bob Dylan",
        "unit": "music",
        "nationality": "American",
        "works": [
            {"title": "The Times They Are A-Changing", "type": "Song", "page": 182}
        ],
        "key_themes": ["Protest", "Social change", "Poetry"],
        "biography": "Bob Dylan is an American singer-songwriter and Nobel Prize laureate.",
        "fun_fact": "He won the Nobel Prize in Literature in 2016.",
        "focus_sections": ["The Sixties"],
        "related_authors": []
    },
    "nina simone": {
        "name": "Nina Simone",
        "unit": "music",
        "nationality": "American",
        "works": [
            {"title": "To Be Young, Gifted and Black", "type": "Song", "page": 181}
        ],
        "key_themes": ["Civil rights", "Black identity"],
        "biography": "Nina Simone was an American singer and civil rights activist.",
        "fun_fact": "She was trained as a classical pianist.",
        "focus_sections": ["Notting Hill Carnival"],
        "related_authors": []
    },
    
    # Unit 11: Migration
    "zadie smith": {
        "name": "Zadie Smith",
        "unit": "migration",
        "nationality": "British",
        "works": [
            {"title": "White Teeth", "type": "Novel", "page": 220}
        ],
        "key_themes": ["Multiculturalism", "Identity", "London"],
        "biography": "Zadie Smith is a British novelist known for her debut novel White Teeth.",
        "fun_fact": "She wrote White Teeth while a student at Cambridge.",
        "focus_sections": ["Integration or cohabitation"],
        "related_authors": []
    }
}

# LLCE Units
LLCE_UNITS = {
    "africa": {
        "title": "Africa: The Danger of a Single Story",
        "pages": "18-37",
        "theme": "Art et contestation",
        "authors": ["Chimamanda Ngozi Adichie", "Chinua Achebe", "Joseph Conrad"],
        "focus_sections": ["Afrofuturism", "From colonialism to postcolonialism"]
    },
    "art": {
        "title": "Sparking Debates with Modern Art",
        "pages": "38-57",
        "theme": "L'art qui fait débat",
        "authors": ["E.E. Cummings", "J.M.W. Turner", "Mae West"],
        "focus_sections": ["Modernist poetry", "Pop Art"]
    },
    "debate": {
        "title": "Up for Debate!",
        "pages": "58-77",
        "theme": "L'art du débat",
        "authors": ["William Shakespeare", "Alexander Hamilton", "Barack Obama"],
        "focus_sections": ["The art of rhetoric"]
    },
    "emotions": {
        "title": "I Feel, Therefore I Am",
        "pages": "88-107",
        "theme": "Expression des émotions",
        "authors": ["Jane Austen", "Emily Brontë"],
        "focus_sections": ["Romanticism", "Stiff upper lip"]
    },
    "bildungsroman": {
        "title": "You Live, You Learn",
        "pages": "128-147",
        "theme": "Initiation, apprentissage",
        "authors": ["Charles Dickens", "Maya Angelou"],
        "focus_sections": ["The Bildungsroman"]
    },
    "music": {
        "title": "The Power of Music",
        "pages": "178-197",
        "theme": "Music and identity",
        "authors": ["Bob Dylan", "Nina Simone"],
        "focus_sections": ["The Sixties"]
    },
    "migration": {
        "title": "Migration: Journeys to a New Life",
        "pages": "198-217",
        "theme": "Migration et exil",
        "authors": ["Zadie Smith"],
        "focus_sections": ["Melting pot and salad bowl"]
    }
}

EXAM_STRUCTURE = {
    "written": "4 hours: Synthesis (500 words, 16 points) + Translation (600 characters, 4 points)",
    "oral": "20 minutes: 10 min presentation + 10 min Q&A on portfolio of 6-8 documents",
    "grand_oral": "20 minutes: 5 min presentation + 10 min discussion + 5 min orientation",
    "level": "B2/C1 CEFR"
}

# ============ DETECTION FUNCTIONS ============
def detect_author(user_lower):
    """Detect which author the query is about"""
    # First check for exact matches
    for key in AUTHORS_DATABASE.keys():
        if key in user_lower:
            return AUTHORS_DATABASE[key]
    
    # Check for partial matches (e.g., "cummings" matches "e.e. cummings")
    for key, author in AUTHORS_DATABASE.items():
        # Extract last name or common search terms
        name_parts = author['name'].lower().split()
        for part in name_parts:
            if part in user_lower and len(part) > 3:  # Avoid matching "e.e." only
                return author
    
    return None

def detect_unit(user_lower):
    """Detect which unit the query relates to"""
    unit_keywords = {
        "africa": ["africa", "adichie", "achebe", "conrad", "colonial", "postcolonial", "nigeria"],
        "art": ["art", "cummings", "poem", "poetry", "turner", "mae west", "modern art", "controversial"],
        "debate": ["debate", "shakespeare", "hamilton", "obama", "rhetoric", "argument"],
        "emotions": ["emotion", "austen", "brontë", "bronte", "feel", "grief", "stiff upper lip"],
        "bildungsroman": ["dickens", "oliver twist", "angelou", "coming of age", "grow"],
        "music": ["music", "song", "dylan", "simone", "protest"],
        "migration": ["migration", "smith", "immigration", "zadie"]
    }
    
    for unit, keywords in unit_keywords.items():
        for keyword in keywords:
            if keyword in user_lower:
                return unit
    return None

def generate_author_response(author_data, query):
    """Generate a beautiful response for any author"""
    unit_data = LLCE_UNITS.get(author_data['unit'], {})
    
    # Format works
    works_list = "\n".join([f"  - \"{w['title']}\" ({w['type']}, page {w.get('page', 'N/A')})" 
                           for w in author_data['works']])
    
    # Format themes
    themes_list = ", ".join(author_data['key_themes'])
    
    # Format related authors
    related = ", ".join(author_data.get('related_authors', [])) or "None"
    
    response = f"""📚 **{author_data['name']}** - LLCE Unit: {unit_data.get('title', author_data['unit'])}

**📍 TEXTBOOK LOCATION:**
- Unit: {author_data['unit'].title()} (pages {unit_data.get('pages', 'N/A')})
- Focus sections: {', '.join(author_data.get('focus_sections', []))}

**📖 KEY WORKS IN YOUR TEXTBOOK:**
{works_list}

**🎯 KEY THEMES FOR BAC ANALYSIS:**
{themes_list}

**👤 BIOGRAPHY:**
{author_data['biography']}

**✨ FUN FACT:**
{author_data.get('fun_fact', 'No fun fact available')}

**🔗 RELATED AUTHORS:**
{related}

**📝 BAC APPLICATION:**

*Written Synthesis:* {author_data['name']} would be an excellent example in a synthesis on {', '.join(author_data['key_themes'][:2])}.

*Oral Portfolio:* Include {author_data['works'][0]['title']} (p. {author_data['works'][0].get('page', 'N/A')}) in your dossier.

*Grand Oral Question:* "How does {author_data['name']}'s work challenge {author_data['key_themes'][0]}?"

**💡 STUDY STRATEGIES:**
- Analyze {author_data['works'][0]['title']} using the questions on page {author_data['works'][0].get('page', 'N/A')}
- Compare with {author_data.get('related_authors', ['other authors'])[0] if author_data.get('related_authors') else 'other authors from this unit'}
- Practice translation with key passages
- Record a 2-minute oral presentation on {author_data['key_themes'][0]}

Would you like me to help you with any specific aspect of {author_data['name']}'s work?"""
    
    return response

def generate_general_response(query, detected_unit):
    """Generate a general response when no author is found"""
    unit_info = LLCE_UNITS.get(detected_unit, {"title": "LLCE curriculum", "pages": "various"})
    
    response = f"""📚 **LLCE RESOURCES FOR: "{query}"**

**📍 UNIT CONTEXT:**
- Unit: {unit_info['title']} (pages {unit_info.get('pages', 'N/A')})
- Theme: {unit_info.get('theme', 'General')}

**📖 SUGGESTED DOCUMENTS IN YOUR TEXTBOOK:**
Check these pages in your "Let's Meet Up!" textbook:
- Look in the table of contents for relevant sections
- Check the index for specific authors or terms
- Review the focus sections in each unit

**🎯 BAC ANALYSIS APPROACH:**

For "{query}", consider:
1. Historical and cultural context
2. Literary or artistic techniques
3. Connections to unit themes
4. Comparative perspectives

**📝 EXAM APPLICATION:**

*Written Synthesis:* Structure your essay with:
- Introduction presenting your thesis
- 3-4 arguments with examples from documents
- Conclusion that opens to broader questions

*Oral Portfolio:* Select 6-8 documents showing different perspectives

**💡 STUDY STRATEGIES:**
- Build vocabulary lists
- Practice timed synthesis writing
- Record mock oral presentations
- Use the method sheets in your textbook (pages 227-261)

Would you like me to help you find specific information about an author or work?"""
    
    return response

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "LLCE BAC Assistant",
        "version": "3.0",
        "authors_available": list(AUTHORS_DATABASE.keys()),
        "units": list(LLCE_UNITS.keys()),
        "endpoints": {
            "chat": "/chat (POST with {'message': 'your question'})",
            "author": "/author/<name> (GET)",
            "unit": "/unit/<name> (GET)",
            "search": "/search?q=<query> (GET)"
        }
    })

@app.route("/author/<name>")
def author_endpoint(name):
    """Get information about a specific author"""
    author = detect_author(name.lower())
    if author:
        return jsonify(author)
    return jsonify({"error": "Author not found"}), 404

@app.route("/unit/<unit_name>")
def unit_endpoint(unit_name):
    """Get information about a specific unit"""
    unit = LLCE_UNITS.get(unit_name.lower())
    if unit:
        return jsonify(unit)
    return jsonify({"error": "Unit not found"}), 404

@app.route("/search")
def search():
    """Search for authors or topics"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    results = []
    
    # Search authors
    for key, author in AUTHORS_DATABASE.items():
        if query in key or query in author['name'].lower():
            results.append({
                "type": "author",
                "name": author['name'],
                "unit": author['unit'],
                "works": [w['title'] for w in author['works']]
            })
    
    # Search units
    for unit_key, unit in LLCE_UNITS.items():
        if query in unit_key or query in unit['title'].lower():
            results.append({
                "type": "unit",
                "name": unit['title'],
                "unit": unit_key,
                "pages": unit['pages']
            })
    
    return jsonify({
        "query": query,
        "results": results[:10]
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400
    
    user_message = data["message"]
    user_lower = user_message.lower()
    
    print(f"Received: {user_message}")
    
    # Try to detect an author
    author = detect_author(user_lower)
    
    if author:
        # Generate author-specific response
        response_text = generate_author_response(author, user_message)
    else:
        # Detect unit for context
        unit = detect_unit(user_lower)
        # Generate general response
        response_text = generate_general_response(user_message, unit)
    
    return jsonify({
        "reply": response_text,
        "detected_author": author['name'] if author else None,
        "detected_unit": detect_unit(user_lower)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 LLCE Assistant starting on port {port}...")
    print(f"📚 Authors loaded: {len(AUTHORS_DATABASE)}")
    print(f"📖 Units loaded: {len(LLCE_UNITS)}")
    print(f"🌐 Access at: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
