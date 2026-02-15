from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os
import re
from typing import Dict, List, Optional

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

# ============ NEW: PAGE-SPECIFIC QUESTION DATABASE ============
PAGE_QUESTIONS = {
    40: {
        "title": "E.E. Cummings Poems",
        "unit": "art",
        "author": "E.E. Cummings",
        "content": [
            {
                "type": "poem",
                "title": "the sky was can dy",
                "text": "the sky was can dy lu mi nous edible spry pinks shy lem ons",
                "questions": [
                    {
                        "number": 1,
                        "question": "Present in one sentence the subject of the two poems.",
                        "answer": "The first poem captures the fragmented perception of a colorful sunset through broken syntax, while the second poem depicts birds as creators who 'invent' the air through flight and song, metaphorically representing the poet's own creative process."
                    },
                    {
                        "number": 2,
                        "question": "Read Let's focus on... Modernist poetry, p. 48. Identify what makes these poems modern and draw a parallel with modernist poetry.",
                        "answer": "These poems are modern because they favor intellect over emotion, use common speech arranged unconventionally, feature freedom of form with words spilling across the page, and abandon rigorous syntax so meaning emerges from spatial arrangement. This parallels modernist poetry's revolt against convention, replacing traditional meter with visual experimentation."
                    },
                    {
                        "number": 3,
                        "question": "Explain how this original form gives access to the meaning of the poems.",
                        "answer": "The form is functional—it enacts the experience it describes. In 'the sky was can dy', words split across lines mimic how we perceive a sunset as separate sensations, with 'can dy' suggesting sweetness and isolated syllables forcing slow reading that mimics gradual light emergence. In 'birds here,in ven ting air', 'in ven ting' split suggests ongoing creation, 'U' isolated invites reader participation, and scattered words mimic birds scattered across the sky."
                    },
                    {
                        "number": 4,
                        "question": "During a lecture in Harvard, E.E. Cummings told the students: 'If poetry is your goal, you've got to forget all about punishments and all about rewards.' Write down three questions you could ask him about his statement.",
                        "answer": "1. 'When you say forget punishments and rewards, are you asking poets to ignore public reception entirely, or simply to prioritize artistic vision over it?'\n2. 'Your poems were initially rejected by publishers who found them incomprehensible—did you ever doubt your experimental approach when facing these punishments?'\n3. 'If a poet creates work that no one can understand, does the poetry still achieve its goal, or does communication with an audience matter?'"
                    }
                ]
            },
            {
                "type": "poem",
                "title": "birds here,in ven ting air",
                "text": "birds here,in ven ting air U Ising Tw iligh t's vas tness",
                "questions": []  # Questions are covered in the first poem's questions since they ask about "the two poems"
            }
        ]
    },
    21: {
        "title": "Chinua Achebe - Things Fall Apart",
        "unit": "africa",
        "author": "Chinua Achebe",
        "content": [
            {
                "type": "text",
                "title": "Things Fall Apart excerpt",
                "questions": [
                    {
                        "number": 1,
                        "question": "In the first paragraph, pick out the change Umuofia had undergone and show how it had spread.",
                        "answer": "The church had come and led many astray. It had spread beyond just the low-born and outcast to include worthy men like Ogbuofi Ugunna, who had taken two titles and cut the anklet of his titles to join the Christians."
                    },
                    {
                        "number": 2,
                        "question": "Explain why the justice system was not fair.",
                        "answer": "The District Commissioner judged cases in ignorance, using court messengers from Umuru who were foreigners, arrogant, and high-handed. They were called 'kotma' and 'Ash-Buttocks' due to their ash-colored shorts."
                    },
                    {
                        "number": 3,
                        "question": "List the arguments explaining how colonisation happened so smoothly.",
                        "answer": "1. The white man came quietly and peaceably with religion\n2. Africans were amused at his foolishness and allowed him to stay\n3. He won over African brothers who then helped uphold his government\n4. He put a knife in the things that held the clan together"
                    }
                ]
            }
        ]
    },
    25: {
        "title": "Chimamanda Ngozi Adichie - The Danger of a Single Story",
        "unit": "africa",
        "author": "Chimamanda Ngozi Adichie",
        "content": [
            {
                "type": "text",
                "title": "The Danger of a Single Story",
                "questions": [
                    {
                        "number": 1,
                        "question": "Pick out words showing how Africans are commonly seen by Americans.",
                        "answer": "The text suggests Africans are commonly seen through stereotypes and single stories—reductive narratives that fail to capture complexity and diversity."
                    },
                    {
                        "number": 2,
                        "question": "List the novels and people she mentions and define what 'African authenticity' is according to them.",
                        "answer": "Adichie mentions various African writers who present authentic, multifaceted representations of African life, challenging the single story."
                    },
                    {
                        "number": 3,
                        "question": "Explain what it means to be 'African' for Chimamanda Ngozi Adichie.",
                        "answer": "For Adichie, being African means embracing complexity, multiplicity, and the right to self-definition. It means resisting the 'single story' imposed by Western narratives and recognizing the diversity of 54 countries and thousands of cultures."
                    }
                ]
            }
        ]
    },
    90: {
        "title": "Jane Austen - Sense and Sensibility",
        "unit": "emotions",
        "author": "Jane Austen",
        "content": [
            {
                "type": "text",
                "title": "Sense and Sensibility excerpt",
                "questions": [
                    {
                        "number": 1,
                        "question": "List the physical signs related to emotions and match them with each character.",
                        "answer": "Marianne: countenance glowing with sudden delight, started up, pronouncing his name in a tone of affection, face crimsoned over, exclaimed in a voice of the greatest emotion. Willoughby: complexion changed, embarrassment returned, held her hand only for a moment, evidently struggling for composure. Elinor: turned involuntarily to Marianne, watched his countenance, tried to screen Marianne from observation."
                    },
                    {
                        "number": 2,
                        "question": "Find the words and expressions that describe the three characters' behaviours. Read Let's focus on... Stiff upper lip (p. 99) and match them with the social conventions of the time.",
                        "answer": "Elinor embodies 'sense' and the stiff upper lip—she remains composed, tries to screen Marianne, and watches others without betraying emotion. Marianne embodies 'sensibility'—she expresses feelings openly, exclaims, and cannot hide her emotions. Willoughby struggles between genuine feeling and social expectation, trying to appear composed while his complexion betrays him."
                    },
                    {
                        "number": 3,
                        "question": "Explain how the title of the book reflects the characters' personalities.",
                        "answer": "The title directly reflects the two sisters: Elinor represents 'Sense' (reason, restraint, social awareness, hiding feelings) while Marianne represents 'Sensibility' (emotion, spontaneity, public feeling, vulnerability). The novel explores the tension between these approaches and suggests a balance is needed."
                    }
                ]
            }
        ]
    },
    96: {
        "title": "Emily Brontë - Wuthering Heights",
        "unit": "emotions",
        "author": "Emily Brontë",
        "content": [
            {
                "type": "text",
                "title": "Wuthering Heights excerpt",
                "questions": [
                    {
                        "number": 1,
                        "question": "Map out the characters in the text (names and relationships).",
                        "answer": "Catherine (main speaker), Nelly (servant and listener), Edgar Linton (Catherine's husband), Heathcliff (Catherine's true love), and Linton (Edgar Linton)."
                    },
                    {
                        "number": 2,
                        "question": "Find elements which suggest extreme emotions and use them to explain the scene.",
                        "answer": "Catherine says she would be 'extremely miserable' in heaven, describes being 'flung out' by angels, says she 'broke my heart with weeping,' and declares 'I am Heathcliff.' These extreme statements reveal her passionate nature and the intensity of her feelings for Heathcliff."
                    },
                    {
                        "number": 3,
                        "question": "Link the following terms to the male character they describe: moonbeam - lightning - frost - fire - foliage in the woods - eternal rocks. Deduce what emotions are suggested through the use of natural imagery.",
                        "answer": "Linton is associated with moonbeam, frost, and foliage—suggesting coldness, temporality, and conventional beauty. Heathcliff is associated with lightning, fire, and eternal rocks—suggesting passion, danger, intensity, and permanence. The natural imagery reveals Catherine's view of Linton as socially acceptable but ultimately superficial, while Heathcliff represents a deeper, elemental connection."
                    }
                ]
            }
        ]
    }
}

