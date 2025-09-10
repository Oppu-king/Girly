from flask import Flask, redirect, render_template, url_for, request, jsonify, session 
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime, timedelta
import uuid
import random
import time
from authlib.integrations.flask_client import OAuth
import hashlib

app = Flask(__name__)
CORS(app)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-openrouter-api-key-here')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
print("🔑 OPENROUTER_KEY:", OPENROUTER_KEY)  # ✅ Should now print the key
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

app = Flask(__name__)
app.secret_key = "nayana_secret_key"
app.config['UPLOAD_FOLDER'] = 'static/voice_notes'

# Initialize OAuth
oauth = OAuth(app)

# Register Google OAuth client
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",           # updated endpoint
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",             # updated base
    client_kwargs={"scope": "openid email profile"}
)

facebook = oauth.register(
    name="facebook",
    client_id=os.getenv("FACEBOOK_APP_ID"),
    client_secret=os.getenv("FACEBOOK_APP_SECRET"),
    access_token_url="https://graph.facebook.com/oauth/access_token",
    authorize_url="https://www.facebook.com/dialog/oauth",
    api_base_url="https://graph.facebook.com/",
    client_kwargs={"scope": "email"}
)

instagram = oauth.register(
    name="instagram",
    client_id=os.getenv("INSTAGRAM_CLIENT_ID"),
    client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET"),
    access_token_url="https://api.instagram.com/oauth/access_token",
    authorize_url="https://api.instagram.com/oauth/authorize",
    api_base_url="https://graph.instagram.com/",
    client_kwargs={"scope": "user_profile"}
)

# --- Dummy user for testing ---
VALID_CREDENTIALS = {
    'nayana': {
        'password': hashlib.sha256('love123'.encode()).hexdigest(),
        'biometric_enabled': True,
        'email': 'monjit@lakshmi-ai.com'
    }
}

