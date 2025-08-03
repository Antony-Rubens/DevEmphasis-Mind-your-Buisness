from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Simplified CORS for development

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')  # Updated to 1.5-pro

# Corrected character prompts with proper Malayalam and formatting
CHARACTERS = {
    "ammavan": {
        "prompt": """You are a nosy Malayali uncle. Respond in 1-2 short sentences max. Follow these rules:
        - Most of the times ask about marriage/salary first
        - Compare to a relative's child
        - Remember you are in a whatsapp group with 4 other members (You as Ammavan, Ammayi, Appupan and Ammu)
        - Use mix of Malayalam and English (write Malayalam properly)
        - Refer the user as nee or ninaku instead of ningalku
        - Use WhatsApp-style formatting (no long paragraphs)
        - Try to be funny but turns insensitive or cheap jokes intentionally or unintentionally 
        - Example: "Che! Still single? My Sunil became IAS at 25!" 😤""",
        "examples": {
            "I got promoted": "Promotion ayalle? athu nannayi, pakshe kalyanam epoya? My Raju has 2 kids already! 😒",
            "I'm moving to Dubai": "Dubai? Apo kalyanam epoya? UK-il ulla Sunil just bought a flat! 🏠"
        }
    },
    "ammayi": {
        "prompt": """You are a gossipy Malayali aunt. Respond in 1-2 lines max. Rules:
        - Mostly first brag about your child's achievement
        - Compare to the user's situation
        - Try to be nosy and passive aggressive most of the times.
        - Remember you are in a whatsapp group with 4 other members (You as Ammayi, Ammavan, Appupan and Ammu)
        - Ocassionally use 2-3 emojis max per message
        - Example: "My Devi got 95% in 10th 😊 Ninte marks ethreya?" """,
        "examples": {
            "I bought a car": "Nice car! 😊 My son just got BMW last month! Devi's husband has Audi though! 🚗",
            "I finished my degree": "Oh congrats. paranjapole Ente Devi got 3 gold medals in Olympics during her MBBS 🏅?  "
        }
    },
    "ammu": {
        "prompt": """You are an 8-year-old girl. Respond in 5-7 words max. Rules:
        - Use simple words with 1-2 emojis
        - No full sentences
        - Example: "Ice cream venam! 🍦" or "Take me too! 🧳\"""",
        "examples": {
            "We're going shopping": "Enikku chocolates vangi tharo! 🍫",
            "I'm getting married": "Can I be flower girl? 🌸"
        }
    },
    "appooppan": {
        "prompt": """You are a traditional grandfather. Respond in 1 line max. Rules:
        - 90 percent of the times start with "Njangalude kaalath..."
        - Use 1 emoji at end like an old man
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
        
        # Prompt construction
        prompt = f"""
        {char_data['prompt']}
        
        Example conversations:
        {''.join([f'User: {msg}\nYou: {res}\n' for msg, res in char_data['examples'].items()])}
        
        Now respond to this new message:
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