from flask import Flask, request, send_file, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import io
from io import BytesIO
import os
from dotenv import load_dotenv
from groq import Groq
from elevenlabs.client import ElevenLabs
import logging
import time
import filetype
import base64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://your-frontend-domain.com"}})

# Load environment variables
load_dotenv()

# Setup the Flask-JWT-Extended extension
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
if not jwt_secret_key:
    raise ValueError("JWT_SECRET_KEY is not set in the environment variables")

app.config['JWT_SECRET_KEY'] = jwt_secret_key
jwt = JWTManager(app)

# Get API keys from environment
groq_api_key = os.getenv("GROQ_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

if not groq_api_key or not elevenlabs_api_key:
    logger.error("Missing API keys in environment variables")
    raise ValueError("API keys are not set")

logger.info("API keys loaded successfully")

# Initialize clients
groq_client = Groq(api_key=groq_api_key)
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

logger.info("Clients initialized successfully")

def generate_sound_effect(text, duration_seconds=2.0, prompt_influence=0.3):
    logger.info(f"Generating sound effect for: '{text}'")
    start_time = time.time()

    result = elevenlabs_client.text_to_sound_effects.convert(
        text=text,
        duration_seconds=duration_seconds,
        prompt_influence=prompt_influence
    )

    audio_data = BytesIO()
    for chunk in result:
        audio_data.write(chunk)
    audio_data.seek(0)

    total_time = (time.time() - start_time) * 1000
    logger.info(f"Sound effect generated in {total_time:.2f} ms")

    return audio_data

# Add a function to check if the file is an MP3
def is_mp3(file_content):
    kind = filetype.guess(file_content)
    return kind is not None and kind.mime == 'audio/mpeg'

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # Check the username and password
    if username == 'gamejam2024' and password == 'happytesting':
        # Create the access token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@app.route('/process_audio', methods=['POST'])
@jwt_required()  # This decorator ensures that a valid JWT token is present in the request
def process_audio():
    logger.info("Received request to /process_audio")
    if 'audio' not in request.files:
        logger.warning("No audio file in request")
        return jsonify({'error': 'No audio file'}), 400

    audio_file = request.files['audio']
    logger.info(f"Received audio file: {audio_file.filename}")

    # Read the file content into memory
    audio_content = audio_file.read()

    # Validate that the file is an MP3
    if not is_mp3(audio_content):
        logger.warning("Uploaded file is not an MP3")
        return jsonify({'error': 'File must be an MP3'}), 400

    try:
        # Perform transcription using Groq
        logger.info("Sending file to Groq for transcription")
        transcription = groq_client.audio.transcriptions.create(
            file=("audio.mp3", audio_content),
            model="whisper-large-v3-turbo",
            response_format="json",
            language="en",
            temperature=0.0
        )
        logger.info(f"Transcription received: {transcription.text}")

        # Generate sound effect based on transcription
        sound_effect_data = generate_sound_effect(transcription.text)

        # Encode the audio data to base64
        encoded_audio = base64.b64encode(sound_effect_data.getvalue()).decode('utf-8')

        # Send both the generated sound effect and transcription back to the frontend
        return jsonify({
            'transcription': transcription.text,
            'audio_data': encoded_audio
        })

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