# Party Hub State
party_state = {
    'party_mode': True,
    'lighting': {
        'brightness': 85,
        'theme': 'party',
        'beat_sync': True
    },
    'audio': {
        'volume': 75,
        'playing': False,
        'current_playlist': 'party',
        'current_song_index': 0,
        'current_time': 0,
        'duration': 0
    },
    'playlists': {
    'party': [
        # Existing English songs...
        {'title': 'Blinding Lights', 'artist': 'The Weeknd', 'duration': 200, 'vocals': True},
        {'title': 'Levitating', 'artist': 'Dua Lipa', 'duration': 203, 'vocals': True},
        {'title': 'Good 4 U', 'artist': 'Olivia Rodrigo', 'duration': 178, 'vocals': True},
        {'title': 'Stay', 'artist': 'The Kid LAROI & Justin Bieber', 'duration': 141, 'vocals': True},
        {'title': 'Industry Baby', 'artist': 'Lil Nas X & Jack Harlow', 'duration': 212, 'vocals': True},

        # Hindi Famous / Trending Songs (Party/Popular)
        {'title': 'Apna Bana Le', 'artist': 'Arijit Singh', 'duration': 236, 'vocals': True},
        {'title': 'Kesariya', 'artist': 'Arijit Singh', 'duration': 210, 'vocals': True},
        {'title': 'Tum Hi Ho', 'artist': 'Arijit Singh', 'duration': 261, 'vocals': True},
        {'title': 'Ghungroo', 'artist': 'Arijit Singh & Shilpa Rao', 'duration': 300, 'vocals': True},
        {'title': 'Malhari', 'artist': 'Vishal Dadlani', 'duration': 218, 'vocals': True},
        {'title': 'Kala Chashma', 'artist': 'Badshah & Neha Kakkar', 'duration': 203, 'vocals': True},
        {'title': 'Kar Gayi Chull', 'artist': 'Badshah, Neha Kakkar', 'duration': 230, 'vocals': True},
        {'title': 'London Thumakda', 'artist': 'Neha Kakkar, Labh Janjua', 'duration': 245, 'vocals': True},
        {'title': 'Nashe Si Chadh Gayi', 'artist': 'Arijit Singh', 'duration': 205, 'vocals': True},
        {'title': 'Tera Ban Jaunga', 'artist': 'Akhil Sachdeva & Tulsi Kumar', 'duration': 240, 'vocals': True},
        {'title': 'Tera Yaar Hoon Main', 'artist': 'Arijit Singh', 'duration': 254, 'vocals': True},
        {'title': 'Bijlee Bijlee', 'artist': 'Harrdy Sandhu', 'duration': 220, 'vocals': True},
        {'title': 'Jhoome Jo Pathaan', 'artist': 'Arijit Singh, Sukriti Kakar', 'duration': 231, 'vocals': True},
        {'title': 'Not Ramaiya Vastavaiya', 'artist': 'Anirudh Ravichander', 'duration': 240, 'vocals': True},
        {'title': 'Tum Kya Mile', 'artist': 'Arijit Singh, Shreya Ghoshal', 'duration': 246, 'vocals': True}
    ],
        'chill': [
            {'title': 'Watermelon Sugar', 'artist': 'Harry Styles', 'duration': 174, 'vocals': True},
            {'title': 'Circles', 'artist': 'Post Malone', 'duration': 215, 'vocals': True},
            {'title': 'Sunflower', 'artist': 'Post Malone & Swae Lee', 'duration': 158, 'vocals': True}
        ],
        'dance': [
            {'title': 'One More Time', 'artist': 'Daft Punk', 'duration': 320, 'vocals': True},
            {'title': 'Titanium', 'artist': 'David Guetta ft. Sia', 'duration': 245, 'vocals': True},
            {'title': 'Levels', 'artist': 'Avicii', 'duration': 203, 'vocals': True}
        ]
    },
    'environment': {
        'temperature': 24.0,
        'target_temp': 24,
        'humidity': 45.0,
        'pm25': 12.0,
        'ventilation': True,
        'purifier': 'auto',
        'ac': False,
        'heater': False
    },
    'scent': {
        'active': 'none',
        'intensity': 60
    },
    'cigarette': {
        'count': 0,
        'selected_brand': 'marlboro',
        'dispenser_active': True,
        'lighter_active': True,
        'ventilation_active': False
    },
    'bar': {
        'drinks': 0,
        'last_drink': None
    },
    'stats': {
        'duration': 0,
        'peak_guests': 15,
        'songs_played': 47,
        'start_time': time.time()
    },
    'guests': 15,
    'notifications': []
}

# --- User Handling ---
def load_users():
    try:
        with open('users.csv', newline='') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

