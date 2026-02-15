from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Set Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-key-here":
    genai.configure(api_key=GEMINI_API_KEY)
    use_gemini = True
else:
    use_gemini = False
    print("Using fallback mode - no Gemini API key configured")

# LLCE Curriculum Units (from your syllabus)
LLCE_UNITS = {
    "africa": "Africa: The Danger of a Single Story - Colonial/post-colonial perspectives, Afrofuturism, Adichie, Conrad, Achebe",
    "art": "Sparking Debates with Modern Art - Controversial artworks, censorship, modern poetry, Mae West, Hirst, Haring",
    "debate": "Up for Debate! - Rhetoric, courtroom debates, political discourse, 12 Angry Men, Hamilton, Obama",
    "censorship": "Censorship, an American Art? - Banned books, Hays Code, trigger warnings, freedom of speech",
    "emotions": "I Feel, Therefore I Am - Emotions in literature/society, Romanticism, Austen, Brontë, Porter",
    "portraits": "Portraits of Fiction - Self-representation in art, metafiction, Vivian Maier, George Orwell",
    "bildungsroman": "You Live, You Learn - Bildungsroman, coming-of-age, Oliver Twist, Harry Potter, Angelou",
    "lgbtq": "Gay Identity in the 1980s - LGBTQ+ history, AIDS crisis, activism, Maupin, Kushner",
    "exploration": "Mankind, a Species Designed for Exploration? - Adventure literature, space exploration, sci-fi",
    "music": "The Power of Music - Music and identity, heritage, protest songs, festivals",
    "migration": "Migration: Journeys to a New Life - Immigration narratives, integration, diaspora art",
    "food": "A Taste for Adventure - Food and culture, travel, identity"
}

# Exam structure constants
EXAM_STRUCTURE = {
    "written": "4 hours: Synthesis (500 words, 16 points) + Translation (600 characters, 4 points)",
    "oral": "20 minutes: 10 min presentation + 10 min Q&A on portfolio of 6-8 documents",
    "grand_oral": "20 minutes: 5 min presentation + 10 min discussion + 5 min orientation project (can be in English)",
    "level": "B2/C1 CEFR - emphasis on argumentation, public speaking, critical thinking"
}

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "LLCE BAC English Specialty Assistant",
        "curriculum_units": list(LLCE_UNITS.keys()),
        "exam_info": EXAM_STRUCTURE,
        "endpoint": "/chat (POST)"
    })

@app.route("/llce/units")
def llce_units():
    return jsonify(LLCE_UNITS)

@app.route("/llce/exam")
def llce_exam():
    return jsonify(EXAM_STRUCTURE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "JSON data is required"}), 400
    
    user_message = data.get("message", "")
    user_lower = user_message.lower()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # LLCE-SPECIFIC SYSTEM PROMPT
    system_prompt = f"""You are an expert LLCE (Langues, Littératures et Cultures Étrangères - English specialty) BAC examiner and tutor.

CURRICULUM CONTEXT: You are teaching the following units: {', '.join(LLCE_UNITS.keys())}

EXAM REQUIREMENTS:
- Written: {EXAM_STRUCTURE['written']}
- Oral: {EXAM_STRUCTURE['oral']}
- Grand Oral: {EXAM_STRUCTURE['grand_oral']}
- Target level: {EXAM_STRUCTURE['level']}

ALWAYS RESPOND WITH THIS STRUCTURE:

1. 📚 UNIT IDENTIFICATION & CONTEXT:
   - Which LLCE unit this relates to
   - Historical/cultural context (Anglophone world focus)
   - Key authors/artists/works from curriculum

2. 🎯 ANALYSIS FOR BAC:
   - Literary/cultural analysis (themes, techniques, devices)
   - Connection to specific unit themes
   - Comparative perspectives when relevant

3. ✍️ EXAM APPLICATION:
   - How this could appear in written synthesis (500 words)
   - Potential oral portfolio document connections
   - Grand Oral discussion angles
   - Translation challenges if text-based

4. 📝 STUDY STRATEGIES:
   - Key vocabulary/terminology
   - Argumentation techniques
   - Portfolio document suggestions
   - Practice exercises

Keep responses at B2/C1 level, in English, with specific references to the LLCE curriculum."""

    try:
        if use_gemini:
            # Prepare messages for Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            full_prompt = f"""{system_prompt}

STUDENT QUERY: {user_message}

