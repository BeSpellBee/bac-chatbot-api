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
        "exam_practice": {"page": 55-57},
        "projects": [
            "Write opinion article on controversial art project",
            "Debate about exhibiting controversial artist"
        ]
    },
    # ... (similar detailed structure for other units - I'll add them on request)
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
        "version": "2.0",
        "features": [
            "Unit-specific resource mapping",
            "Page-by-page textbook navigation",
            "BAC exam integration",
            "Guided analysis methodology",
            "Portfolio building assistance"
        ],
        "curriculum_units": list(LLCE_UNITS.keys()),
        "endpoints": {
            "chat": "/chat (POST)",
            "unit": "/unit/<unit_name> (GET)",
            "search": "/search?q=<query> (GET)",
            "exam": "/exam/<component> (GET)"
        }
    })

@app.route("/unit/<unit_name>")
def get_unit(unit_name):
    """Get detailed information about a specific LLCE unit"""
    unit = LLCE_UNITS.get(unit_name)
    if not unit:
        return jsonify({"error": "Unit not found"}), 404
    return jsonify(unit)

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
        "results": results[:20]  # Limit to 20 results
    })

@app.route("/exam/<component>")
def get_exam_info(component):
    """Get detailed information about exam components"""
    if component in EXAM_STRUCTURE:
        return jsonify(EXAM_STRUCTURE[component])
    return jsonify({"error": "Exam component not found"}), 404

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "JSON data is required"}), 400
    
    user_message = data.get("message", "")
    user_lower = user_message.lower()
    
    # Check if user wants textbook page references
    wants_pages = any(term in user_lower for term in ['page', 'p.', 'where', 'find', 'in the book'])

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

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
        "follow_up_suggestions": generate_follow_ups(unit_key, topic, user_lower)
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
            "Practice writing a BAC synthesis paragraph using Cummings as an example"
        ]
    elif unit_key == "africa":
        follow_ups = [
            "Compare Conrad's and Achebe's representations of Africa",
            "Explore the 'Afrofuturism' focus section on page 28",
            "Prepare an oral presentation on 'The danger of a single story'"
        ]
    elif unit_key == "emotions":
        follow_ups = [
            "Analyze the 'Stiff Upper Lip' concept in British culture",
            "Compare Austen's and Brontë's treatment of emotion",
            "Connect to the 'Romanticism' focus section on page 98"
        ]
    else:
        follow_ups = [
            f"Explore other documents in the {LLCE_UNITS.get(unit_key, {}).get('title', 'this')} unit",
            "Practice with the grammar exercises on the unit's grammar page",
            "Build your oral portfolio with documents from this unit"
        ]
    
    return follow_ups

