from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os
import re
from typing import Dict, List, Optional, Any

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

# ============ COMPREHENSIVE AUTHOR DATABASE ============
# This contains every author from the syllabus with their details

AUTHORS_DATABASE = {
    # Unit 1: Africa
    "chimamanda ngozi adichie": {
        "name": "Chimamanda Ngozi Adichie",
        "unit": "africa",
        "nationality": "Nigerian",
        "works": [
            {"title": "The Danger of a Single Story", "type": "TED Talk", "page": 25, "description": "Speech about the dangers of monolithic narratives"},
            {"title": "Purple Hibiscus", "type": "Novel", "page": 31, "description": "Coming-of-age story set in Nigeria"},
            {"title": "Half of a Yellow Sun", "type": "Novel", "page": 31, "description": "Novel about the Nigerian Civil War"}
        ],
        "key_themes": ["Postcolonialism", "Feminism", "Identity", "Representation", "The danger of single stories"],
        "biography": "Chimamanda Ngozi Adichie is a Nigerian writer whose work explores feminism, postcolonialism, and identity. She was born in Enugu, Nigeria in 1977.",
        "fun_fact": "Her 2009 TED Talk 'The Danger of a Single Story' is one of the most-viewed TED Talks of all time.",
        "focus_sections": ["Postcolonialism", "African literature"],
        "related_authors": ["Chinua Achebe", "Ngugi Wa Thiong'o"]
    },
    "chinua achebe": {
        "name": "Chinua Achebe",
        "unit": "africa",
        "nationality": "Nigerian",
        "works": [
            {"title": "Things Fall Apart", "type": "Novel", "page": 21, "description": "Seminal novel about pre-colonial Nigeria and the arrival of Europeans"},
            {"title": "No Longer at Ease", "type": "Novel", "page": 29, "description": "Sequel to Things Fall Apart"},
            {"title": "Arrow of God", "type": "Novel", "page": 29, "description": "Third novel in the trilogy"}
        ],
        "key_themes": ["Colonialism", "Igbo culture", "Tradition vs change", "Masculinity"],
        "biography": "Chinua Achebe was a Nigerian novelist and critic, widely considered the father of modern African literature.",
        "fun_fact": "Things Fall Apart has sold over 20 million copies worldwide and has been translated into 57 languages.",
        "focus_sections": ["From colonialism to postcolonialism"],
        "related_authors": ["Chimamanda Ngozi Adichie", "Joseph Conrad"]
    },
    "joseph conrad": {
        "name": "Joseph Conrad",
        "unit": "africa",
        "nationality": "Polish-British",
        "works": [
            {"title": "Heart of Darkness", "type": "Novel", "page": 20, "description": "Novella about a voyage up the Congo River"}
        ],
        "key_themes": ["Colonialism", "Imperialism", "Darkness", "Civilization vs savagery"],
        "biography": "Joseph Conrad was a Polish-British writer regarded as one of the greatest novelists in English. His experience as a mariner informed much of his work.",
        "fun_fact": "The spaceship in the Ridley Scott film Alien is named Nostromo after Conrad's 1904 novel.",
        "focus_sections": ["Colonialism"],
        "related_authors": ["Chinua Achebe"]
    },
    "ngugi wa thiong'o": {
        "name": "Ngugi Wa Thiong'o",
        "unit": "africa",
        "nationality": "Kenyan",
        "works": [
            {"title": "Decolonising the Mind", "type": "Essay", "page": 27, "description": "Essay on language and African literature"}
        ],
        "key_themes": ["Decolonization", "Language", "African identity", "Postcolonial theory"],
        "biography": "Ngũgĩ wa Thiong'o is a Kenyan writer and academic who writes primarily in Gikuyu and English. He advocates for African literature in African languages.",
        "fun_fact": "He was imprisoned in Kenya for his controversial play 'Ngaahika Ndeenda' and later went into exile.",
        "focus_sections": ["Decolonising the mind"],
        "related_authors": ["Chinua Achebe"]
    },
    "dada masilo": {
        "name": "Dada Masilo",
        "unit": "africa",
        "nationality": "South African",
        "works": [
            {"title": "Swan Lake", "type": "Ballet", "page": 27, "description": "Reimagining of Swan Lake with African dance"},
            {"title": "Romeo and Juliet", "type": "Ballet", "page": 29, "description": "Multiracial adaptation of Shakespeare"}
        ],
        "key_themes": ["Fusion", "Identity", "Tradition and modernity", "Challenging stereotypes"],
        "biography": "Dada Masilo is a South African dancer and choreographer known for reinterpreting classical ballets with African dance and contemporary themes.",
        "fun_fact": "In her gay interpretation of Swan Lake, the male dancer performing Odile is the only one to perform en pointe.",
        "focus_sections": ["Afrofuturism", "Contemporary African art"],
        "related_authors": []
    },
    
    # Unit 2: Art (Modern Art)
    "e.e. cummings": {
        "name": "E.E. Cummings",
        "unit": "art",
        "nationality": "American",
        "works": [
            {"title": "the sky was can dy", "type": "Poem", "page": 40, "description": "Concrete poem about a sunset"},
            {"title": "birds here,in ven ting air", "type": "Poem", "page": 40, "description": "Poem about birds and creation"}
        ],
        "key_themes": ["Modernism", "Visual poetry", "Individualism", "Love and nature"],
        "biography": "Edward Estlin Cummings was an American poet, painter, and playwright known for his unconventional punctuation and syntax.",
        "fun_fact": "Cummings was arrested by the French on suspicion of espionage during World War I.",
        "focus_sections": ["Modernist poetry"],
        "related_authors": ["Ezra Pound", "Hilda Doolittle"]
    },
    "j.m.w. turner": {
        "name": "J.M.W. Turner",
        "unit": "art",
        "nationality": "British",
        "works": [
            {"title": "The Fighting Temeraire", "type": "Painting", "page": 38, "description": "Painting of a ship being towed to be scrapped"},
            {"title": "Rain, Steam and Speed", "type": "Painting", "page": 51, "description": "Painting of a steam locomotive"},
            {"title": "Snow Storm - Steam-Boat off a Harbour's Mouth", "type": "Painting", "page": 98, "description": "Dramatic storm scene"}
        ],
        "key_themes": ["Sublime", "Light", "Nature", "Industrial Revolution"],
        "biography": "Joseph Mallord William Turner was a British landscape painter of the 18th and 19th centuries, known as the 'Painter of Light'.",
        "fun_fact": "Turner was said to have had himself tied to the mast of a ship during a storm to experience the power of the sea.",
        "focus_sections": ["Romanticism"],
        "related_authors": ["John Constable"]
    },
    "mae west": {
        "name": "Mae West",
        "unit": "art",
        "nationality": "American",
        "works": [
            {"title": "Sex", "type": "Play", "page": 45, "description": "Broadway play about prostitution that led to her arrest"},
            {"title": "She Done Him Wrong", "type": "Film", "page": 45, "description": "Film that saved Paramount from bankruptcy"}
        ],
        "key_themes": ["Sexuality", "Censorship", "Female empowerment", "Controversy"],
        "biography": "Mae West was an American actress, playwright, and sex symbol known for her bawdy double entendres and independent spirit.",
        "fun_fact": "She served eight days in jail for 'Sex' and ate dinner with the warden and his wife.",
        "focus_sections": ["Scandal in the arts"],
        "related_authors": []
    },
    "damien hirst": {
        "name": "Damien Hirst",
        "unit": "art",
        "nationality": "British",
        "works": [
            {"title": "God Knows Why", "type": "Sculpture", "page": 43, "description": "Artwork featuring dead animals in formaldehyde"}
        ],
        "key_themes": ["Death", "Controversy", "Consumerism", "Art as spectacle"],
        "biography": "Damien Hirst is a British artist and art collector who is said to be the richest living artist, known for works exploring death.",
        "fun_fact": "As a student, he worked in a mortuary, which influenced his work.",
        "focus_sections": ["Contemporary art"],
        "related_authors": ["Marc Quinn", "Keith Haring"]
    },
    "keith haring": {
        "name": "Keith Haring",
        "unit": "art",
        "nationality": "American",
        "works": [
            {"title": "Andy Mouse 3", "type": "Artwork", "page": 47, "description": "Pop art featuring Andy Warhol as Mickey Mouse"}
        ],
        "key_themes": ["Pop Art", "AIDS awareness", "Street art", "Accessibility"],
        "biography": "Keith Haring was an American artist whose graffiti-inspired drawings conveyed energy and optimism before his death from AIDS.",
        "fun_fact": "He opened the Pop Shop in New York so everyone could buy affordable pieces of his work.",
        "focus_sections": ["Pop Art"],
        "related_authors": ["Andy Warhol", "Roy Lichtenstein"]
    },
    "marc quinn": {
        "name": "Marc Quinn",
        "unit": "art",
        "nationality": "British",
        "works": [
            {"title": "Self", "type": "Sculpture", "page": 43, "description": "Self-portrait made of frozen blood"}
        ],
        "key_themes": ["Identity", "Mortality", "The body", "Self-portraiture"],
        "biography": "Marc Quinn is a British visual artist whose work explores what it means to be human through subjects including the body and genetics.",
        "fun_fact": "Each Self sculpture is made of 4.5 litres of his own blood taken over five months.",
        "focus_sections": ["Contemporary art"],
        "related_authors": ["Damien Hirst"]
    },
    "j.d. salinger": {
        "name": "J.D. Salinger",
        "unit": "art",
        "nationality": "American",
        "works": [
            {"title": "The Catcher in the Rye", "type": "Novel", "page": 42, "description": "Controversial coming-of-age novel"}
        ],
        "key_themes": ["Alienation", "Teenage rebellion", "Authenticity", "Censorship"],
        "biography": "J.D. Salinger was an American writer known for his reclusive nature and his novel The Catcher in the Rye.",
        "fun_fact": "The Catcher in the Rye is both one of the most censored books in American schools and one of the most taught.",
        "focus_sections": ["Scandal in 50s America"],
        "related_authors": []
    },
    
    # Unit 3: Debate
    "william shakespeare": {
        "name": "William Shakespeare",
        "unit": "debate",
        "nationality": "British",
        "works": [
            {"title": "Richard III", "type": "Play", "page": 60, "description": "Historical play featuring persuasive rhetoric"},
            {"title": "Much Ado About Nothing", "type": "Play", "page": 71, "description": "Comedy with witty banter and debate"},
            {"title": "Love's Labour's Lost", "type": "Play", "page": 60, "description": "Play about wit and wordplay"}
        ],
        "key_themes": ["Rhetoric", "Power", "Deception", "Politics"],
        "biography": "William Shakespeare was an English playwright and poet, widely regarded as the greatest writer in the English language.",
        "fun_fact": "In 1759, the character Cleopatra was played by a woman for the first time in the play's 150-year history.",
        "focus_sections": ["The art of rhetoric"],
        "related_authors": []
    },
    "alexander hamilton": {
        "name": "Alexander Hamilton",
        "unit": "debate",
        "nationality": "American",
        "works": [
            {"title": "Cabinet Battle #2", "type": "Song", "page": 66, "description": "Rap battle from Hamilton musical"}
        ],
        "key_themes": ["Debate", "Politics", "Constitution", "Economics"],
        "biography": "Alexander Hamilton was a Founding Father of the United States and the first Secretary of the Treasury.",
        "fun_fact": "He was killed in a duel by Vice President Aaron Burr in 1804.",
        "focus_sections": ["A great debater: Alexander Hamilton"],
        "related_authors": ["Lin-Manuel Miranda"]
    },
    "barack obama": {
        "name": "Barack Obama",
        "unit": "debate",
        "nationality": "American",
        "works": [
            {"title": "Immigration reform speech", "type": "Speech", "page": 62, "description": "Presidential speech on immigration"}
        ],
        "key_themes": ["Rhetoric", "Hope", "Change", "Unity"],
        "biography": "Barack Obama was the 44th President of the United States and the first African American to hold the office.",
        "fun_fact": "He collects Spider-Man and Conan the Barbarian comics.",
        "focus_sections": ["The art of rhetoric"],
        "related_authors": []
    },
    "lin-manuel miranda": {
        "name": "Lin-Manuel Miranda",
        "unit": "debate",
        "nationality": "American",
        "works": [
            {"title": "Hamilton", "type": "Musical", "page": 66, "description": "Hip-hop musical about Alexander Hamilton"}
        ],
        "key_themes": ["Storytelling", "History", "Identity", "Musical innovation"],
        "biography": "Lin-Manuel Miranda is an American actor, composer, and writer known for creating the musical Hamilton.",
        "fun_fact": "He got the idea for Hamilton from reading a biography of Alexander Hamilton at an airport.",
        "focus_sections": ["A great debater: Alexander Hamilton"],
        "related_authors": ["Alexander Hamilton"]
    },
    "denzel washington": {
        "name": "Denzel Washington",
        "unit": "debate",
        "nationality": "American",
        "works": [
            {"title": "The Great Debaters", "type": "Film", "page": 61, "description": "Film about a debate team"}
        ],
        "key_themes": ["Debate", "Civil rights", "Education", "Perseverance"],
        "biography": "Denzel Washington is an American actor and director known for roles in Malcolm X, Training Day, and The Great Debaters.",
        "fun_fact": "His oldest son, John David, was drafted by the NFL's St. Louis Rams in 2006.",
        "focus_sections": ["The Great Debaters"],
        "related_authors": []
    },
    
    # Unit 5: Emotions
    "jane austen": {
        "name": "Jane Austen",
        "unit": "emotions",
        "nationality": "British",
        "works": [
            {"title": "Sense and Sensibility", "type": "Novel", "page": 90, "description": "Novel contrasting理性 and emotion"},
            {"title": "Pride and Prejudice", "type": "Novel", "page": 101, "description": "Romantic novel with social satire"}
        ],
        "key_themes": ["Reason vs emotion", "Social class", "Marriage", "Irony"],
        "biography": "Jane Austen was an English novelist known for her social commentary and irony in works like Pride and Prejudice.",
        "fun_fact": "The 'Janeties' fan club was created in 1870 and still exists today!",
        "focus_sections": ["Stiff upper lip"],
        "related_authors": ["Emily Brontë"]
    },
    "emily brontë": {
        "name": "Emily Brontë",
        "unit": "emotions",
        "nationality": "British",
        "works": [
            {"title": "Wuthering Heights", "type": "Novel", "page": 96, "description": "Gothic novel of passion and revenge"}
        ],
        "key_themes": ["Passion", "Romanticism", "Nature", "Obsession"],
        "biography": "Emily Brontë was an English novelist and poet, best known for her only novel, Wuthering Heights.",
        "fun_fact": "She was the fifth of six children, including Charlotte and Anne Brontë, who also became writers.",
        "focus_sections": ["Romanticism"],
        "related_authors": ["Jane Austen"]
    },
    "max porter": {
        "name": "Max Porter",
        "unit": "emotions",
        "nationality": "British",
        "works": [
            {"title": "Grief is the Thing with Feathers", "type": "Novel", "page": 94, "description": "Experimental novel about grief"}
        ],
        "key_themes": ["Grief", "Loss", "Family", "Healing"],
        "biography": "Max Porter is a British writer and bookseller, best known for his debut novel Grief is the Thing with Feathers.",
        "fun_fact": "The title comes from Emily Dickinson's poem 'Hope is the thing with feathers'.",
        "focus_sections": ["Grief"],
        "related_authors": []
    },
    "the cure": {
        "name": "The Cure",
        "unit": "emotions",
        "nationality": "British",
        "works": [
            {"title": "Boys Don't Cry", "type": "Song", "page": 93, "description": "Song about male emotional repression"}
        ],
        "key_themes": ["Emotional repression", "Masculinity", "Vulnerability"],
        "biography": "The Cure is an English rock band formed in 1976, known for their Gothic rock and post-punk sound.",
        "fun_fact": "Their first label ended their contract after saying 'Not even people in prison would like these songs!'",
        "focus_sections": ["Stiff upper lip"],
        "related_authors": []
    },
    
    # Unit 7: Bildungsroman
    "charles dickens": {
        "name": "Charles Dickens",
        "unit": "bildungsroman",
        "nationality": "British",
        "works": [
            {"title": "Oliver Twist", "type": "Novel", "page": 129, "description": "Novel about an orphan's journey"}
        ],
        "key_themes": ["Social criticism", "Childhood", "Poverty", "Identity"],
        "biography": "Charles Dickens was an English writer and social critic, regarded as the greatest novelist of the Victorian era.",
        "fun_fact": "Many of his novels were first published in serialized form in magazines.",
        "focus_sections": ["Oliver Twist", "The Bildungsroman"],
        "related_authors": []
    },
    "j.k. rowling": {
        "name": "J.K. Rowling",
        "unit": "bildungsroman",
        "nationality": "British",
        "works": [
            {"title": "Harry Potter and the Philosopher's Stone", "type": "Novel", "page": 129, "description": "Fantasy coming-of-age novel"}
        ],
        "key_themes": ["Coming of age", "Friendship", "Good vs evil", "Identity"],
        "biography": "J.K. Rowling is a British author best known for the Harry Potter fantasy series.",
        "fun_fact": "She was the first person to become a billionaire from writing books.",
        "focus_sections": ["The Bildungsroman"],
        "related_authors": []
    },
    "maya angelou": {
        "name": "Maya Angelou",
        "unit": "bildungsroman",
        "nationality": "American",
        "works": [
            {"title": "Still I Rise", "type": "Poem", "page": 130, "description": "Empowering poem about resilience"}
        ],
        "key_themes": ["Resilience", "Identity", "Race", "Feminism"],
        "biography": "Maya Angelou was an American poet, memoirist, and civil rights activist.",
        "fun_fact": "She spoke six languages and worked as a streetcar conductor in San Francisco.",
        "focus_sections": ["Learning from role models"],
        "related_authors": []
    },
    
    # Unit 10: Music
    "bob dylan": {
        "name": "Bob Dylan",
        "unit": "music",
        "nationality": "American",
        "works": [
            {"title": "The Times They Are A-Changing", "type": "Song", "page": 182, "description": "Protest song of the 1960s"}
        ],
        "key_themes": ["Protest", "Social change", "Poetry", "Counterculture"],
        "biography": "Bob Dylan is an American singer-songwriter and Nobel Prize laureate in Literature.",
        "fun_fact": "He won the Nobel Prize in Literature in 2016, the first musician to do so.",
        "focus_sections": ["The Sixties"],
        "related_authors": []
    },
    "nina simone": {
        "name": "Nina Simone",
        "unit": "music",
        "nationality": "American",
        "works": [
            {"title": "To Be Young, Gifted and Black", "type": "Song", "page": 181, "description": "Anthem of Black pride"}
        ],
        "key_themes": ["Civil rights", "Black identity", "Empowerment"],
        "biography": "Nina Simone was an American singer, songwriter, and civil rights activist.",
        "fun_fact": "She was trained as a classical pianist and applied to the Curtis Institute, where she was rejected—she believed due to racism.",
        "focus_sections": ["Notting Hill Carnival"],
        "related_authors": []
    },
    "bruce springsteen": {
        "name": "Bruce Springsteen",
        "unit": "music",
        "nationality": "American",
        "works": [
            {"title": "Born in the USA", "type": "Song", "page": 181, "description": "Often misunderstood patriotic song"}
        ],
        "key_themes": ["Working class", "America", "Patriotism", "Social criticism"],
        "biography": "Bruce Springsteen is an American singer-songwriter known for his heartland rock sound and working-class themes.",
        "fun_fact": "Born in the USA was often misinterpreted as a jingoistic anthem when it's actually critical of America's treatment of Vietnam veterans.",
        "focus_sections": ["Born in the USA: misunderstood songs"],
        "related_authors": []
    },
    
    # Unit 11: Migration
    "jacob lawrence": {
        "name": "Jacob Lawrence",
        "unit": "migration",
        "nationality": "American",
        "works": [
            {"title": "The Migration Series", "type": "Painting", "page": 200, "description": "Series depicting the Great Migration"}
        ],
        "key_themes": ["Migration", "African American experience", "History", "Identity"],
        "biography": "Jacob Lawrence was an American painter known for his portrayal of African American historical subjects.",
        "fun_fact": "He was only 23 when he completed The Migration Series, which made him famous.",
        "focus_sections": ["The Great Migration"],
        "related_authors": []
    },
    "amy tan": {
        "name": "Amy Tan",
        "unit": "migration",
        "nationality": "American",
        "works": [
            {"title": "The Joy Luck Club", "type": "Novel", "page": 203, "description": "Novel about Chinese-American mothers and daughters"}
        ],
        "key_themes": ["Immigration", "Mother-daughter relationships", "Identity", "Cultural conflict"],
        "biography": "Amy Tan is an American writer whose work explores mother-daughter relationships and the Chinese-American experience.",
        "fun_fact": "The Joy Luck Club was adapted into a film in 1993, with Tan co-writing the screenplay.",
        "focus_sections": ["Melting pot and salad bowl"],
        "related_authors": []
    },
    "zadie smith": {
        "name": "Zadie Smith",
        "unit": "migration",
        "nationality": "British",
        "works": [
            {"title": "White Teeth", "type": "Novel", "page": 220, "description": "Novel about multicultural London"}
        ],
        "key_themes": ["Multiculturalism", "Identity", "Race", "London"],
        "biography": "Zadie Smith is a British novelist and essayist known for her debut novel White Teeth.",
        "fun_fact": "She wrote White Teeth while still a student at Cambridge University.",
        "focus_sections": ["Integration or cohabitation"],
        "related_authors": []
    }
}