# LLCE Curriculum Units with detailed resources
LLCE_UNITS = {
    "africa": {
        "title": "Africa: The Danger of a Single Story",
        "pages": "18-37",
        "theme": "Art et contestation",
        "authors": ["Chimamanda Ngozi Adichie", "Joseph Conrad", "Chinua Achebe", "Ngugi Wa Thiong'o"],
        "key_texts": [
            {"title": "Heart of Darkness", "author": "Joseph Conrad", "page": 20, "type": "novel excerpt"},
            {"title": "Things Fall Apart", "author": "Chinua Achebe", "page": 21, "type": "novel excerpt"},
            {"title": "The danger of a single story", "author": "Chimamanda Ngozi Adichie", "page": 25, "type": "speech"},
            {"title": "Decolonising the Mind", "author": "Ngugi Wa Thiong'o", "page": 27, "type": "essay"}
        ],
        "key_images": [
            {"title": "Satirical drawing on colonialism", "page": 20},
            {"title": "Andrew Gilbert installation", "page": 22},
            {"title": "Afrochella Festival poster", "page": 26}
        ],
        "key_videos": [
            {"title": "Lupita Nyong'o on Black Panther", "page": 22, "code": "201lce005"},
            {"title": "Swan Lake meets Africa - Dada Masilo", "page": 27, "code": "201lce006"}
        ],
        "focus_sections": ["Afrofuturism", "Black Panther", "From colonialism to postcolonialism"],
        "grammar": {"page": 32, "topics": ["Le pluperfect simple", "Le superlatif de supériorité"]},
        "pronunciation": {"page": 33, "topics": ["Les deux consonnes l", "L'accentuation"]},
        "translation": {"page": 34},
        "exam_practice": {"page": 35},
        "projects": [
            "Write preface of an African artist's biography",
            "Create podcast on new African art trends"
        ]
    },
    "art": {
        "title": "Sparking Debates with Modern Art",
        "pages": "38-57",
        "theme": "L'art qui fait débat",
        "authors": ["E.E. Cummings", "J.M.W. Turner", "Mae West", "Damien Hirst", "Keith Haring", "Marc Quinn"],
        "key_texts": [
            {"title": "the sky was can dy", "author": "E.E. Cummings", "page": 40, "type": "poem"},
            {"title": "birds here,in ven ting air", "author": "E.E. Cummings", "page": 40, "type": "poem"},
            {"title": "The Catcher in the Rye excerpt", "author": "J.D. Salinger", "page": 42, "type": "novel excerpt"},
            {"title": "The Singular Boldness of Mae West", "author": "Rachel Wager-Smith", "page": 45, "type": "article"}
        ],
        "key_images": [
            {"title": "The Fighting Temeraire", "artist": "J.M.W. Turner", "page": 38},
            {"title": "Guggenheim Museum", "artist": "Frank Lloyd Wright", "page": 41},
            {"title": "Myra", "artist": "Marcus Harvey", "page": 43},
            {"title": "God Knows Why", "artist": "Damien Hirst", "page": 43},
            {"title": "Self", "artist": "Marc Quinn", "page": 43},
            {"title": "Andy Mouse 3", "artist": "Keith Haring", "page": 47}
        ],
        "key_videos": [
            {"title": "The EY Exhibition: Late Turner", "page": 40, "code": "201lce012"},
            {"title": "The Art of Complaining - Guerrilla Girls", "page": 45, "code": "201lce013"},
            {"title": "Jeff Koon's Rabbit sculpture sale", "page": 46, "code": "201lce014"}
        ],
        "focus_sections": ["Pop Art", "Modernist poetry", "Scandal in 50s America: The Catcher in the Rye"],
        "grammar": {"page": 52, "topics": ["Les verbes de perception", "La forme du verbe après un modal"]},
        "pronunciation": {"page": 53, "topics": ["La voyelle longue /a:/", "La ION rule"]},
        "translation": {"page": 54},
        "exam_practice": {"page": "55-57"},
        "projects": [
            "Write opinion article on controversial art project",
            "Debate about exhibiting controversial artist"
        ]
    },
    "emotions": {
        "title": "I Feel, Therefore I Am",
        "pages": "88-107",
        "theme": "Expression des émotions",
        "authors": ["Jane Austen", "Emily Brontë", "Max Porter", "The Cure"],
        "key_texts": [
            {"title": "Sense and Sensibility excerpt", "author": "Jane Austen", "page": 90, "type": "novel excerpt"},
            {"title": "Grief is the Thing with Feathers excerpt", "author": "Max Porter", "page": 94, "type": "novel excerpt"},
            {"title": "Wuthering Heights excerpt", "author": "Emily Brontë", "page": 96, "type": "novel excerpt"},
            {"title": "Boys Don't Cry lyrics", "author": "The Cure", "page": 93, "type": "song lyrics"}
        ],
        "key_images": [
            {"title": "Hellel and Hildebrand", "artist": "Frederick William Burton", "page": 91},
            {"title": "Wonder Woman comic", "artist": "Charles Moulton", "page": 92},
            {"title": "The Young Widow", "artist": "Edward Killingworth Johnson", "page": 95},
            {"title": "The Meeting Place", "artist": "Paul Day", "page": 97}
        ],
        "key_videos": [
            {"title": "Stiff Upper Lip", "page": 91, "code": "201lce031"},
            {"title": "Sigourney Weaver interview", "page": 93, "code": "201lce033"},
            {"title": "The Descendants clip", "page": 94, "code": "201lce034"},
            {"title": "Fleabag wedding speech", "page": 97, "code": "201lce035"}
        ],
        "focus_sections": ["Romanticism", "Stiff upper lip"],
        "grammar": {"page": 102, "topics": ["La phrase exclamative", "While, during et for"]},
        "pronunciation": {"page": 103, "topics": ["Les voyelles /i/ et /i:/", "Prononciation des mots en -ate"]},
        "translation": {"page": 104},
        "exam_practice": {"page": 105}
    }
    # Other units can be added similarly
}