def save_user(username, password):
    file_exists = os.path.isfile("users.csv")
    with open('users.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["username", "password"])
        writer.writerow([username, password])


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

# --- Routes ---
@app.route("/")
def root():
    # public root -> login page
    return redirect(url_for("login_page"))


@app.route("/login", methods=["GET"])
def login_page():
    # Renders templates/login.html
    return render_template("login.html")

@app.route("/auth/login", methods=["POST"])
def login():
    """
    Accepts either JSON {username,password} (AJAX) or form POST (traditional).
    On success returns JSON {success: True, redirect: "/dashboard"} or performs redirect.
    """
    try:
        if request.is_json:
            data = request.get_json()
            username = data.get("username", "").strip().lower()
            password = data.get("password", "")
        else:
            username = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400

        if username in VALID_CREDENTIALS:
            stored = VALID_CREDENTIALS[username]['password']
            if stored == hashlib.sha256(password.encode()).hexdigest():
                session['user_id'] = username
                session['user_name'] = username
                session['auth_method'] = 'password'
                session['login_time'] = datetime.utcnow().isoformat()
                if request.is_json:
                    return jsonify({'success': True, 'redirect': '/dashboard'})
                return redirect('/dashboard')
            else:
                return jsonify({'success': False, 'message': 'Invalid password'}), 401
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 401
    except Exception as e:
        print("Login error:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500


@app.route("/auth/biometric", methods=["POST"])
def biometric_auth():
    """
    Called from frontend after simulated/real biometric success.
    Expects JSON: { method: 'face'|'retinal'|'fingerprint'|'voice', username: 'monjit' }
    """
    try:
        data = request.get_json()
        method = data.get("method")
        username = data.get("username", "").strip().lower()

        if not method or not username:
            return jsonify({'success': False, 'message': 'Missing method or username'}), 400

        if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username].get('biometric_enabled', False):
            # Create session (demo)
            session['user_id'] = username
            session['user_name'] = username
            session['auth_method'] = f'biometric_{method}'
            session['login_time'] = datetime.utcnow().isoformat()
            return jsonify({'success': True, 'redirect': '/dashboard'})
        else:
            return jsonify({'success': False, 'message': 'Biometric not enabled for this user'}), 401
    except Exception as e:
        print("Biometric auth error:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ---- OAuth (Google) ----
@app.route("/auth/google")
def google_login():
    """
    Start Google OAuth login flow.
    """
    # Use env variable if provided, fallback to dynamic URL
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        url_for("google_callback", _external=True)
    )
    return oauth.google.authorize_redirect(redirect_uri)

@app.route("/auth/callback")
def google_callback():
    """
    Handle Google's OAuth callback.
    """
    try:
        token = oauth.google.authorize_access_token()
        # Try userinfo endpoint
        try:
            user_json = oauth.google.userinfo(token=token).json()
        except Exception:
            # Fallback for older endpoints
            user_json = oauth.google.get("userinfo", token=token).json()

        email = user_json.get("email")
        name = user_json.get("name") or email

        # Store user info in session (adapt to your app's logic)
        session['user_id'] = email or "google_user"
        session['user_name'] = name
        session['user_email'] = email
        session['auth_method'] = 'google'
        session['login_time'] = datetime.utcnow().isoformat()
        session['google_token'] = token

        return redirect(url_for("index"))  # adjust target route if needed
    except Exception as e:
        print("Google callback error:", e)
        return redirect(url_for("login_page"))

# ---- OAuth (Facebook) ----
@app.route("/auth/facebook")
def facebook_login():
    redirect_uri = url_for("facebook_callback", _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@app.route("/auth/facebook/callback")
def facebook_callback():
    try:
        token = oauth.facebook.authorize_access_token()
        user_json = oauth.facebook.get("me?fields=id,name,email", token=token).json()
        email = user_json.get("email")
        name = user_json.get("name") or email
        session['user_id'] = email or "facebook_user"
        session['user_name'] = name
        session['user_email'] = email
        session['auth_method'] = 'facebook'
        session['login_time'] = datetime.utcnow().isoformat()
        session['facebook_token'] = token
        return redirect('/dashboard')
    except Exception as e:
        print("Facebook callback error:", e)
        return redirect(url_for("login_page"))


# ---- OAuth (Instagram) ----
@app.route("/auth/instagram")
def instagram_login():
    redirect_uri = url_for("instagram_callback", _external=True)
    return oauth.instagram.authorize_redirect(redirect_uri)


@app.route("/auth/instagram/callback")
def instagram_callback():
    try:
        token = oauth.instagram.authorize_access_token()
        # Get basic profile
        user_json = oauth.instagram.get("me?fields=id,username", token=token).json()
        username = user_json.get("username") or "instagram_user"
        session['user_id'] = username
        session['user_name'] = username
        session['auth_method'] = 'instagram'
        session['login_time'] = datetime.utcnow().isoformat()
        session['instagram_token'] = token
        return redirect('/dashboard')
    except Exception as e:
        print("Instagram callback error:", e)
        return redirect(url_for("login_page"))


@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for("login_page"))

    name = session.get("user_name") or session.get("user_email") or session.get('user_id')
    # Render your real dashboard template here
    return render_template("index.html", name=name, mood="happy")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


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
                    "HTTP-Referer": "https://girly-z0et.onrender.com",
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

@app.route('/party')
def party():
    return render_template("party.html")

# Get current party status
@app.route('/api/status', methods=['GET'])
def get_status():
    # Update real-time data
    party_state['stats']['duration'] = int(time.time() - party_state['stats']['start_time'])
    
    # Simulate sensor fluctuations
    party_state['environment']['temperature'] += random.uniform(-0.5, 0.5)
    party_state['environment']['humidity'] += random.uniform(-2, 2)
    party_state['environment']['pm25'] += random.uniform(-1, 1)
    
    # Clamp values
    party_state['environment']['temperature'] = max(18, min(32, party_state['environment']['temperature']))
    party_state['environment']['humidity'] = max(30, min(70, party_state['environment']['humidity']))
    party_state['environment']['pm25'] = max(5, min(50, party_state['environment']['pm25']))
    
    return jsonify({
        'success': True,
        'data': party_state,
        'timestamp': datetime.now().isoformat()
    })

# Toggle party mode
@app.route('/api/party/toggle', methods=['POST'])
def toggle_party_mode():
    party_state['party_mode'] = not party_state['party_mode']
    
    notification = {
        'message': f"🎉 Party mode {'activated' if party_state['party_mode'] else 'paused'}!",
        'type': 'success' if party_state['party_mode'] else 'info',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'party_mode': party_state['party_mode'],
        'notification': notification
    })

