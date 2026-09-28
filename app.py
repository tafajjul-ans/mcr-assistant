import os
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATA_FILE = "college_data.txt"

def load_college_data():
    """Reads all lines from the text file"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def tokenize(text):
    """Custom tokenizer: converts text to lowercase and extracts unique words"""
    return set(re.findall(r'\b\w+\b', text.lower()))

def calculate_similarity_score(query_tokens, line_tokens):
    """Custom Scoring Algorithm: calculates token intersection ratio"""
    if not query_tokens or not line_tokens:
        return 0.0
    intersection = query_tokens.intersection(line_tokens)
    # Overlap coefficient or Jaccard-like score
    score = len(intersection) / float(len(query_tokens))
    return score

def custom_ai_engine(user_query):
    """Custom Search and Response Formatting Algorithm"""
    lines = load_college_data()
    if not lines:
        return "Maaf kijiye, abhi college data file khali hai ya milti nahi hai."

    query_tokens = tokenize(user_query)
    
    best_match_line = None
    highest_score = 0.0

    # Step 1: Score each line based on custom keyword matching
    for line in lines:
        line_tokens = tokenize(line)
        score = calculate_similarity_score(query_tokens, line_tokens)
        
        # Give bonus weight if exact keywords like 'syllabus', 'room', 'bathroom', 'principal' match
        for q_token in query_tokens:
            if q_token in line.lower():
                score += 0.1

        if score > highest_score:
            highest_score = score
            best_match_line = line

    # Threshold for matching (0.15 means at least some contextual words matched)
    if highest_score >= 0.15 and best_match_line:
        # Step 2: Separate main sentence and metadata brackets [...]
        bracket_match = re.search(r'\[(.*?)\]', best_match_line)
        metadata_str = bracket_match.group(1) if bracket_match else ""
        
        # Clean text without brackets for clean reading
        clean_sentence = re.sub(r'\[.*?\]', '', best_match_line).strip()
        
        # Step 3: Format custom natural response in Hinglish
        response_text = f"**MCR Assistant (Custom Engine):**\n\n📌 **Jankari:** {clean_sentence}"
        
        if metadata_str:
            response_text += f"\n\n📍 **Location / Details:** `{metadata_str}`"
            
        # Check if query is about syllabus/links
        if "http" in best_match_line:
            url_match = re.search(r'(https?://[^\s]+)', best_match_line)
            if url_match:
                response_text += f"\n\n🔗 **Direct Link:** [Click Here to Open]({url_match.group(1)})"

        return response_text
    else:
        return "Maaf kijiye, is sawal ki jankari abhi mere local data me nahi hai. Aap data file me yeh line add kar sakte hain, aur AI ise turant sikh lega!"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Kripya apna sawal likhein!"})
    
    ai_reply = custom_ai_engine(user_message)
    return jsonify({"response": ai_reply})

if __name__ == "__main__":
    app.run(debug=True)
