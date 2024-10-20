from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import io
import os
from dotenv import load_dotenv
from groq import Groq
from elevenlabs.client import ElevenLabs
import logging
import time
import magic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://your-frontend-domain.com"}})

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Change this!
jwt = JWTManager(app)

# Load environment variables
load_dotenv()

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

    temp_file = "assets/sound/level1/bullet.mp3"
    with open(temp_file, "wb") as f:
        for chunk in result:
            f.write(chunk)

    total_time = (time.time() - start_time) * 1000
    logger.info(f"Sound effect generated in {total_time:.2f} ms")

    return temp_file

# Add a function to check if the file is an MP3
def is_mp3(file):
    mime = magic.Magic(mime=True)
    return mime.from_buffer(file.read(1024)) == 'audio/mpeg'

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # Check the username and password
    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Create the access token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route('/process_audio', methods=['POST'])
@jwt_required()  # This decorator ensures that a valid JWT token is present in the request
def process_audio():
    logger.info("Received request to /process_audio")
    if 'audio' not in request.files:
        logger.warning("No audio file in request")
        return jsonify({'error': 'No audio file'}), 400

    audio_file = request.files['audio']
    logger.info(f"Received audio file: {audio_file.filename}")

    # Validate that the file is an MP3
    if not is_mp3(audio_file):
        logger.warning("Uploaded file is not an MP3")
        return jsonify({'error': 'File must be an MP3'}), 400

    # Reset file pointer after checking
    audio_file.seek(0)

    # Save the received audio file temporarily
    temp_input_file = "temp_input_audio.mp3"
    audio_file.save(temp_input_file)

    try:
        # Perform transcription using Groq
        with open(temp_input_file, "rb") as file:
            logger.info("Sending file to Groq for transcription")
            transcription = groq_client.audio.transcriptions.create(
                file=(temp_input_file, file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                language="en",
                temperature=0.0
            )
        logger.info(f"Transcription received: {transcription.text}")

        # Generate sound effect based on transcription
        sound_effect_file = generate_sound_effect(transcription.text)

        # Send both the generated sound effect and transcription back to the frontend
        return jsonify({
            'transcription': transcription.text,
            'audio_url': f'/get_audio/{os.path.basename(sound_effect_file)}'
        })

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500

    finally:
        # Clean up temporary files
        for file in [temp_input_file]:
            try:
                os.remove(file)
                logger.debug(f"Temporary file {file} removed")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file}: {str(e)}")

@app.route('/get_audio/<filename>', methods=['GET'])
@jwt_required()  # This decorator ensures that a valid JWT token is present in the request
def get_audio(filename):
    return send_file(f"assets/sound/level1/{filename}", mimetype='audio/mp3')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
