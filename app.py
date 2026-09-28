import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# Initialize Google GenAI client (API key will be read from environment variables)
client = genai.Client()

DATA_FILE = "college_data.txt"

def load_college_data():
    """Reads college records from the simple text file"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def search_data(query):
    """Simple keyword matching to retrieve the most relevant lines from the text file"""
    lines = load_college_data()
    query_words = query.lower().split()
    relevant_lines = []
    
    for line in lines:
        match_count = sum(1 for word in query_words if word in line.lower())
        if match_count > 0:
            relevant_lines.append((match_count, line))
            
    # Sort by relevance and take top 3 matches
    relevant_lines.sort(key=lambda x: x[0], reverse=True)
    return "\n".join([item[1] for item in relevant_lines[:3]])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Please ask something!"})
    
    # 1. Retrieve matching context from text file
    context = search_data(user_message)
    
    # 2. Build system instructions and prompt for Gemini
    prompt = f"""
    You are MCR Assistant (Marwari College Assistant), an advanced AI assistant for Marwari College, Ranchi.
    You help students, teachers, professors, and the principal with syllabus links, room locations, directions, and campus facilities.
    You can speak and understand Hindi, English, and Hinglish naturally.
    
    Here is the relevant data retrieved from the college records file:
    {context if context else "No direct data found in local records for this specific query."}
    
    User's Query: {user_message}
    
    Instructions:
    - Answer accurately based on the retrieved data above.
    - If location details (Building, Floor, Latitude, Longitude) are present, explain them clearly so the user can navigate.
    - If a syllabus link is found, present it neatly.
    - If data is not available, politely mention that the record is not updated yet.
    - Match the user's language style (Hindi/English/Hinglish).
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ai_reply = response.text
    except Exception as e:
        ai_reply = f"Maaf kijiye, abhi system me kuch technical issue aa raha hai. Kripya thodi der baad try karein."
        
    return jsonify({"response": ai_reply})

if __name__ == "__main__":
    app.run(debug=True)
