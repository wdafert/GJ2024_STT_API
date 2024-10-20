# GJ2024 STT API

This project is a Flask-based API that processes audio files, transcribes them using Groq, and generates sound effects using ElevenLabs.

## Setup

1. Clone the repository:   ```
   git clone https://github.com/wdafert/GJ2024_STT_API.git
   cd GJ2024_STT_API   ```

2. Create a virtual environment and activate it:   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`   ```

3. Install the required packages:   ```
   pip install -r requirements.txt   ```

4. Set up your environment variables:
   Create a `.env` file in the root directory and add your API keys:   ```
   GROQ_API_KEY=your_groq_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   JWT_SECRET_KEY=your_jwt_secret_key   ```

5. Run the application:   ```
   python app.py   ```

## API Endpoints

### POST `/login`
Get a JWT token for authentication.

Request body:
json
{
"username": "test",
"password": "test"
}


Response:
json
{
"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}


### POST `/process_audio`
Process an audio file, transcribe it, and generate a sound effect.

Headers:
- `Authorization: Bearer <your_access_token>`

Request body:
- Form data with key `audio` containing the MP3 file

Response:

json
{
"transcription": "Transcribed text here",
"audio_data": "base64_encoded_audio_data"
}


## Usage Example

Here's a Python script demonstrating how to use the API:

python
import requests
import base64
Login and get token
login_response = requests.post('http://localhost:5000/login', json={
'username': 'test',
'password': 'test'
})
token = login_response.json()['access_token']
Process audio
with open('your_audio_file.mp3', 'rb') as audio_file:
files = {'audio': audio_file}
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:5000/process_audio', files=files, headers=headers)
result = response.json()
print("Transcription:", result['transcription'])
Save the generated audio
audio_data = base64.b64decode(result['audio_data'])
with open('generated_sound_effect.mp3', 'wb') as f:
f.write(audio_data)

## Heroku Deployment

This application is configured for easy deployment to Heroku. Follow these steps to deploy:

1. Create a Heroku account if you don't have one.
2. Install the Heroku CLI and log in.
3. In your project directory, run:   ```
   heroku create your-app-name   ```
4. Set up your environment variables on Heroku:   ```
   heroku config:set GROQ_API_KEY=your_groq_api_key
   heroku config:set ELEVENLABS_API_KEY=your_elevenlabs_api_key
   heroku config:set JWT_SECRET_KEY=your_jwt_secret_key   ```
5. Push your code to Heroku:   ```
   git push heroku main   ```
6. Open your app:   ```
   heroku open   ```

### Automatic Deployments

To set up automatic deployments from GitHub:

1. Go to your Heroku dashboard and select your app.
2. Go to the "Deploy" tab.
3. In the "Deployment method" section, choose "GitHub".
4. Connect your GitHub repository to your Heroku app.
5. In the "Automatic deploys" section, choose the branch you want to deploy and click "Enable Automatic Deploys".

Now, every time you push to the selected branch on GitHub, Heroku will automatically deploy your updated application.
