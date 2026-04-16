import streamlit as st 
from api_call import generate_study_materials, audio_trans
from PIL import Image
import re   

# Page Config
st.set_page_config(page_title="AI Smart Notes", page_icon="📝", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }

    /* Glassmorphism sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Card-like containers */
    .stSecondaryBlock {
        background: rgba(255, 255, 255, 0.05);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }

    /* Stylish buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }

    /* Headers */
    h1, h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    .title-text {
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    /* Status messages */
    .stAlert {
        border-radius: 1rem !important;
        border: none !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# App Content
st.markdown('<div class="title-text">AI Smart Notes</div>', unsafe_allow_html=True)
st.markdown("##### Transform your captures into structured knowledge using Gemini 3.1 Flash")
st.divider()

# Sidebar for Inputs
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/learning.png", width=80)
    st.header("Workspace")
    
    uploaded_files = st.file_uploader("Capture or upload images (max 3)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
    
    if len(uploaded_files) > 3:
        st.warning("⚠️ Limit: 3 images")
        uploaded_files = uploaded_files[:3]

    st.divider()
    difficulty = st.selectbox("Complexity Level", ["Easy", "Medium", "Hard"], index=1)
    
    generate_btn = st.button("Generate Mastery Pack", type="primary")

# Main Logic
if generate_btn:
    if not uploaded_files:
        st.error('Please upload at least one image to begin.')
    else:
        pil_images = [Image.open(file) for file in uploaded_files]
        
        # Grid for uploaded images preview
        cols = st.columns(min(len(pil_images), 3))
        for i, img in enumerate(pil_images):
            with cols[i]:
                st.image(img, use_column_width=True)

        try:
            with st.spinner("🧠 Analyzing content and crafting materials..."):
                response_text, used_model = generate_study_materials(pil_images, difficulty)
                
                # Parsing logic
                # Looking for [SUMMARY] ... [QUIZ]
                summary_match = re.search(r'\[SUMMARY\](.*?)\[QUIZ\]', response_text, re.DOTALL | re.IGNORECASE)
                quiz_match = re.search(r'\[QUIZ\](.*)', response_text, re.DOTALL | re.IGNORECASE)
                
                if summary_match and quiz_match:
                    summary_text = summary_match.group(1).strip()
                    quiz_text = quiz_match.group(1).strip()
                else:
                    # Fallback if parsing fails
                    summary_text = response_text
                    quiz_text = "Analysis complete, but quiz formatting was unavailable. Please try again."

                # Results Display in Tabs
                tab1, tab2, tab3 = st.tabs(["📚 Study Notes", "🎧 Audio Guide", "📝 mastery Quiz"])
                
                with tab1:
                    st.markdown("### 📖 Summary Notes")
                    st.markdown(summary_text)
                    
                with tab2:
                    st.markdown("### 🔊 Listen to your Notes")
                    try:
                        clean_notes = re.sub(r'[*#$-]', '', summary_text)
                        audio_file = audio_trans(clean_notes)
                        st.audio(audio_file, format='audio/mp3')
                        st.info("Tip: You can download this audio for offline study.")
                    except Exception as e:
                        st.error(f"Audio generation failed: {str(e)}")

                with tab3:
                    st.markdown(f"### 🎯 Knowledge Check ({difficulty})")
                    st.markdown(quiz_text)

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                st.error("⚠️ API quota exceeded. Please wait a moment or try again later.")
            else:
                st.error(f"System Error: {str(e)}")

st.markdown("---")
if 'used_model' in locals():
    st.caption(f"Active Model: **{used_model}** • Powered by Google Gemini • Made with ❤️ for Students")
else:
    st.caption("Powered by Google Gemini • Made with ❤️ for Students")