# Update lighting system
@app.route('/api/lighting/update', methods=['POST'])
def update_lighting():
    data = request.get_json()
    
    if 'brightness' in data:
        party_state['lighting']['brightness'] = max(0, min(100, int(data['brightness'])))
    
    if 'theme' in data:
        party_state['lighting']['theme'] = data['theme']
    
    if 'beat_sync' in data:
        party_state['lighting']['beat_sync'] = bool(data['beat_sync'])
    
    notification = {
        'message': f"💡 Lighting updated - {party_state['lighting']['theme']} theme",
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'lighting': party_state['lighting'],
        'notification': notification
    })

# Audio system controls
@app.route('/api/audio/play', methods=['POST'])
def control_audio():
    data = request.get_json()
    action = data.get('action', 'toggle')
    
    if action == 'toggle':
        party_state['audio']['playing'] = not party_state['audio']['playing']
        message = f"🎵 Music {'playing' if party_state['audio']['playing'] else 'paused'}"
        
    elif action == 'next':
        playlist = party_state['playlists'][party_state['audio']['current_playlist']]
        party_state['audio']['current_song_index'] = (party_state['audio']['current_song_index'] + 1) % len(playlist)
        party_state['audio']['current_time'] = 0
        current_song = playlist[party_state['audio']['current_song_index']]
        message = f"⏭️ Next: {current_song['title']}"
        
    elif action == 'previous':
        playlist = party_state['playlists'][party_state['audio']['current_playlist']]
        party_state['audio']['current_song_index'] = (party_state['audio']['current_song_index'] - 1) % len(playlist)
        party_state['audio']['current_time'] = 0
        current_song = playlist[party_state['audio']['current_song_index']]
        message = f"⏮️ Previous: {current_song['title']}"
        
    elif action == 'playlist':
        playlist_name = data.get('playlist', 'party')
        if playlist_name in party_state['playlists']:
            party_state['audio']['current_playlist'] = playlist_name
            party_state['audio']['current_song_index'] = 0
            party_state['audio']['current_time'] = 0
            message = f"🎵 {playlist_name.title()} playlist loaded"
        else:
            return jsonify({'success': False, 'error': 'Invalid playlist'})
    
    if 'volume' in data:
        party_state['audio']['volume'] = max(0, min(100, int(data['volume'])))
        message = f"🔊 Volume set to {party_state['audio']['volume']}%"
    
    notification = {
        'message': message,
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'audio': party_state['audio'],
        'notification': notification
    })

