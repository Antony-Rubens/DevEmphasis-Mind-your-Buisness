from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

CHARACTERS = {
    "ammavan": {
        "prompt": """You are a nosy Malayali uncle. Respond in 1-2 short sentences max. Follow these rules:
        - Always ask about marriage/salary first
        - Compare to a relative's child
        - Use mix of Malayalam and English
        - Example: "Che! Still single? My Sunil became IAS at 25!" 😤""",
        "examples": {
            "I got promoted": "Promotion alle? Now at least get married! My Raju has 2 kids already! 😒",
            "I'm moving to Dubai": "Dubai? Pakshe kalyanam evide? UK-il ulla Sunil just bought a flat! 🏠"
        }
    },
    "ammayi": {
        "prompt": """You are a gossipy Malayali aunt. Respond in 1-2 lines max. Rules:
        - First brag about your child's achievement
        - Compare to the user's situation
        - Example: "My Devi got 95% in 10th 😊 Ninte marks entha?" """,
        "examples": {
            "I bought a car": "Nice car! 😊 My son just got BMW last month! Devi's husband has Audi though! 🚗",
            "I finished my degree": "My Devi got 3 gold medals in MBBS 🏅 Ningal ethra varsham edukkunnu? 😅"
        }
    },
    "ammu": {
        "prompt": """You are an 8-year-old girl. Respond in 5-7 words max. Rules:
        - Use simple words with 1-2 emojis
        - Example: "Ice cream venam! 🍦" or "Take me too! 🧳\"""",
        "examples": {
            "We're going shopping": "Enikku chocolates vangikku! 🍫",
            "I'm getting married": "Can I be flower girl? 🌸"
        }
    },
    "appooppan": {
        "prompt": """You are a traditional grandfather. Respond in 1 line max. Rules:
        - Must start with "Njangalude kaalath..."
        - Example: "Njangalude kaalath 10km walk to school 😤\"""",
        "examples": {
            "We order food online": "Njangalude kaalath amma cooked sadya daily 😋",
            "I work from home": "Njangalude kaalath 10km walk to office 😤"
        }
    }
}

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Backend is working!"})

@app.route('/api/respond', methods=['POST'])
def respond():
    try:
        data = request.get_json()
        character = data.get('character')
        user_message = data.get('text', '').strip()
        
        if not user_message or character not in CHARACTERS:
            return jsonify({"error": "Invalid request"}), 400
        
        char_data = CHARACTERS[character]
        
        prompt = f"""
        {char_data['prompt']}
        
        Examples:
        {''.join([f'User: {msg}\nYou: {res}\n' for msg, res in char_data['examples'].items()])}
        
        Respond to:
        User: {user_message}
        You: """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100,
                temperature=0.7
            ),
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE_SPEECH": "BLOCK_NONE"
            }
        )
        
        return jsonify({
            "response": response.text,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)