import streamlit as st
import json
import io # Needed for handling uploaded file bytes
import requests # Ensure requests library is imported for API calls

# Set Streamlit page configuration
st.set_page_config(
    page_title="AI Sales Trainer",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Global Variables for Firebase/App ID (Standard for Canvas Environment) ---
# These variables are automatically provided by the Canvas environment.
# DO NOT prompt the user for these or try to validate them.
# Corrected syntax to be valid Python for checking if global variables are defined.
appId = globals().get('__app_id', 'default-app-id')
firebaseConfig = json.loads(globals().get('__firebase_config', '{}'))
initialAuthToken = globals().get('__initial_auth_token', '')


# --- AI Coaching Logic ---
# Changed from 'async def' to 'def' because it now uses the synchronous 'requests' library
def get_ai_feedback(pitch_text):
    """
    Sends the sales pitch text to the Gemini API for analysis and feedback.
    """
    if not pitch_text.strip():
        return "Please enter your sales pitch to get feedback."

    prompt = f"""You are an AI sales coach specializing in helping small vendors improve their pitches.
Analyze the following sales pitch for:
1.  **Tone:** Is it confident, persuasive, empathetic, too aggressive, monotone, engaging?
2.  **Clarity:** Is the message clear, concise, easy to understand, free of jargon?
3.  **Structure:** Does it have a clear opening, problem identification, solution presentation, call to action, and logical flow?

Provide specific, actionable tips for improvement for each of these three areas.
Also, give an an overall assessment and highlight one strength and one area for immediate improvement.

Sales Pitch:
"{pitch_text}"

Provide your feedback in a structured, easy-to-read format."""

    chatHistory = []
    chatHistory.push({ "role": "user", "parts": [{ "text": prompt }] })

    payload = {
        "contents": chatHistory,
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "topK": 40
        }
    }

    # API key is automatically handled by the Canvas environment if empty string
    apiKey = "AIzaSyDFjPqo1X_QJGZ13Zxo7ojDVX0o2-W8jeA" # Leave this as an empty string. Canvas will inject the key at runtime.
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={apiKey}"

    try:
        response = requests.post(
            apiUrl,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.warning("Received an empty or unexpected response from the AI. Please try again.")
            return "No feedback generated. The AI might have found the pitch too short or unclear."

    except requests.exceptions.RequestException as e:
        st.error(f"An API request error occurred: {e}")
        return "An unexpected error occurred while processing your pitch."
    except Exception as e:
        st.error(f"An general error occurred: {e}")
        return "An unexpected error occurred while processing your pitch."


# --- Streamlit UI ---

st.title("🎙️ AI Sales Trainer for Small Vendors")
st.markdown("---")

st.write("""
Welcome to your personal AI Sales Coach!
You can either upload an audio recording of your pitch or type it below.
I'll provide instant feedback on your **tone**, **clarity**, and **structure**.
Let's make your pitches perfect!
""")

# Option for voice input (file upload)
st.subheader("Option 1: Upload Your Sales Pitch (Audio)")
uploaded_audio_file = st.file_uploader(
    "Upload an audio file (e.g., MP3, WAV)",
    type=["mp3", "wav"],
    help="Upload a recording of your sales pitch. Note: Actual Speech-to-Text conversion is simulated in this environment."
)

st.subheader("Option 2: Type or Paste Your Sales Pitch")
pitch_text_input = st.text_area(
    "Type or paste your sales pitch here:",
    height=250,
    placeholder="e.g., 'Hello! We offer a revolutionary new eco-friendly cleaning product that saves time and money. Our unique formula uses natural ingredients...'"
)

# Determine the input to use
final_pitch_for_analysis = ""
if uploaded_audio_file is not None:
    st.audio(uploaded_audio_file, format=uploaded_audio_file.type)
    
    st.info("Audio file uploaded. For a full voice-based coach, this audio would now be transcribed to text using a Speech-to-Text API.")
    # For now, if audio is uploaded, we will still rely on the text area for the pitch analysis unless it's empty
    if not pitch_text_input.strip():
        st.warning("Please type or paste your pitch in the text area below, as direct audio transcription is not fully integrated in this demo.")
        final_pitch_for_analysis = "" # Ensure no analysis happens without text
    else:
        final_pitch_for_analysis = pitch_text_input # Use text area if audio uploaded AND text provided
        st.info("Using the typed pitch for analysis as the audio transcription is conceptual.")

elif pitch_text_input.strip():
    final_pitch_for_analysis = pitch_text_input

# Button to get feedback
if st.button("Get Instant Feedback", use_container_width=True, type="primary"):
    if final_pitch_for_analysis.strip():
        with st.spinner("Analyzing your pitch..."):
            feedback = get_ai_feedback(final_pitch_for_analysis)
        st.markdown("---")
        st.subheader("Your AI Coach's Feedback:")
        st.markdown(feedback)
    else:
        st.warning("Please upload an audio file or enter your sales pitch to get feedback.")

st.markdown("---")
st.subheader("💡 How This Helps Small Vendors:")
st.markdown("""
* **Instant Improvement:** Get immediate, actionable tips without waiting for human coaching.
* **Cost-Effective:** A more affordable way to access sales training compared to traditional methods.
* **Focused Practice:** Pinpoint specific areas like tone, clarity, and structure for targeted improvement.
* **Confidence Boost:** Practice and refine pitches in a private, supportive environment.
""")

st.subheader("💰 Monetization Ideas:")
st.markdown("""
This tool can be monetized in several ways:
* **Freemium Model:** Offer a limited number of daily feedback sessions for free, then prompt for a subscription for unlimited access or deeper analysis.
* **Pay-per-Training Module:** Develop and sell specialized training modules (e.g., "Mastering Objection Handling," "Crafting Compelling CTAs") that integrate with the coaching.
* **Group Licensing:** Sell bulk subscriptions or custom versions to market associations, business incubators, or small business networks.
* **Premium Features:** Offer advanced metrics (e.g., predicted engagement score), historical pitch analysis, or personalized learning paths as premium features.
""")