# Exam structure constants
EXAM_STRUCTURE = {
    "written": {
        "duration": "4 hours",
        "synthesis": "500 words, 16 points",
        "translation": "600 characters, 4 points",
        "material": "Unilingual non-encyclopedic dictionary allowed"
    },
    "oral": {
        "duration": "20 minutes (10 min + 10 min Q&A)",
        "portfolio": "6-8 documents including: one complete work, two literary texts, two visual arts, one non-literary text",
        "themes": "Linked to one or more program themes"
    },
    "grand_oral": {
        "duration": "20 minutes (5+10+5)",
        "parts": ["Presentation of question(s)", "Deepening discussion", "Orientation project"],
        "language": "Can be done in English",
        "coef": 10,
        "skills": ["Public speaking", "Argumentation", "Critical thinking", "Motivation"]
    },
    "level": "B2/C1 CEFR"
}

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "LLCE BAC English Specialty Assistant - Deep Dive Edition",
        "version": "3.0",
        "features": [
            "Unit-specific resource mapping",
            "Page-by-page textbook navigation",
            "BAC exam integration",
            "Guided analysis methodology",
            "Portfolio building assistance",
            "NEW: Page-specific question answering"
        ],
        "curriculum_units": list(LLCE_UNITS.keys()),
        "pages_with_questions": list(PAGE_QUESTIONS.keys()),
        "endpoints": {
            "chat": "/chat (POST)",
            "unit": "/unit/<unit_name> (GET)",
            "search": "/search?q=<query> (GET)",
            "exam": "/exam/<component> (GET)",
            "page": "/page/<page_number> (GET) - NEW: Get questions for a specific page"
        }
    })

