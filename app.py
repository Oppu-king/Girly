from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime, timedelta
import uuid
import random

app = Flask(__name__)
CORS(app)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-openrouter-api-key-here')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_api(prompt, system_prompt="You are Nipa, a helpful AI assistant for girls. You're friendly, supportive, and knowledgeable about fashion, beauty, wellness, and lifestyle. IMPORTANT: Always use emojis instead of asterisks (*). Never use asterisks for emphasis - use emojis like 💕✨🌟💖 instead. Respond in a girly, encouraging tone with lots of emojis."):
    """Call OpenRouter API with DeepSeek model"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nipa-app.onrender.com",
            "X-Title": "Nipa - Girly Lifestyle Hub"
        }

        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"OpenRouter API Error: {response.status_code} - {response.text}")
            return "Sorry babe! I'm having a little technical moment right now. Please try again in a second! 💕✨"

    except Exception as e:
        print(f"API Error: {str(e)}")
        return "Sorry babe! I'm having a little technical moment right now. Please try again in a second! 💕✨"


# Helper Functions
# -------------------------------------------------------------------
def call_ai_api(message, context='general'):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompts = {
        'tutor': 'You are an expert AI Legal Tutor helping law students.',
        'case_brief': 'You are an AI legal assistant specializing in case brief generation.',
        'drafting': 'You are an AI legal drafting assistant.',
        'research': 'You are an AI legal research assistant.',
        'general': 'You are an expert AI legal assistant.'
    }

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompts.get(context, system_prompts['general'])},
            {"role": "user", "content": message}
        ],
        "max_tokens": 3000,
        "temperature": 0.7
    }

    response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"API request failed: {response.status_code} | {response.text}")

def extract_file_content(file_path, filename):
    try:
        if filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif filename.endswith('.pdf'):
            return f"PDF content from {filename} (parser needed)"
        elif filename.endswith(('.doc', '.docx')):
            return f"Word content from {filename} (parser needed)"
        else:
            return f"File content from {filename}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def log_interaction(message, response, context):
    pass

def save_generated_document(doc_type, content, details):
    return str(uuid.uuid4())

def save_case_brief(content, case_name):
    return str(uuid.uuid4())

def call_openrouter_api(prompt: str, api_key: str) -> str:
"""Call OpenRouter API with DeepSeek V3"""
try:
response = requests.post(
'https://openrouter.ai/api/v1/chat/completions',
headers={
'Authorization': f'Bearer {api_key}',
'Content-Type': 'application/json',
'HTTP-Referer': 'https://nexus-ai-trading.com',
'X-Title': 'NEXUS AI Trading Platform'
},
json={
'model': 'deepseek/deepseek-chat',
'messages': [
{
'role': 'system',
'content': 'You are a professional Indian market analyst specializing in NSE and BSE stocks. Provide specific insights for Indian markets.'
},
{
'role': 'user',
'content': prompt
}
],
'max_tokens': 3000,
'temperature': 0.1
}
)

if response.status_code == 200:  
        data = response.json()  
        return data['choices'][0]['message']['content']  
    else:  
        return f"API Error: {response.status_code} - {response.text}"  
          
except Exception as e:  
    return f"Error calling OpenRouter API: {str(e)}"


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

# AI Chat Routes
@app.route('/api/chat', methods=['POST'])
def chat():
    """General AI chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        system_prompt = data.get('system_prompt', "You are Nipa, a helpful AI assistant for girls. You're friendly, supportive, and knowledgeable about fashion, beauty, wellness, and lifestyle. IMPORTANT: Always use emojis instead of asterisks (*). Never use asterisks for emphasis - use emojis like 💕✨🌟💖 instead. Respond in a girly, encouraging tone with lots of emojis.")

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        response = call_openrouter_api(message, system_prompt)
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Fashion Routes
@app.route('/api/fashion/outfit', methods=['POST'])
def generate_outfit():
    """Generate outfit recommendations"""
    try:
        data = request.get_json()
        occasion = data.get('occasion', '')
        weather = data.get('weather', '')
        style = data.get('style', '')

        prompt = f"""Create a detailed outfit recommendation for:
        - Occasion: {occasion}
        - Weather: {weather}  
        - Style: {style}
        
        Include specific clothing items, colors, accessories, and styling tips. 
        Make it girly and fashionable with lots of emojis! 💕✨"""

        system_prompt = "You are Nipa's fashion stylist AI. Create detailed, trendy outfit recommendations with specific items, colors, and styling tips. Always use emojis instead of asterisks. Be encouraging and girly!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'outfit': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Beauty Routes