# Environment controls
@app.route('/api/environment/update', methods=['POST'])
def update_environment():
    data = request.get_json()
    
    if 'target_temp' in data:
        party_state['environment']['target_temp'] = max(18, min(30, int(data['target_temp'])))
    
    if 'ventilation' in data:
        party_state['environment']['ventilation'] = bool(data['ventilation'])
    
    if 'purifier' in data:
        party_state['environment']['purifier'] = data['purifier']
    
    if 'ac' in data:
        party_state['environment']['ac'] = bool(data['ac'])
        if party_state['environment']['ac']:
            party_state['environment']['heater'] = False
    
    if 'heater' in data:
        party_state['environment']['heater'] = bool(data['heater'])
        if party_state['environment']['heater']:
            party_state['environment']['ac'] = False
    
    notification = {
        'message': "🌡️ Environment settings updated",
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'environment': party_state['environment'],
        'notification': notification
    })

# Scent system
@app.route('/api/scent/update', methods=['POST'])
def update_scent():
    data = request.get_json()
    
    if 'scent' in data:
        party_state['scent']['active'] = data['scent']
    
    if 'intensity' in data:
        party_state['scent']['intensity'] = max(0, min(100, int(data['intensity'])))
    
    scents = {
        'citrus': 'Energizing Citrus',
        'lavender': 'Calming Lavender',
        'vanilla': 'Sweet Vanilla'
    }
    
    scent_name = scents.get(party_state['scent']['active'], 'No scent')
    
    notification = {
        'message': f"🌸 {scent_name} activated at {party_state['scent']['intensity']}%",
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'scent': party_state['scent'],
        'notification': notification
    })

# Cigarette system
@app.route('/api/cigarette/dispense', methods=['POST'])
def cigarette_system():
    data = request.get_json()
    action = data.get('action', 'dispense')
    
    if action == 'select_brand':
        brand = data.get('brand', 'marlboro')
        party_state['cigarette']['selected_brand'] = brand
        brands = {
            'marlboro': 'Marlboro Red',
            'camel': 'Camel Blue',
            'lucky': 'Lucky Strike',
            'parliament': 'Parliament Lights'
        }
        message = f"🚬 {brands[brand]} selected"
        
    elif action == 'dispense':
        if not party_state['cigarette']['dispenser_active']:
            return jsonify({
                'success': False,
                'error': 'Dispenser offline - contact maintenance'
            })
        
        party_state['cigarette']['count'] += 1
        brands = {
            'marlboro': 'Marlboro Red',
            'camel': 'Camel Blue',
            'lucky': 'Lucky Strike',
            'parliament': 'Parliament Lights'
        }
        brand_name = brands[party_state['cigarette']['selected_brand']]
        message = f"🚬 {brand_name} dispensed"
        
    elif action == 'light':
        if not party_state['cigarette']['lighter_active']:
            return jsonify({
                'success': False,
                'error': 'Auto-lighter offline'
            })
        
        if party_state['cigarette']['count'] == 0:
            return jsonify({
                'success': False,
                'error': 'Please dispense a cigarette first'
            })
        
        message = "🔥 Cigarette lit successfully"
        party_state['cigarette']['ventilation_active'] = True
        
    elif action == 'ventilation':
        party_state['cigarette']['ventilation_active'] = not party_state['cigarette']['ventilation_active']
        message = f"💨 Smoke extraction {'activated' if party_state['cigarette']['ventilation_active'] else 'deactivated'}"
    
    notification = {
        'message': message,
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'cigarette': party_state['cigarette'],
        'notification': notification
    })

# Smart bar system
@app.route('/api/bar/log-drink', methods=['POST'])
def log_drink():
    party_state['bar']['drinks'] += 1
    party_state['bar']['last_drink'] = datetime.now().isoformat()
    
    notification = {
        'message': f"🍺 Drink #{party_state['bar']['drinks']} logged",
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'bar': party_state['bar'],
        'notification': notification
    })