@app.route("/unit/<unit_name>")
def get_unit(unit_name):
    """Get detailed information about a specific LLCE unit"""
    unit = LLCE_UNITS.get(unit_name)
    if not unit:
        return jsonify({"error": "Unit not found"}), 404
    return jsonify(unit)

@app.route("/page/<int:page_num>")
def get_page(page_num):
    """Get all questions and answers for a specific page"""
    if page_num in PAGE_QUESTIONS:
        return jsonify(PAGE_QUESTIONS[page_num])
    return jsonify({"error": f"Page {page_num} not found in database"}), 404

@app.route("/search")
def search_textbook():
    """Search for specific topics, authors, or terms in the textbook"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    results = []
    
    # Search through all units
    for unit_key, unit in LLCE_UNITS.items():
        # Check unit title
        if query in unit['title'].lower():
            results.append({
                "type": "unit",
                "title": unit['title'],
                "unit": unit_key,
                "pages": unit['pages']
            })
        
        # Check texts
        for text in unit.get('key_texts', []):
            if query in text['title'].lower() or query in text.get('author', '').lower():
                results.append({
                    "type": "text",
                    "title": text['title'],
                    "author": text.get('author'),
                    "unit": unit_key,
                    "page": text['page']
                })
        
        # Check authors
        for author in unit.get('authors', []):
            if query in author.lower():
                results.append({
                    "type": "author",
                    "name": author,
                    "unit": unit_key,
                    "works": [t['title'] for t in unit.get('key_texts', []) if t.get('author') == author]
                })
    
    return jsonify({
        "query": query,
        "results_count": len(results),
        "results": results[:20]
    })

@app.route("/exam/<component>")
def get_exam_info(component):
    """Get detailed information about exam components"""
    if component in EXAM_STRUCTURE:
        return jsonify(EXAM_STRUCTURE[component])
    return jsonify({"error": "Exam component not found"}), 404

# ============ FIXED: Extract page number from query with better patterns ============
def extract_page_number(user_message):
    """Extract page number from query like 'page 40', 'page40', 'p.40', or 'p40'"""
    user_lower = user_message.lower()
    
    # Pattern 1: "page 40" or "page40" (with or without space)
    match = re.search(r'page\s*(\d+)', user_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "p.40" or "p40" (with or without dot)
    match = re.search(r'p\.?\s*(\d+)', user_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 3: "pg 40" or "pg40"
    match = re.search(r'pg\s*(\d+)', user_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 4: "on page 40"
    match = re.search(r'on\s+page\s+(\d+)', user_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 5: "questions on 40" - but only if it's a standalone number that might be a page
    # This is riskier, so we'll only use it if the message is short and contains a number
    if len(user_lower.split()) <= 3:
        numbers = re.findall(r'\b(\d{2,3})\b', user_lower)
        if numbers and any(int(n) in PAGE_QUESTIONS for n in numbers):
            return int(numbers[0])
    
    return None

# ============ FIXED: Generate page response with better formatting ============
def generate_page_response(page_num):
    """Generate a formatted response for page-specific questions"""
    if page_num not in PAGE_QUESTIONS:
        return None
    
    page_data = PAGE_QUESTIONS[page_num]
    response = f"📚 **PAGE {page_num}: {page_data['title']}**\n\n"
    response += f"*Unit: {page_data['unit'].title()} | Author: {page_data['author']}*\n\n"
    
    for item in page_data['content']:
        if item.get('title'):
            response += f"**📖 {item['title']}**\n\n"
        
        for q in item.get('questions', []):
            response += f"**Question {q['number']}:** {q['question']}\n"
            response += f"**Answer:** {q['answer']}\n\n"
    
    response += "💡 **Would you like me to explain any of these answers in more detail or help you with another page?**"
    return response

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "JSON data is required"}), 400
    
    user_message = data.get("message", "")
    user_lower = user_message.lower()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # ============ FIXED: PRIORITY 1 - Check if asking about a specific page ============
    page_num = extract_page_number(user_message)
    print(f"DEBUG - Extracted page number: {page_num}")  # Add debug print
    
    if page_num:
        if page_num in PAGE_QUESTIONS:
            page_response = generate_page_response(page_num)
            print(f"DEBUG - Found page {page_num} in database, returning response")
            return jsonify({
                "reply": page_response,
                "type": "page_response",
                "page": page_num,
                "source": "page_database"
            })
        else:
            # Page number detected but not in database
            print(f"DEBUG - Page {page_num} not in database")
            # Continue to normal flow, but we could add a message
            pass

    # Detect unit and topic
    unit_key = detect_llce_unit(user_lower)
    unit_data = LLCE_UNITS.get(unit_key, None)
    
    # Extract specific topic (poem, author, concept)
    topic = extract_topic(user_message, unit_data)

    # LLCE-SPECIFIC SYSTEM PROMPT with deep dive framework
    system_prompt = f"""You are an expert LLCE (Langues, Littératures et Cultures Étrangères - English specialty) BAC examiner and tutor.