Provide a comprehensive LLCE-focused response following the 4-part structure above."""
            
            response = model.generate_content(full_prompt)
            bot_reply = response.text
        else:
            # USE LLCE-SPECIFIC FALLBACKS
            bot_reply = generate_llce_fallback(user_message, user_lower)
            
    except Exception as e:
        print(f"API error: {str(e)}")
        bot_reply = generate_llce_fallback(user_message, user_lower)

    return jsonify({
        "reply": bot_reply,
        "llce_unit": detect_llce_unit(user_lower),
        "exam_relevance": detect_exam_component(user_lower),
        "source": "gemini" if use_gemini else "llce_fallback"
    })

def generate_llce_fallback(user_message, user_lower):
    """Generate LLCE-specific fallback responses based on curriculum units."""
    
    # Detect which unit the question relates to
    unit = detect_llce_unit(user_lower)
    unit_info = LLCE_UNITS.get(unit, "General LLCE curriculum")
    
    # UNIT-SPECIFIC RESPONSES
    if unit == "africa":
        return f"""1. 📚 UNIT IDENTIFICATION & CONTEXT:
- LLCE Unit: {unit_info}
- Key works: Chimamanda Ngozi Adichie's "The Danger of a Single Story" (TED Talk), Joseph Conrad's "Heart of Darkness", Chinua Achebe's "Things Fall Apart"
- Context: Postcolonial theory, representation of Africa, Afrofuturism as counter-narrative

2. 🎯 ANALYSIS FOR BAC:
- Adichie argues against monolithic representations of Africa
- Conrad vs. Achebe: Colonial vs. postcolonial perspectives
- Afrofuturism (e.g., Black Panther) reimagines African futures
- Themes: Identity, representation, power of narrative

3. ✍️ EXAM APPLICATION:
- Synthesis topic: "How do postcolonial writers challenge single stories?"
- Oral portfolio: Combine Adichie's TED Talk + excerpt from "Things Fall Apart" + Afrofuturism art
- Translation: Idiomatic expressions in Achebe ("Proverbs are the palm-oil with which words are eaten")
- Grand Oral: Link to orientation project in cultural studies, journalism, or international relations

4. 📝 STUDY STRATEGIES:
- Key terms: Postcolonialism, Orientalism, hybridity, diaspora
- Compare: Conrad's symbolic Africa vs. Achebe's realistic Igbo society
- Practice: Write a 500-word synthesis comparing two representations of Africa
- Portfolio suggestion: Add contemporary Afrofuturist music (Janelle Monáe)"""

    elif unit == "emotions":
        return f"""1. 📚 UNIT IDENTIFICATION & CONTEXT:
- LLCE Unit: {unit_info}
- Key works: Jane Austen's "Pride and Prejudice", Emily Brontë's "Wuthering Heights", Max Porter's "Grief is the Thing with Feathers"
- Context: Romanticism, emotional expression in literature, modern approaches to emotion

2. 🎯 ANALYSIS FOR BAC:
- Austen: Social emotions, irony, restraint vs. feeling
- Brontë: Passionate emotions, Gothic intensity, nature as emotional mirror
- Porter: Contemporary grief, blend of poetry/prose/fable
- Themes: Emotional intelligence, social constraints on feeling, grief processing

3. ✍️ EXAM APPLICATION:
- Synthesis topic: "How do literary representations of emotion evolve from Romanticism to today?"
- Oral portfolio: Austen letter + Brontë poem + Porter excerpt + psychological article on grief
- Translation: Emotional idioms ("heart of stone" → "cœur de pierre")
- Grand Oral: Link to psychology, literature, or social work orientation

4. 📝 STUDY STRATEGIES:
- Key terms: Sentimentality, pathetic fallacy, emotional labor, catharsis
- Trace: Romantic emotional excess → Victorian restraint → Modern fragmentation
- Practice: Analyze emotional vocabulary in Austen vs. Brontë
- Portfolio suggestion: Add song lyrics about emotion (Adele, Billie Eilish)"""

    elif unit == "bildungsroman":
        return f"""1. 📚 UNIT IDENTIFICATION & CONTEXT:
- LLCE Unit: {unit_info}
- Key works: Dickens' "Oliver Twist", Rowling's "Harry Potter", Maya Angelou's "I Know Why the Caged Bird Sings"
- Context: Coming-of-age narratives, social education, identity formation

2. 🎯 ANALYSIS FOR BAC:
- Dickens: Social critique through child's perspective, Victorian morality
- Rowling: Modern Bildungsroman with fantasy elements, friendship as education
- Angelou: African-American female Bildungsroman, trauma and resilience
- Themes: Innocence to experience, social integration, self-discovery

3. ✍️ EXAM APPLICATION:
- Synthesis topic: "How do Bildungsromane reflect their social contexts?"
- Oral portfolio: Excerpt from each + psychological theory of adolescence
- Translation: Child vs. adult narrative voices in translation
- Grand Oral: Link to education, social work, or literature studies