def generate_llce_deep_dive(user_message: str, user_lower: str, unit_key: Optional[str], 
                            unit_data: Optional[Dict], topic: Optional[str]) -> str:
    """Generate LLCE-specific deep dive responses following the 5-phase framework."""
    
    # UNIT-SPECIFIC DEEP DIVE RESPONSES
    
    # E.E. CUMMINGS DEEP DIVE (from page 40)
    if unit_key == "art" and any(term in user_lower for term in ['cummings', 'poem', 'sky', 'birds']):
        return f"""1. 📚 SOURCE GROUNDING - TEXTBOOK CONTEXT
- **LLCE Unit:** {unit_data['title']} (pages {unit_data['pages']})
- **Theme:** {unit_data.get('theme')}
- **Specific Document:** E.E. Cummings poems on **page 40**
- **Focus Section:** "Modernist poetry" on **page 48** and E.E. Cummings biography on **page 48**

2. 🎯 PRESENT THE CORE MATERIALS
Your textbook provides these resources on E.E. Cummings:

**Primary Texts (page 40):**
- Poem 1: "the sky was can dy" - a concrete poem about a sunset/sky
- Poem 2: "birds here,in ven ting air" - about birds and creation/invention

**Textbook Questions (page 40):**
1. "Present in one sentence the subject of the two poems."
2. "Read Let's focus on... Modernist poetry, p. 48. Identify what makes these poems modern and draw a parallel with modernist poetry."
3. "Explain how this original form gives access to the meaning of the poems."
4. "During a lecture in Harvard, E.E. Cummings told the students: 'If poetry is your goal, you've got to forget all about punishments and all about rewards.' Write down three questions you could ask him about his statement."

**Visual Support:** The poems themselves are visual arrangements on the page

**Additional Resources:**
- Modernist poetry focus section (page 48)
- E.E. Cummings biography (page 48)
- Pronunciation exercises (page 53)
- Translation page (page 54)

3. 🔍 GUIDED ANALYSIS USING TEXTBOOK QUESTIONS

**Question 1: "Present in one sentence the subject of the two poems."**

*Methodology:* Look at the key words and visual arrangement to identify theme.

- **Poem 1 ("the sky was can dy"):** The fragmented words ("can dy" for candy, "lu mi nous" for luminous, "spry pinks," "shy lem ons," "choco lates") suggest a sunset or sky painted in vibrant colors—the speaker is breaking down a visual experience into its component parts, just as the poem breaks words into syllables.

- **Poem 2 ("birds here,in ven ting air"):** The words "inven ting" (inventing), "U" (you), "Ising" (I sing/Icing?), "Tw iligh t's" (twilight's), and "vas" (vast) suggest birds in flight creating/marking the air, possibly at twilight. The wordplay with "I sing" suggests the poet identifying with the birds' creative act.

*Sample B2/C1 response:* "The first poem captures the fragmented perception of a colorful sunset through broken syntax, while the second poem depicts birds as creators who 'invent' the air through flight and song, metaphorically representing the poet's own creative process."

**Question 2: "Identify what makes these poems modern and draw a parallel with modernist poetry."**

*Methodology:* First, read the "Modernist poetry" section on page 48. Extract key characteristics, then apply them to Cummings.

*Key characteristics from page 48:*
- "Modernist poets tended to favour intellect over emotion"
- "A more accessible, common speech language over the flowery style"
- "The lyrics are often shorter, sharper"
- "Freedom of form and content is at the heart of modern poetry"
- "The syntax is not always rigorous"

*Applying to Cummings:*
- **Intellect over emotion:** Cummings forces readers to *think* about how language creates meaning—the visual fragmentation makes us analyze, not just feel.
- **Common speech:** He uses simple words ("sky," "sweet," "birds") but arranges them unconventionally.
- **Shorter, sharper:** The poems are brief; each fragment delivers impact.
- **Freedom of form:** The words spill across the page unconventionally—this is radical formal freedom.
- **Non-rigorous syntax:** Traditional grammar is abandoned; meaning emerges from spatial arrangement.

*Sample analysis:* "Cummings exemplifies modernist poetry's revolt against convention. Like his contemporaries, he replaces traditional meter and rhyme with visual experimentation, forcing readers to construct meaning actively rather than passively receive it. His simple vocabulary democratizes poetry while his complex arrangements intellectualize the reading experience."

**Question 3: "Explain how this original form gives access to the meaning of the poems."**

*Methodology:* Look at specific formal choices and connect them to meaning.

*For "the sky was can dy":*
- Words split across lines mimic how we actually perceive a sunset—not as a unified whole, but as separate sensations (colors, light, sweetness)
- "can dy" (candy) suggests the sweetness/pleasure of the visual experience
- The isolation of "lu" and "mi" in "lu mi nous" forces slow reading, mimicking the gradual emergence of light
- The vertical arrangement mirrors looking up at the sky

*For "birds here,in ven ting air":*
- "in ven ting" split suggests the active, ongoing process of creation
- "U" (you) isolated invites reader participation
- "Ising" plays on "I sing" and "icing"—both artistic creation and a surface being covered/transformed
- The scattered words mimic birds scattered across the sky

*Sample analysis:* "Cummings' form is not decorative but functional—it enacts the very experience it describes. The fragmented words in the first poem recreate the way light and color disperse across the evening sky, each isolated syllable demanding attention like an individual hue. Similarly, the scattered words of the second poem visualize birds in flight, their positions on the page creating a kind of word-skyscape. The reader must actively piece together meaning, just as one pieces together a visual scene."

**Question 4: "Write down three questions you could ask him about his statement."**

*Statement:* "If poetry is your goal, you've got to forget all about punishments and all about rewards."

*Sample B2/C1 questions:*
1. "When you say 'forget punishments and rewards,' are you asking poets to ignore public reception entirely, or simply to prioritize artistic vision over it?"

2. "Your poems were initially rejected by publishers who found them incomprehensible—did you ever doubt your experimental approach when facing these 'punishments'?"

3. "If a poet creates work that no one can understand, does the poetry still achieve its 'goal,' or does communication with an audience matter?"

4. ✨ BAC APPLICATION BRIDGE

**Written Synthesis Application:**
Cummings would be an excellent example in a synthesis on "L'art qui fait débat" (Art that sparks debate). You could argue that Cummings provoked controversy not through shocking content but through revolutionary form—challenging what poetry *is*.

*Sample synthesis paragraph:*
"E.E. Cummings exemplifies how formal innovation can itself constitute artistic protest. His poems on page 40, with their fragmented words and unconventional layouts, sparked debate not about subject matter but about the very definition of poetry. By forcing readers to question whether text arranged visually on a page constitutes 'verse,' Cummings anticipated later debates about conceptual art and the boundaries of artistic media."

**Oral Portfolio Integration:**
For your oral presentation (10 minutes + 10 min Q&A), you could create a dossier including:
1. One Cummings poem from page 40
2. The "Modernist poetry" focus section from page 48
3. A second controversial artwork from this unit (e.g., Hirst's "God Knows Why" on page 43)
4. An article about artistic controversy (e.g., the Jeff Koons article referenced on page 46)

*Possible presentation structure:*
- Introduction: What makes art "controversial"? (2 min)
- Document 1: Cummings' formal revolution (3 min)
- Document 2: Hirst's material provocation (3 min)
- Synthesis: Different ways art challenges conventions (2 min)

**Grand Oral Connection:**
Possible question: "How do artists use formal experimentation to challenge social and artistic conventions?"

*This could connect to orientation projects in:*
- Art history/criticism
- Creative writing
- Cultural journalism
- Museum studies

**Translation Practice (relevant to written exam):**
Translate Cummings presents unique challenges. How would you render "the sky was can dy" in French while preserving the visual fragmentation? Possible approaches:
- Keep English words but explain in commentary
- Create equivalent French word splits ("le ciel était bon bon")
- Focus on meaning in translation, discuss form in analysis

5. 🚀 INTERACTIVE NEXT STEPS

Would you like to:
1. **Analyze the second Cummings poem** ("birds here,in ven ting air") in similar depth?
2. **Compare Cummings with another modernist poet** mentioned in the focus section?
3. **Explore how other artists in this unit** (Turner, Hirst, Haring) sparked different kinds of debates?
4. **Practice writing a BAC synthesis paragraph** using Cummings as your main example?
5. **Build an oral portfolio entry** around experimental poetry?

Just let me know which pathway interests you!"""

    # AFRICA UNIT DEEP DIVE
    elif unit_key == "africa":
        return f"""1. 📚 SOURCE GROUNDING - TEXTBOOK CONTEXT
- **LLCE Unit:** {unit_data['title']} (pages {unit_data['pages']})
- **Theme:** {unit_data.get('theme')}
- **Key Authors:** {', '.join(unit_data.get('authors', []))}
- **Focus Sections:** {', '.join(unit_data.get('focus_sections', []))}

2. 🎯 PRESENT THE CORE MATERIALS
Your textbook provides these key documents:

**Literary Texts:**
- Joseph Conrad, "Heart of Darkness" excerpt (page 20)
- Chinua Achebe, "Things Fall Apart" excerpt (page 21)
- Mike Phillips, "Visions of Africa" essay (page 23)
- Noo Saro-Wiwa, "Looking for Transwonderland" excerpt (page 34 - translation exercise)
- Ngugi Wa Thiong'o, "Decolonising the Mind" excerpt (page 27)

**Visual Documents:**
- Satirical drawing on colonialism (page 20)
- Andrew Gilbert installation (page 22)
- Afrochella Festival poster (page 26)
- Hank Willis Thomas, "Raise up" (page 29)

**Video/Audio Resources:**
- Lupita Nyong'o on Black Panther (page 22, code: 201lce005)
- Dada Masilo interview: Swan Lake meets Africa (page 27, code: 201lce006)
- Chimamanda Ngozi Adichie on "The danger of a single story" (referenced page 25)

**Focus Sections (pages 28-29):**
- Afrofuturism
- Black Panther
- From colonialism to postcolonialism
- Author biographies

**Language Resources:**
- Grammar: Pluperfect simple, Superlatives (page 32)
- Pronunciation: The two l consonants, Word stress (page 33)
- Translation practice (page 34)
- Exam practice: Synthesis (page 35)

3. 🔍 GUIDED ANALYSIS - KEY QUESTIONS FROM YOUR TEXTBOOK

**From page 20 (Conrad extract):**
*Question 4: "Imagine the description of the white narrator by the African fireman."*

*Methodology:* This exercise asks you to reverse the colonial gaze—to imagine how Africans perceived Europeans.

*Key elements to consider:*
- The fireman sees the narrator as strange, possibly threatening
- The narrator's incomprehensible technology (steam gauges, pipes)
- The power dynamic—the narrator is in charge but seems dependent on the fireman's labor
- The condescending way the narrator describes the fireman would surely be reciprocated

*Sample response:* "The pale man watches me tend the boiler with suspicious eyes. He thinks I don't understand this machine, but I know when the water runs low. He calls me 'savage' yet relies on my hands to keep the boat moving. His skin looks sickly, like someone who never sees sun. When he speaks to the other pale men, they laugh and point at me. I wonder what god they worship that makes them so cold."

**From page 23 (Mike Phillips essay):**
*Question 5: "Write a short article for an art magazine to present the exhibition and its goals."*

*Structure for your article:*
1. **Introduction:** Present the Tate exhibition "Seeing Africa" and its premise
2. **The problem:** How 19th-century colonialism shaped European visions of Africa
3. **The exhibition's purpose:** To uncover and challenge these inherited perspectives
4. **Key works:** Mention specific artists and their approaches
5. **Conclusion:** Why this matters today—how we can learn to see differently

*Key vocabulary to include:*
- "Biological determinism," "repressed sexuality," "romanticised vision"
- "Colonising gaze," "psychological confrontation"
- "Traumas and complexities of race"

**From page 26 (Afrochella poster):**
*Question 3: "Afrochella's 'purposes are to tell the New Africa story from a native's perspective.' Comment on this statement."*

*Analysis points:*
- Contrast with Conrad's external perspective (page 20)
- Connection to Adichie's "single story" concept (page 25)
- The importance of who tells the story
- "New Africa" implies rejecting old stereotypes
- "Native's perspective" emphasizes authenticity and self-representation

4. ✨ BAC APPLICATION BRIDGE

**Written Synthesis Topic (from page 35):**
"Write a commentary on the three documents. Use the following guidelines:
a. Explain how art helps link the past, present and future.
b. Analyse how modern art illustrates Africa's development.
c. Show how art is a powerful tool to create a new Africa."

*Sample thesis:* "Through the juxtaposition of colonial and postcolonial works, contemporary African art demonstrates that reclaiming narrative control is essential to linking Africa's traumatic past with its innovative future."

**Oral Portfolio Structure:**
Your dossier could include:
1. Achebe's "Things Fall Apart" excerpt (page 21) - the literary response to Conrad
2. Afrochella poster (page 26) - contemporary cultural celebration
3. Dada Masilo video (page 27) - artistic innovation blending traditions
4. Your personal reflection on representation

**Grand Oral Question Possibility:**
"Can art heal historical trauma and reshape cultural identity?"

5. 🚀 INTERACTIVE NEXT STEPS

Choose your focus:
1. Compare Conrad and Achebe's representations of Africa
2. Explore Afrofuturism through the Black Panther focus section
3. Analyze the Dada Masilo video and her fusion of traditions
4. Prepare for the written synthesis on page 35
5. Build your oral portfolio with documents from this unit"""

    # EMOTIONS UNIT DEEP DIVE
    elif unit_key == "emotions":
        return f"""1. 📚 SOURCE GROUNDING - TEXTBOOK CONTEXT
- **LLCE Unit:** {unit_data['title']} (pages {unit_data['pages']})
- **Theme:** {unit_data.get('theme')}
- **Key Authors:** {', '.join(unit_data.get('authors', []))}
- **Focus Sections:** {', '.join(unit_data.get('focus_sections', []))}

2. 🎯 PRESENT THE CORE MATERIALS

**Literary Texts:**
- Jane Austen, "Sense and Sensibility" excerpt (page 90)
- Max Porter, "Grief is the Thing with Feathers" excerpt (page 94)
- Emily Brontë, "Wuthering Heights" excerpt (page 96)
- Boys Don't Cry song lyrics (page 93)

**Visual Documents:**
- Frederick William Burton, "Hellel and Hildebrand" (page 91)
- Wonder Woman comic (page 92)
- Edward Killingworth Johnson, "The Young Widow" (page 95)
- Paul Day, "The Meeting Place" statue (page 97)

**Video/Audio Resources:**
- Stiff Upper Lip video (page 91, code: 201lce031)
- Sigourney Weaver interview (page 93, code: 201lce033)
- The Descendants clip (page 94, code: 201lce034)
- Fleabag wedding speech (page 97, code: 201lce035)

**Focus Sections (pages 98-99):**
- Romanticism
- Stiff upper lip
- Author biographies

**Language Resources:**
- Grammar: Exclamative sentences, While/during/for (page 102)
- Pronunciation: /i/ and /i:/ vowels, -ate words (page 103)
- Translation practice (page 104)
- Exam practice (page 105)

3. 🔍 GUIDED ANALYSIS

**Key Question from page 90 (Austen extract):**
*Question 3: "Explain how the title of the book reflects the characters' personalities."*

*Analysis:*
- **Sense (Elinor):** Reason, restraint, social awareness, hiding feelings
- **Sensibility (Marianne):** Emotion, spontaneity, public feeling, vulnerability
- The novel explores the tension between these approaches and suggests a balance is needed

**Key Question from page 96 (Brontë extract):**
*Question 4: "Explain in your own words the definition of love Catherine gives."*

*Catherine's definition:*
"I am Heathcliff — he's always, always in my mind — not as a pleasure, any more than I am always a pleasure to myself — but as my own being."

*Analysis:* Love here is not about pleasure or happiness—it's about identity itself. Catherine doesn't love Heathcliff as a separate person; he IS her. This explains why marrying Edgar feels like self-betrayal.

4. ✨ BAC APPLICATION BRIDGE

**Possible Synthesis Topic:**
"How do British texts represent the conflict between emotional expression and social restraint?"

**Oral Portfolio Idea:**
Compare Austen's representation of restrained emotion (Elinor) with Porter's contemporary grief narrative—how has the "stiff upper lip" evolved?

5. 🚀 INTERACTIVE NEXT STEPS

1. Analyze the "Stiff Upper Lip" concept in British culture
2. Compare Austen and Brontë's treatment of emotion
3. Explore the Romanticism focus section
4. Practice translation with the page 104 exercise"""

    # GENERAL LLCE DEEP DIVE TEMPLATE
    else:
        unit_info = unit_data['title'] if unit_data else "General LLCE curriculum"
        unit_pages = unit_data['pages'] if unit_data else "various pages"
        
        return f"""1. 📚 SOURCE GROUNDING - TEXTBOOK CONTEXT
- **LLCE Unit:** {unit_info} (pages {unit_pages})
- **BAC English Specialty:** Langues, Littératures et Cultures Étrangères
- **Focus:** Anglophone literature, culture, and critical analysis

2. 🎯 PRESENT THE CORE MATERIALS
Your textbook contains these resources related to your query:

**Primary Documents:**
Check