CURRICULUM CONTEXT: You are teaching from the "Let's Meet Up! LLCE Tle" textbook.

EXAM REQUIREMENTS:
- Written: {EXAM_STRUCTURE['written']}
- Oral: {EXAM_STRUCTURE['oral']}
- Grand Oral: {EXAM_STRUCTURE['grand_oral']}
- Target level: {EXAM_STRUCTURE['level']}

YOUR PEDAGOGICAL APPROACH - THE "DEEP DIVE" FRAMEWORK:

ALWAYS STRUCTURE RESPONSES IN 5 PHASES:

1. 📚 SOURCE GROUNDING - TEXTBOOK CONTEXT:
   - Identify EXACT unit, pages, and documents
   - Reference specific textbook materials by page number
   - Connect to unit theme and focus sections

2. 🎯 PRESENT THE CORE MATERIALS:
   - List all relevant texts, images, videos from the textbook with page numbers
   - Include focus sections, grammar/pronunciation resources
   - Quote textbook questions directly

3. 🔍 GUIDED ANALYSIS USING TEXTBOOK QUESTIONS:
   - Walk through each textbook question step-by-step
   - Provide methodology, not just answers
   - Show HOW to analyze using course concepts
   - Include sample analytical language at B2/C1 level

4. ✨ BAC APPLICATION BRIDGE:
   - Show how analysis connects to written synthesis
   - Suggest oral portfolio integration with specific documents
   - Propose Grand Oral question angles
   - Address translation challenges if relevant

