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