@app.route('/api/beauty/skincare', methods=['POST'])
def generate_skincare():
    """Generate skincare routine"""
    try:
        data = request.get_json()
        skin_type = data.get('skin_type', '')
        concerns = data.get('concerns', '')
        budget = data.get('budget', '')

        prompt = f"""Create a personalized skincare routine for:
        - Skin Type: {skin_type}
        - Main Concerns: {concerns}
        - Budget: {budget}
        
        Include morning and evening routines with specific product recommendations, 
        application order, and tips. Use emojis and be encouraging! 🧴✨"""

        system_prompt = "You are Nipa's skincare expert AI. Create detailed skincare routines with specific products and application tips. Always use emojis instead of asterisks. Be knowledgeable and supportive!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'routine': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Wellness Routes
@app.route('/api/wellness/cycle', methods=['POST'])
def calculate_cycle():
    """Calculate menstrual cycle predictions"""
    try:
        data = request.get_json()
        last_period = data.get('last_period', '')
        cycle_length = int(data.get('cycle_length', 28))

        # Parse the date
        last_period_date = datetime.strptime(last_period, '%Y-%m-%d')

        # Calculate predictions
        next_period = last_period_date + timedelta(days=cycle_length)
        ovulation = last_period_date + timedelta(days=cycle_length - 14)
        fertile_start = ovulation - timedelta(days=5)
        fertile_end = ovulation + timedelta(days=1)

        return jsonify({
            'next_period': next_period.isoformat(),
            'ovulation': ovulation.isoformat(),
            'fertile_start': fertile_start.isoformat(),
            'fertile_end': fertile_end.isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wellness/workout', methods=['POST'])
def generate_workout():
    """Generate workout plan"""
    try:
        data = request.get_json()
        goal = data.get('goal', '')
        time = data.get('time', '')

        prompt = f"""Create a personalized workout plan for:
        - Fitness Goal: {goal}
        - Available Time: {time} minutes per day
        
        Include specific exercises, sets, reps, and modifications for beginners.
        Make it encouraging and achievable with emojis! 💪✨"""

        system_prompt = "You are Nipa's fitness coach AI. Create safe, effective workout plans with clear instructions. Always use emojis instead of asterisks. Be motivating and supportive!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'workout': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lifestyle Routes
@app.route('/api/lifestyle/mood', methods=['POST'])
def mood_support():
    """Provide mood support and advice"""
    try:
        data = request.get_json()
        mood = data.get('mood', '')
        emoji = data.get('emoji', '')

        prompt = f"""The user is feeling {mood} {emoji}. Provide supportive advice, 
        self-care suggestions, and encouraging words. Include activities that might 
        help improve their mood and remind them of their worth. Use lots of emojis! 💕"""

        system_prompt = "You are Nipa's emotional support AI. Provide caring, supportive responses with practical self-care advice. Always use emojis instead of asterisks. Be empathetic and uplifting!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lifestyle/affirmation', methods=['GET'])
def generate_affirmation():
    """Generate daily affirmation"""
    try:
        prompt = """Generate a powerful, personalized daily affirmation for a girl. 
        Make it empowering, confidence-boosting, and beautiful. Include self-love, 
        strength, and positivity. Use emojis! ✨💖"""

        system_prompt = "You are Nipa's affirmation generator. Create beautiful, empowering affirmations that boost confidence and self-love. Always use emojis instead of asterisks. Be inspiring and uplifting!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'affirmation': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lifestyle/selfcare', methods=['POST'])
def generate_selfcare():
    """Generate self-care routine"""
    try:
        data = request.get_json()
        time = data.get('time', '')

        prompt = f"""Create a self-care routine for {time} minutes. Include activities 
        for relaxation, pampering, and mental wellness. Make it achievable and 
        luxurious feeling, even on a budget. Use emojis! 🛁💆‍♀️"""

        system_prompt = "You are Nipa's self-care expert. Create relaxing, achievable self-care routines that promote wellness and happiness. Always use emojis instead of asterisks. Be nurturing and caring!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'routine': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Shopping Routes
@app.route('/api/shopping/products', methods=['POST'])
def find_products():
    """Find product recommendations"""
    try:
        data = request.get_json()
        category = data.get('category', '')
        budget = data.get('budget', '')
        specific = data.get('specific', '')

        prompt = f"""Find the best {category} products within {budget} budget.
        {f'Specifically looking for: {specific}' if specific else ''}
        
        Include product names, price ranges, where to buy, and why they're great.
        Focus on quality and value. Use emojis! 🛍️💎"""

        system_prompt = "You are Nipa's shopping assistant. Recommend quality products with good value, including where to find them and why they're worth buying. Always use emojis instead of asterisks. Be helpful and budget-conscious!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'products': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Community Routes
@app.route('/api/community/question', methods=['POST'])
def answer_question():
    """Answer anonymous community questions"""
    try:
        data = request.get_json()
        question = data.get('question', '')

        prompt = f"""Answer this anonymous question with care and wisdom: "{question}"
        
        Provide supportive, non-judgmental advice. Be understanding and helpful.
        Include practical tips and emotional support. Use emojis! 💭💕"""

        system_prompt = "You are Nipa's community support AI. Answer questions with empathy, wisdom, and practical advice. Always use emojis instead of asterisks. Be supportive and non-judgmental!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/girl-talk', methods=['GET'])
def girl_talk_topic():
    """Generate girl talk discussion topic"""
    try:
        prompt = """Generate a fun, engaging discussion topic for girls to chat about.
        Make it relatable, interesting, and conversation-starting. Could be about 
        relationships, fashion, life experiences, dreams, or fun hypotheticals. 
        Use emojis! 💬✨"""

        system_prompt = "You are Nipa's conversation starter generator. Create engaging, fun topics that girls would love to discuss together. Always use emojis instead of asterisks. Be creative and relatable!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'topic': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/style-challenge', methods=['GET'])
def style_challenge():
    """Generate weekly style challenge"""
    try:
        prompt = """Create a fun weekly style challenge for girls. Make it creative,
        achievable, and Instagram-worthy. Include specific styling goals and tips
        for completing the challenge. Use emojis! 🏆👗"""

        system_prompt = "You are Nipa's style challenge creator. Design fun, creative fashion challenges that are achievable and inspiring. Always use emojis instead of asterisks. Be creative and encouraging!"

        response = call_openrouter_api(prompt, system_prompt)
        return jsonify({'challenge': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/legalmind")
def legalmind():
    return render_template("legalmind.html")


@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Handle AI chat requests"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', 'general')
        model = data.get('model', 'deepseek/deepseek-chat')

        if not message:  
            return jsonify({'error': 'Message is required'}), 400  

        # System prompts  
        system_prompts = {  
            'tutor': 'You are an expert AI Legal Tutor helping law students. Provide educational explanations with examples and case references where relevant. Focus on Indian law when applicable.',  
            'case_brief': 'You are an AI legal assistant specializing in case brief generation. Analyze judgments and create comprehensive case briefs with facts, issues, holdings, and legal reasoning.',  
            'drafting': 'You are an AI legal drafting assistant. Create professional legal documents with proper formatting, clauses, and legal language. Ensure compliance with standard legal practices.',  
            'research': 'You are an AI legal research assistant. Provide comprehensive legal research with relevant cases, statutes, legal principles, and citations.',  
            'moot_court': 'You are an AI moot court judge. Provide constructive feedback, ask probing questions, and present counter-arguments. Be professional but challenging.',  
            'general': 'You are an expert AI legal assistant helping law students and professionals. Provide accurate, helpful legal information and guidance.'  
        }  

        system_prompt = system_prompts.get(context, system_prompts['general'])  

        # Call OpenRouter API directly  
        headers = {  
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",  
            "Content-Type": "application/json"  
        }  

        payload = {  
            "model": model,  
            "messages": [  
                {"role": "system", "content": system_prompt},  
                {"role": "user", "content": message}  
            ],  
            "max_tokens": 1000,  
            "temperature": 0.7,  
            "top_p": 1  
        }  

        import requests  
        response = requests.post(  
            "https://openrouter.ai/api/v1/chat/completions",  
            headers=headers,  
            json=payload  
        )  

        if response.status_code != 200:  
            return jsonify({'error': f"OpenRouter API error: {response.text}"}), 500  

        result = response.json()  
        ai_message = result['choices'][0]['message']['content']  

        return jsonify({'reply': ai_message})  

    except Exception as e:  
        return jsonify({'error': str(e)}), 500
# -------------------------------------------------------------------
# File Upload
# -------------------------------------------------------------------
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"

        upload_folder = os.path.join(app.root_path, "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        content = extract_file_content(file_path, file.filename)

        return jsonify({
            "file_id": file_id,
            "filename": file.filename,
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "size": os.path.getsize(file_path),
            "upload_time": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------
# Generate Document
# -------------------------------------------------------------------
@app.route('/api/generate-document', methods=['POST'])
def generate_document():
    try:
        data = request.get_json()
        doc_type = data.get("document_type", "")
        details = data.get("details", "")

        if not doc_type or not details:
            return jsonify({"error": "Document type and details are required"}), 400

        prompt = f"""Generate a professional {doc_type} based on these requirements: "{details}".
Please create a complete, legally formatted document with:
1. Proper legal structure and formatting
2. All necessary clauses and provisions
3. Placeholder fields for customization (marked with [PLACEHOLDER])
4. Professional legal language
5. Compliance with standard legal practices"""

        ai_response = call_openrouter_api(prompt, "You are an AI legal drafting assistant.")
        doc_id = save_generated_document(doc_type, ai_response, details)

        return jsonify({
            "document_id": doc_id,
            "content": ai_response,
            "document_type": doc_type,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------
# Case Brief
# -------------------------------------------------------------------
@app.route('/api/case-brief', methods=['POST'])
def generate_case_brief():
    try:
        data = request.get_json()
        file_content = data.get("file_content", "")

        if not file_content:
            return jsonify({"error": "File content is required"}), 400

        prompt = f"""Analyze this legal judgment and create a comprehensive case brief. Content: "{file_content}"."""

        ai_response = call_openrouter_api(prompt, "You are an AI legal assistant specializing in case brief generation.")
        brief_id = save_case_brief(ai_response, file_content[:100])

        return jsonify({
            "brief_id": brief_id,
            "content": ai_response,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------
# Plagiarism
# -------------------------------------------------------------------
@app.route('/api/plagiarism-check', methods=['POST'])
def check_plagiarism():
    try:
        data = request.get_json()
        content = data.get("content", "")

        if not content:
            return jsonify({"error": "Content is required"}), 400

        prompt = f"""Analyze this document for plagiarism and originality. Content: "{content}"."""

        ai_response = call_openrouter_api(prompt, "You are an AI legal research assistant.")

        return jsonify({
            "report": ai_response,
            "analyzed_at": datetime.now().isoformat(),
            "word_count": len(content.split())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------
# User Stats
# -------------------------------------------------------------------
@app.route('/api/user-stats', methods=['GET', 'POST'])
def user_stats():
    if request.method == "GET":
        stats = session.get("user_stats", {
            "study_streak": 0,
            "cases_studied": 0,
            "ai_interactions": 0,
            "documents_created": 0,
            "overall_progress": 0
        })
        return jsonify(stats)

    if request.method == "POST":
        data = request.get_json()
        current_stats = session.get("user_stats", {})
        current_stats.update(data)
        session["user_stats"] = current_stats
        return jsonify(current_stats)


# -------------------------------------------------------------------
# Save Document
# -------------------------------------------------------------------
@app.route('/api/save-document', methods=['POST'])
def save_document():
    try:
        data = request.get_json()
        doc_name = data.get("name", "")
        doc_content = data.get("content", "")
        doc_type = data.get("type", "general")

        if not doc_name or not doc_content:
            return jsonify({"error": "Name and content are required"}), 400

        saved_docs = session.get("saved_documents", [])
        doc_id = str(uuid.uuid4())

        new_doc = {
            "id": doc_id,
            "name": doc_name,
            "content": doc_content,
            "type": doc_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        saved_docs.append(new_doc)
        session["saved_documents"] = saved_docs

        return jsonify({
            "document_id": doc_id,
            "message": "Document saved successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------
# Legal News
# -------------------------------------------------------------------
@app.route('/api/legal-news', methods=['GET'])
def get_legal_news():
    try:
        prompt = """Generate 3 current and realistic legal news items for today's date relevant to Indian law students."""

        ai_response = call_openrouter_api(prompt, "You are an expert AI legal assistant.")

        return jsonify({
            "news": ai_response,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/nayana-ai", methods=["GET", "POST"])
def nayana_ai():
    response = None
    if request.method == "POST":
        try:
            # Get data from form or JSON
            if request.is_json:
                data = request.get_json()
                question = data.get('question')
                mode = data.get('mode', 'general')
                system_prompt = data.get('systemPrompt', '')
            else:
                question = request.form.get("question")
                mode = request.form.get("mode", "general")
                system_prompt = request.form.get("systemPrompt", "")
            
            if not question:
                return jsonify({'error': 'No question provided'}), 400
            
            # Make request to OpenRouter using your working configuration
            ai_response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://lakshmi-ai-trades.onrender.com",
                    "X-Title": "Nayana AI"
                },
                json={
                    "model": "deepseek/deepseek-chat-v3-0324",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 600,
                    "temperature": 0.9,
                    "top_p": 0.95
                }
            )
            
            if ai_response.status_code != 200:
                print(f"OpenRouter API Error: {ai_response.status_code}")
                print(f"Response: {ai_response.text}")
                return jsonify({'error': f'AI service error: {ai_response.status_code}'}), 500
                
            ai_data = ai_response.json()
            response = ai_data['choices'][0]['message']['content']
            
            # Return JSON for AJAX requests
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'response': response})
            
            # Return HTML template for regular form submissions
            return render_template("nayana_ai.html", response=response)
            
        except Exception as e:
            print(f"AI Chat Error: {e}")
            error_msg = f"AI Processing Error: {str(e)}"
            
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': error_msg}), 500
            else:
                return render_template("nayana_ai.html", response=error_msg)
    
    # GET request - show the form
    return render_template("nayana_ai.html", response=response)

    # ✅ Handle GET requests
    return render_template("nayana_ai.html", response=None)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'message': 'Nipa API is running! 💕✨'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