5. 🚀 INTERACTIVE NEXT STEPS:
   - Offer 2-3 specific follow-up pathways
   - Suggest related materials to explore
   - Propose practice exercises

Keep responses in English at B2/C1 level. Be specific, not generic. Every answer should make the student feel like you've actually read their textbook."""

    try:
        if use_gemini:
            # Prepare enhanced prompt with unit context
            enhanced_prompt = system_prompt
            
            if unit_data:
                enhanced_prompt += f"\n\nCURRENT UNIT CONTEXT:\n"
                enhanced_prompt += f"Unit: {unit_data['title']} (pages {unit_data['pages']})\n"
                enhanced_prompt += f"Theme: {unit_data.get('theme', 'N/A')}\n"
                enhanced_prompt += f"Key authors: {', '.join(unit_data.get('authors', []))}\n"
                
                # Add specific resources if topic detected
                if topic and 'key_texts' in unit_data:
                    for text in unit_data['key_texts']:
                        if topic.lower() in text['title'].lower() or topic.lower() in text.get('author', '').lower():
                            enhanced_prompt += f"\nSTUDENT IS ASKING ABOUT: {text['title']} on page {text['page']}\n"
                            enhanced_prompt += f"Textbook questions for this document: (See page {text['page']})\n"
                            break
            
            enhanced_prompt += f"\nSTUDENT QUERY: {user_message}\n\nProvide a comprehensive LLCE-focused response following the 5-phase Deep Dive framework above."
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(enhanced_prompt)
            bot_reply = response.text
        else:
            # USE ENHANCED LLCE-SPECIFIC FALLBACKS with deep dive framework
            bot_reply = generate_llce_deep_dive(user_message, user_lower, unit_key, unit_data, topic)
            
    except Exception as e:
        print(f"API error: {str(e)}")
        bot_reply = generate_llce_deep_dive(user_message, user_lower, unit_key, unit_data, topic)

    return jsonify({
        "reply": bot_reply,
        "llce_unit": unit_key,
        "unit_info": unit_data['title'] if unit_data else None,
        "exam_relevance": detect_exam_component(user_lower),
        "source": "gemini" if use_gemini else "llce_deep_dive",
        "follow_up_suggestions": generate_follow_ups(unit_key, topic, user_lower),
        "page_detected": page_num if page_num else None
    })

def extract_topic(user_message: str, unit_data: Optional[Dict]) -> Optional[str]:
    """Extract specific topic from user message (poem title, author, concept)"""
    # Check for poem titles
    poem_patterns = [
        r'"([^"]+)"',  # Quoted text
        r"'([^']+)'",   # Single-quoted text
        r'poem.*?by\s+(\w+\s+\w+)',  # "poem by Author"
        r'(\w+\s+\w+).*?poem'  # "Author poem"
    ]
    
    for pattern in poem_patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Check for author names in unit data
    if unit_data and 'authors' in unit_data:
        for author in unit_data['authors']:
            if author.lower() in user_message.lower():
                return author
    
    return None