4. 📝 STUDY STRATEGIES:
- Key terms: Initiation, rites of passage, epiphany, character arc
- Compare: 19th vs. 20th vs. 21st century coming-of-age
- Practice: Chart Harry Potter's moral education across the series
- Portfolio suggestion: Add film clip (Moonlight, Lady Bird) as visual comparison"""

    elif unit == "music":
        return f"""1. 📚 UNIT IDENTIFICATION & CONTEXT:
- LLCE Unit: {unit_info}
- Key focus: Protest songs, music festivals, music as cultural identity
- Examples: Bob Dylan, Nina Simone, Woodstock, Glastonbury, Beyoncé's Lemonade
- Context: Music as social/political commentary, community formation

2. 🎯 ANALYSIS FOR BAC:
- Protest songs: Lyrics as poetry, amplification of social movements
- Festivals: Temporary communities, counter-culture expression
- Identity: Music as diaspora connection (e.g., Caribbean music in UK)
- Themes: Resistance, belonging, cultural memory

3. ✍️ EXAM APPLICATION:
- Synthesis topic: "How does music construct and challenge social identities?"
- Oral portfolio: Song lyrics + festival documentary clip + academic analysis
- Translation: Translating rhyme/rhythm in song lyrics
- Grand Oral: Link to musicology, cultural studies, event management

4. 📝 STUDY STRATEGIES:
- Key terms: Auteur, intertextuality, cultural appropriation, sonic identity
- Analyze: Lyrics as poetry + musical elements + performance context
- Practice: Compare 1960s protest songs with contemporary political music
- Portfolio suggestion: Include personal music narrative from student"""

    # GENERAL LLCE RESPONSE TEMPLATE
    else:
        return f"""1. 📚 UNIT IDENTIFICATION & CONTEXT:
- LLCE Unit: {unit_info if unit else 'General LLCE curriculum'}
- BAC English Specialty: Langues, Littératures et Cultures Étrangères
- Focus: Anglophone literature, culture, and critical analysis

2. 🎯 ANALYSIS FOR BAC:
- For "{user_message}", consider: historical context, literary devices, cultural significance
- Connect to broader LLCE themes: Rencontres, Imaginaires, Représentations, Appartenances
- Apply B2/C1 level analysis: nuanced argumentation, precise terminology

3. ✍️ EXAM APPLICATION:
- Written synthesis: Structure with thesis, 3-4 arguments, conclusion (500 words)
- Oral portfolio: Select documents showing different perspectives on this topic
- Grand Oral: Prepare 5-minute clear presentation with visual support if needed
- Translation practice: Work on FR↔EN cultural equivalents

4. 📝 STUDY STRATEGIES:
- Build vocabulary list specific to this topic
- Practice timed synthesis writing (4 hours total)
- Record mock oral presentations for fluency
- Use method sheets for poem/image/film analysis
- Consult Hatier platform digital resources"""

def detect_llce_unit(user_lower):
    """Detect which LLCE unit the question relates to."""
    unit_keywords = {
        "africa": ["africa", "adichie", "conrad", "achebe", "postcolonial", "single story", "afrofuturism"],
        "art": ["art", "modern art", "censorship", "haring", "hirst", "mae west", "poetry"],
        "debate": ["debate", "rhetoric", "courtroom", "12 angry men", "hamilton", "obama", "political"],
        "censorship": ["censorship", "banned", "hays code", "trigger warning", "free speech"],
        "emotions": ["emotion", "austen", "brontë", "porter", "romanticism", "feel", "grief"],
        "portraits": ["portrait", "fiction", "orwell", "maier", "metafiction", "self-representation"],
        "bildungsroman": ["bildungsroman", "coming of age", "oliver twist", "harry potter", "angelou", "grow"],
        "lgbtq": ["gay", "lgbtq", "aids", "1980s", "maupin", "kushner", "activism"],
        "exploration": ["exploration", "adventure", "space", "science fiction", "travel", "journey"],
        "music": ["music", "song", "protest", "festival", "identity", "heritage"],
        "migration": ["migration", "immigration", "diaspora", "journey", "integration"],
        "food": ["food", "taste", "cuisine", "culinary", "culture", "identity"]
    }
    
    for unit, keywords in unit_keywords.items():
        if any(keyword in user_lower for keyword in keywords):
            return unit
    return None

def detect_exam_component(user_lower):
    """Detect which exam component the question relates to."""
    if any(word in user_lower for word in ['synthesis', 'written', '500 words', 'essay']):
        return "written_exam"
    elif any(word in user_lower for word in ['oral', 'portfolio', 'presentation', 'q&a']):
        return "oral_exam"
    elif any(word in user_lower for word in ['grand oral', 'orientation', 'project']):
        return "grand_oral"
    elif any(word in user_lower for word in ['translation', 'translate', '600 characters']):
        return "translation"
    return "general_preparation"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
