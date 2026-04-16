import google.generativeai as genai
from dotenv import load_dotenv
import os
from gtts import gTTS
import io

load_dotenv()

my_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=my_api_key)

# Prioritized list of models for fallback
AVAILABLE_MODELS = [
    "gemini-3.1-flash-lite-preview",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b"
]

def generate_study_materials(images, difficulty):
    prompt = f"""
    Analyze the uploaded images and provide study materials in two parts.
    
    PART 1: Summary Note
    Summarize the content of the images in a professional study note (max 150 words). 
    Use clear markdown headings and bullet points.
    
    PART 2: Interactive Quiz
    Generate 3 challenging quiz questions based on the {difficulty} difficulty level. 
    Include 4 options for each question and indicate the correct answer.
    
    Format the response exactly as follows:
    [SUMMARY]
    (Your notes here)
    [QUIZ]
    (Your quiz here)
    """
    
    errors = []
    for model_name in AVAILABLE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content([*images, prompt])
            return res.text, model_name
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                errors.append(f"Model {model_name} exhausted (Quota limit).")
            else:
                errors.append(f"Model {model_name} failed: {error_msg}")
            continue
            
    # If all models fail
    raise Exception("Critical: All AI models are currently unavailable due to quota limits or errors.\n" + "\n".join(errors))

def audio_trans(text):
     speech = gTTS(text, lang='en', slow=False)
     audio_buffer = io.BytesIO()
     speech.write_to_fp(audio_buffer)
     audio_buffer.seek(0)
     return audio_buffer