def generate_follow_ups(unit_key: Optional[str], topic: Optional[str], user_lower: str) -> List[str]:
    """Generate intelligent follow-up suggestions"""
    follow_ups = []
    
    if unit_key == "art" and "cummings" in user_lower:
        follow_ups = [
            "Analyze the second Cummings poem: 'birds here,in ven ting air'",
            "Compare Cummings with another modernist poet from the unit",
            "Connect Cummings' style to the 'Modernist poetry' focus section on page 48",
            "Practice writing a BAC synthesis paragraph using Cummings as an example",
            "Try asking: 'What are the questions on page 40?'"
        ]
    elif unit_key == "africa":
        follow_ups = [
            "Compare Conrad's and Achebe's representations of Africa",
            "Explore the 'Afrofuturism' focus section on page 28",
            "Prepare an oral presentation on 'The danger of a single story'",
            "Try asking: 'What are the questions on page 21?'"
        ]
    elif unit_key == "emotions":
        follow_ups = [
            "Analyze the 'Stiff Upper Lip' concept in British culture",
            "Compare Austen's and Brontë's treatment of emotion",
            "Connect to the 'Romanticism' focus section on page 98",
            "Try asking: 'What are the questions on page 90?'"
        ]
    else:
        follow_ups = [
            f"Explore other documents in the {LLCE_UNITS.get(unit_key, {}).get('title', 'this')} unit",
            "Practice with the grammar exercises on the unit's grammar page",
            "Build your oral portfolio with documents from this unit",
            "Try asking about a specific page number (e.g., 'questions on page 40')"
        ]
    
    return follow_ups

def detect_llce_unit(user_lower):
    """Detect which LLCE unit the question relates to."""
    unit_keywords = {
        "africa": ["africa", "adichie", "conrad", "achebe", "postcolonial", "single story", "afrofuturism", "nigeria", "colonial"],
        "art": ["art", "modern art", "cummings", "poem", "turner", "mae west", "hirst", "haring", "quinn", "salinger", "catcher"],
        "debate": ["debate", "rhetoric", "courtroom", "12 angry men", "hamilton", "obama", "political", "shakespeare"],
        "censorship": ["censorship", "banned", "hays code", "trigger warning", "free speech", "miller"],
        "emotions": ["emotion", "austen", "brontë", "bronte", "porter", "romanticism", "feel", "grief", "cure", "boys don't cry"],
        "portraits": ["portrait", "fiction", "orwell", "maier", "metafiction", "self-representation", "fourth wall"],
        "bildungsroman": ["bildungsroman", "coming of age", "oliver twist", "harry potter", "angelou", "dickens", "rowling"],
        "lgbtq": ["gay", "lgbtq", "aids", "1980s", "maupin", "kushner", "activism"],
        "exploration": ["exploration", "adventure", "space", "science fiction", "travel", "journey", "kipling", "clarke"],
        "music": ["music", "song", "protest", "festival", "heritage", "dylan", "simone", "springsteen"],
        "migration": ["migration", "immigration", "diaspora", "journey", "integration", "lawrence", "tan", "smith"],
        "food": ["food", "taste", "cuisine", "culinary", "culture", "swift", "blanco"]
    }
    
    for unit, keywords in unit_keywords.items():
        if any(keyword in user_lower for keyword in keywords):
            return unit
    return None

def detect_exam_component(user_lower):
    """Detect which exam component the question relates to."""
    if any(word in user_lower for word in ['synthesis', 'written', '500 words', 'essay', 'synthèse', 'écrit']):
        return "written_exam"
    elif any(word in user_lower for word in ['oral', 'portfolio', 'presentation', 'q&a', 'dossier']):
        return "oral_exam"
    elif any(word in user_lower for word in ['grand oral', 'orientation', 'project', 'projet']):
        return "grand_oral"
    elif any(word in user_lower for word in ['translation', 'translate', '600 characters', '