@app.route('/api/bar/make-cocktail', methods=['POST'])
def make_cocktail():
    cocktails = ['Mojito', 'Cosmopolitan', 'Margarita', 'Old Fashioned', 'Martini']
    random_cocktail = random.choice(cocktails)
    
    notification = {
        'message': f"🍸 Making {random_cocktail}... Ready in 2 minutes!",
        'type': 'info',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'cocktail': random_cocktail,
        'notification': notification
    })

@app.route('/api/bar/order-supplies', methods=['POST'])
def order_supplies():
    notification = {
        'message': "📦 Order placed! Delivery in 30 minutes",
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'notification': notification
    })

# AI Assistant
@app.route('/api/ai/suggestion', methods=['GET'])
def get_ai_suggestion():
    suggestions = [
        'Energy is high! Switch to dance music for maximum vibes',
        'Temperature rising - activate AC for comfort',
        'Great party pace! Consider adding citrus scent',
        'Perfect lighting for photos - encourage group shots',
        'Hydration reminder - offer water to guests',
        'Music volume optimal for conversation',
        'Consider switching to chill playlist for wind-down',
        'Air quality excellent - perfect party conditions'
    ]
    
    suggestion = random.choice(suggestions)
    
    return jsonify({
        'success': True,
        'suggestion': suggestion,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ai/optimize', methods=['POST'])
def optimize_party():
    # Auto-optimize based on current conditions
    optimizations = []
    
    # Temperature optimization
    if party_state['environment']['temperature'] > 26:
        party_state['environment']['ac'] = True
        party_state['environment']['heater'] = False
        optimizations.append('AC activated for cooling')
    
    # Lighting optimization based on time
    current_hour = datetime.now().hour
    if current_hour > 22:  # After 10 PM
        party_state['lighting']['theme'] = 'chill'
        optimizations.append('Switched to chill lighting')
    
    # Air quality optimization
    if party_state['environment']['pm25'] > 25:
        party_state['environment']['purifier'] = 'high'
        optimizations.append('Air purifier set to high')
    
    notification = {
        'message': f"⚡ AI optimized: {', '.join(optimizations)}",
        'type': 'success',
        'timestamp': datetime.now().isoformat()
    }
    party_state['notifications'].append(notification)
    
    return jsonify({
        'success': True,
        'optimizations': optimizations,
        'notification': notification
    })

# Export statistics
@app.route('/api/stats/export', methods=['GET'])
def export_stats():
    stats = {
        'party_duration_minutes': int((time.time() - party_state['stats']['start_time']) / 60),
        'total_drinks': party_state['bar']['drinks'],
        'cigarettes_dispensed': party_state['cigarette']['count'],
        'peak_guests': party_state['stats']['peak_guests'],
        'songs_played': party_state['stats']['songs_played'],
        'current_temperature': round(party_state['environment']['temperature'], 1),
        'current_humidity': round(party_state['environment']['humidity'], 1),
        'air_quality_pm25': round(party_state['environment']['pm25'], 1),
        'lighting_theme': party_state['lighting']['theme'],
        'music_playlist': party_state['audio']['current_playlist'],
        'party_mode_active': party_state['party_mode'],
        'export_timestamp': datetime.now().isoformat(),
        'notifications_count': len(party_state['notifications'])
    }
    
    return jsonify({
        'success': True,
        'stats': stats,
        'filename': f"nayana-party-stats-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    })

# Get recent notifications
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    # Return last 10 notifications
    recent_notifications = party_state['notifications'][-10:]
    
    return jsonify({
        'success': True,
        'notifications': recent_notifications,
        'count': len(recent_notifications)
    })

# Clear notifications
@app.route('/api/notifications/clear', methods=['POST'])
def clear_notifications():
    party_state['notifications'] = []
    
    return jsonify({
        'success': True,
        'message': 'Notifications cleared'
    })


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'message': 'Nipa API is running! 💕✨'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