# LLCE Curriculum Units
LLCE_UNITS = {
    "africa": {
        "title": "Africa: The Danger of a Single Story",
        "pages": "18-37",
        "theme": "Art et contestation",
        "authors": ["Chimamanda Ngozi Adichie", "Joseph Conrad", "Chinua Achebe", "Ngugi Wa Thiong'o", "Dada Masilo"],
        "focus_sections": ["Afrofuturism", "Black Panther", "From colonialism to postcolonialism"],
        "grammar": {"page": 32, "topics": ["Le pluperfect simple", "Le superlatif de supériorité"]},
        "pronunciation": {"page": 33, "topics": ["Les deux consonnes l", "L'accentuation"]},
        "translation": {"page": 34},
        "exam_practice": {"page": 35}
    },
    "art": {
        "title": "Sparking Debates with Modern Art",
        "pages": "38-57",
        "theme": "L'art qui fait débat",
        "authors": ["E.E. Cummings", "J.M.W. Turner", "Mae West", "Damien Hirst", "Keith Haring", "Marc Quinn", "J.D. Salinger"],
        "focus_sections": ["Pop Art", "Modernist poetry", "Scandal in 50s America: The Catcher in the Rye"],
        "grammar": {"page": 52, "topics": ["Les verbes de perception", "La forme du verbe après un modal"]},
        "pronunciation": {"page": 53, "topics": ["La voyelle longue /a:/", "La ION rule"]},
        "translation": {"page": 54},
        "exam_practice": {"page": "55-57"}
    },
    "debate": {
        "title": "Up for Debate!",
        "pages": "58-77",
        "theme": "L'art du débat",
        "authors": ["William Shakespeare", "Alexander Hamilton", "Barack Obama", "Lin-Manuel Miranda", "Denzel Washington"],
        "focus_sections": ["The O.J. Simpson case", "A great debater: Alexander Hamilton"],
        "grammar": {"page": 72, "topics": ["L'expression de l'opposition", "Le subjonctif"]},
        "pronunciation": {"page": 73, "topics": ["Les diphtongues /əʊ/ et /aʊ/", "L'accentuation des mots en -ic(s)"]},
        "translation": {"page": 74},
        "exam_practice": {"page": 75}
    },
    "censorship": {
        "title": "Censorship, an American Art?",
        "pages": "78-85",
        "theme": "Censorship",
        "authors": ["Arthur Miller"],
        "focus_sections": ["The Hays Code", "Banned Books Week"],
        "grand_oral": {"page": 84}
    },
    "emotions": {
        "title": "I Feel, Therefore I Am",
        "pages": "88-107",
        "theme": "Expression des émotions",
        "authors": ["Jane Austen", "Emily Brontë", "Max Porter", "The Cure"],
        "focus_sections": ["Romanticism", "Stiff upper lip"],
        "grammar": {"page": 102, "topics": ["La phrase exclamative", "While, during et for"]},
        "pronunciation": {"page": 103, "topics": ["Les voyelles /i/ et /i:/", "Prononciation des mots en -ate"]},
        "translation": {"page": 104},
        "exam_practice": {"page": 105}
    },
    "portraits": {
        "title": "Portraits of Fiction",
        "pages": "108-127",
        "theme": "Mise en scène de soi",
        "authors": ["George Orwell", "Vivian Maier", "Eminem"],
        "focus_sections": ["Breaking the fourth wall", "Cameos", "Mise en abyme"],
        "grammar": {"page": 122, "topics": ["Tags et reprises elliptiques", "By et le gérondif"]},
        "pronunciation": {"page": 123, "topics": ["La voyelle longue /ɔ:/", "La prononciation des auxiliaires"]},
        "translation": {"page": 124},
        "exam_practice": {"page": 125}
    },
    "bildungsroman": {
        "title": "You Live, You Learn",
        "pages": "128-147",
        "theme": "Initiation, apprentissage",
        "authors": ["Charles Dickens", "J.K. Rowling", "Maya Angelou"],
        "focus_sections": ["Oliver Twist", "The Bildungsroman"],
        "grammar": {"page": 142, "topics": ["Les adjectifs composés", "For et since"]},
        "pronunciation": {"page": 143, "topics": ["La voyelle brève /ʌ/", "L'accentuation des mots composés"]},
        "translation": {"page": 144},
        "exam_practice": {"page": 145}
    },
    "lgbtq": {
        "title": "Gay Identity in the 1980s",
        "pages": "148-155",
        "theme": "LGBTQ+ history",
        "authors": ["Armistead Maupin", "Tony Kushner", "Thom Gunn"],
        "focus_sections": ["AIDS crisis", "ACT UP"],
        "grand_oral": {"page": 154}
    },
    "exploration": {
        "title": "Mankind, a Species Designed for Exploration?",
        "pages": "158-177",
        "theme": "Exploration et aventure",
        "authors": ["Rudyard Kipling", "Arthur C. Clarke"],
        "focus_sections": ["The age of exploration", "Science fiction", "Space race"],
        "grammar": {"page": 172, "topics": ["Les inversions sujet-auxiliaire", "Les structures corrélatives"]},
        "pronunciation": {"page": 173, "topics": ["La voyelle /ʌ/ et la réduction vocalique"]},
        "translation": {"page": 174},
        "exam_practice": {"page": 175}
    },
    "music": {
        "title": "The Power of Music",
        "pages": "178-197",
        "theme": "Music and identity",
        "authors": ["Bob Dylan", "Nina Simone", "Bruce Springsteen", "Woody Guthrie", "James Brown", "Midnight Oil"],
        "focus_sections": ["The Sixties", "Notting Hill Carnival", "Relocation of Japanese Americans during WWII"],
        "grammar": {"page": 192, "topics": ["La place des prépositions dans les relatives", "Les structures causatives"]},
        "pronunciation": {"page": 193, "topics": ["La voyelle brève /ʊ/", "L'intonation"]},
        "translation": {"page": 194},
        "exam_practice": {"page": 195}
    },
    "migration": {
        "title": "Migration: Journeys to a New Life",
        "pages": "198-217",
        "theme": "Migration et exil",
        "authors": ["Jacob Lawrence", "Amy Tan", "Zadie Smith", "Natalie Diaz"],
        "focus_sections": ["Famous immigrant success stories", "Melting pot and salad bowl", "The Great Migration"],
        "grammar": {"page": 212, "topics": ["As et like", "Which et what"]},
        "pronunciation": {"page": 213, "topics": ["La consonne /j/", "Les suffixes accentués"]},
        "translation": {"page": 214},
        "exam_practice": {"page": 215}
    },
    "food": {
        "title": "A Taste for Adventure",
        "pages": "218-225",
        "theme": "Food and culture",
        "authors": ["Jonathan Swift", "Richard Blanco", "Zadie Smith"],
        "focus_sections": ["Food and identity"],
        "grand_oral": {"page": 226}
    }
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
    "
