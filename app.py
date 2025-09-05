from flask import Flask, request, jsonify,send_file
from flask_cors import CORS
import os
import base64
import requests
import json
from PIL import Image
except ImportError:
    import Image
import io
from datetime import datetime, timedelta
from flask import render_template
import random
import uuid
import logging


app = Flask(__name__)
CORS(app)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-openrouter-api-key-here')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Validate API key on startup
if not DEEPSEEK_API_KEY:
    logger.error("DEEPSEEK_API_KEY environment variable not set!")
    raise ValueError("DeepSeek API key is required")

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def save_uploaded_file(file, prefix="img"):
    """Save uploaded file and return the path"""
    if file and file.filename:
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{prefix}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Validate and resize if needed
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024 for API efficiency)
                max_size = 1024
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    img.save(file_path, 'JPEG', quality=90)
                
                logger.info(f"Saved and processed image: {file_path} ({img.width}x{img.height})")
                return file_path
                
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    return None

def call_deepseek_api(person_image_path, clothing_image_path, options):
    """Call DeepSeek V3 API for virtual try-on"""
    try:
        # Encode images to base64
        person_b64 = encode_image_to_base64(person_image_path)
        clothing_b64 = encode_image_to_base64(clothing_image_path)
        
        # Prepare the prompt based on options
        quality_prompts = {
            'standard': 'Generate a realistic virtual try-on result',
            'high': 'Generate a high-quality, detailed virtual try-on result with accurate fitting',
            'ultra': 'Generate an ultra-high-definition virtual try-on result with perfect detail and realistic lighting'
        }
        
        fit_prompts = {
            'auto': 'with natural, well-fitted appearance',
            'loose': 'with a loose, comfortable fit',
            'tight': 'with a tight, form-fitting appearance',
            'custom': 'with custom tailored fit'
        }
        
        style_prompts = {
            'none': '',
            'natural': 'Maintain natural lighting and colors',
            'enhanced': 'Enhance colors and contrast for a more vibrant look',
            'artistic': 'Apply artistic styling with enhanced visual appeal'
        }
        
        base_prompt = quality_prompts.get(options.get('quality', 'high'), quality_prompts['high'])
        fit_prompt = fit_prompts.get(options.get('fit', 'auto'), fit_prompts['auto'])
        style_prompt = style_prompts.get(options.get('style', 'natural'), style_prompts['natural'])
        
        full_prompt = f"""
        {base_prompt} {fit_prompt}. {style_prompt}
        
        Instructions:
        1. Take the person from the first image and the clothing item from the second image
        2. Realistically place the clothing on the person, ensuring proper fit and proportions
        3. Maintain the person's pose, lighting, and background
        4. Ensure the clothing looks natural and well-fitted
        5. Preserve image quality and realistic textures
        6. Make sure shadows and lighting are consistent
        
        Return only the final composite image showing the person wearing the clothing item.
        """
        
        # Prepare API request
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "deepseek-v3",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{person_b64}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{clothing_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.1
        }
        
        logger.info("Sending request to DeepSeek V3 API...")
        
        # Make API call
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("DeepSeek V3 API call successful")
            return result
        else:
            logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error calling DeepSeek API: {str(e)}")
        return None

def process_api_response(api_response, person_image_path, clothing_image_path):
    """Process the API response and generate result image"""
    try:
        # For this example, we'll create a composite result
        # In a real implementation, DeepSeek V3 would return the generated image
        
        # Load the original images
        person_img = Image.open(person_image_path)
        clothing_img = Image.open(clothing_image_path)
        
        # Create a result image (this is a placeholder - replace with actual API response processing)
        result_img = person_img.copy()
        
        # Add a subtle overlay to indicate processing (remove this in production)
        overlay = Image.new('RGBA', result_img.size, (124, 58, 237, 30))
        result_img = Image.alpha_composite(result_img.convert('RGBA'), overlay).convert('RGB')
        
        # Save result
        result_filename = f"result_{uuid.uuid4().hex}.jpg"
        result_path = os.path.join(RESULTS_FOLDER, result_filename)
        result_img.save(result_path, 'JPEG', quality=95)
        
        logger.info(f"Generated result image: {result_path}")
        return result_path
        
    except Exception as e:
        logger.error(f"Error processing API response: {str(e)}")
        return None


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

@app.route('/api/status', methods=['GET'])
def api_status():
    """Check API status and DeepSeek V3 availability"""
    try:
        # Test API connectivity
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Simple test request
        test_payload = {
            "model": "deepseek-v3",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                'status': 'connected',
                'model': 'deepseek-v3',
                'timestamp': datetime.now().isoformat(),
                'message': 'DeepSeek V3 API is ready'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'API Error: {response.status_code}'
            }), 500
            
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }), 500

@app.route('/api/try-on', methods=['POST'])
def virtual_try_on():
    """Main virtual try-on endpoint"""
    start_time = time.time()
    
    try:
        # Validate request
        if 'person' not in request.files or 'clothing' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Both person and clothing images are required'
            }), 400
        
        person_file = request.files['person']
        clothing_file = request.files['clothing']
        
        # Get processing options
        options = {
            'quality': request.form.get('quality', 'high'),
            'fit': request.form.get('fit', 'auto'),
            'style': request.form.get('style', 'natural')
        }
        
        logger.info(f"Processing try-on request with options: {options}")
        
        # Save uploaded files
        person_path = save_uploaded_file(person_file, 'person')
        clothing_path = save_uploaded_file(clothing_file, 'clothing')
        
        if not person_path or not clothing_path:
            return jsonify({
                'success': False,
                'error': 'Failed to process uploaded images'
            }), 400
        
        # Call DeepSeek V3 API
        api_response = call_deepseek_api(person_path, clothing_path, options)
        
        if not api_response:
            return jsonify({
                'success': False,
                'error': 'AI processing failed. Please try again.'
            }), 500
        
        # Process the response and generate result
        result_path = process_api_response(api_response, person_path, clothing_path)
        
        if not result_path:
            return jsonify({
                'success': False,
                'error': 'Failed to generate result image'
            }), 500
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        # Get result image info
        with Image.open(result_path) as img:
            resolution = f"{img.width}x{img.height}"
        
        # Generate result URL
        result_url = f"/api/result/{os.path.basename(result_path)}"
        
        # Clean up uploaded files (optional)
        try:
            os.remove(person_path)
            os.remove(clothing_path)
        except:
            pass
        
        logger.info(f"Try-on completed successfully in {processing_time}s")
        
        return jsonify({
            'success': True,
            'result_url': result_url,
            'processing_time': processing_time,
            'resolution': resolution,
            'options_used': options,
            'model': 'deepseek-v3',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Try-on processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500

@app.route('/api/result/<filename>')
def get_result(filename):
    """Serve result images"""
    try:
        result_path = os.path.join(RESULTS_FOLDER, filename)
        if os.path.exists(result_path):
            return send_file(result_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Result not found'}), 404
    except Exception as e:
        logger.error(f"Error serving result {filename}: {str(e)}")
        return jsonify({'error': 'Failed to serve result'}), 500



# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'message': 'Nipa API is running! 💕✨'})


if __name__ == '__main__':
    # Set maximum file size (10MB)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    
    print("🚀 VirtualFit Flask Server Starting...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📁 Results folder: {RESULTS_FOLDER}")
    print(f"🤖 DeepSeek V3 API: {'✅ Configured' if DEEPSEEK_API_KEY else '❌ Missing API Key'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)