# TubeScope
📚YouTube Video to Note Cards🎓
This Streamlit app extracts the transcript from a YouTube video and generates concise and insightful note cards using Google Gemini Pro.

Requirements
Python 3.7 or higher
Virtual environment (recommended)
API key for Google Gemini Pro
Setup Instructions
1. Clone the Repository
Clone the repository to your local machine using the following command:

git clone https://github.com/your-username/your-repo.git
cd your-repo
2. Create and Activate a Virtual Environment (Recommended)
It's a good practice to use a virtual environment to manage dependencies.

# Navigate to the project directory
cd path/to/project/directory

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
3. Install the Required Packages
Install the necessary Python packages using the requirements file.

pip install -r requirements.txt
4. Set Up Environment Variables
Create a .env file in the root directory of the project and add your API key for Google Gemini Pro.

YOUR_API_KEY=your_google_gemini_pro_api_key
5. Run the Streamlit App
Start the Streamlit app with the following command:

streamlit run app.py
6. Add a Background Image (Optional)
If you want to change the background image, replace hi5.jpg in the project directory with your desired image, and update the image path in the add_bg_from_local function.

Usage Instructions
Enter YouTube Video Link: Paste the URL of the YouTube video you want to extract the transcript from into the text input box.
Generate Note Cards: Click on the "Generate Note Cards" button. The app will extract the transcript and generate note cards based on the video content.
View Note Cards: The generated note cards will be displayed below the button.
Code Overview
1. Import Necessary Libraries
import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
import random
import base64
2. Configure Streamlit and Load Environment Variables
st.set_page_config(page_title="YouTube Note Cards", page_icon="hi7.png", layout="wide")

load_dotenv()
api_key = os.getenv("YOUR_API_KEY")
if not api_key:
    st.error("API key not found. Please set up your environment variable correctly.")
    st.stop()

genai.configure(api_key=api_key)  # Use the actual API key
3. Define Helper Functions
Extract Video ID
def extract_video_id(youtube_url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        st.error("Invalid YouTube URL.")
        return None
Extract Transcript Details
def extract_transcript_details(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([segment['text'] for segment in transcript_list])
        return full_transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None
Generate Note Cards
def generate_note_cards_from_transcript(full_transcript):
    prompt = f"""You are an educational assistant helping to create concise and insightful 
    note cards from a YouTube video transcript. 

    Here is the full transcript:

    "{full_transcript}"

    Create small, easy-to-understand note cards that are useful for learning. Each note card should:
    * Highlight the most important concepts or facts.
    * Provide brief explanations for each concept or fact.
    * Be concise and written in simple language.

    Please generate several note cards based on the above transcript.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating note card content: {e}")
        return None
Format Note Cards
def format_note_cards(note_cards_content):
    note_cards = note_cards_content.split("Note Card ")
    formatted_note_cards = []
    colors = ['#FFCDD2', '#F8BBD0', '#E1BEE7', '#D1C4E9', '#C5CAE9', '#BBDEFB', '#B3E5FC', '#B2EBF2', '#B2DFDB', '#C8E6C9']
    for i, note_card in enumerate(note_cards[1:], start=1):  # Skip the first empty element
        note_card = note_card.strip()
        if note_card:
            color = random.choice(colors)
            formatted_note_cards.append(f"""
                <div class="note-card" style="background-color: {color};">
                    <h3>Note Card {i}</h3>
                    <ul>
                        {note_card.replace('. ', '.<br>')}
                    </ul>
                </div>
            """)
    return formatted_note_cards
Add Background Image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}

    .main {{  /* Added to target the main content area */
        background-color: rgba(255, 255, 255, 0.9);  /* Semi-transparent white background */
        padding: 20px;
        border-radius: 10px; /* Optional rounded corners */
        margin: 80px auto; /* Center the container horizontally */
        margin-bottom: 20px; /* Add some space at the bottom */
        max-width: 900px;  /* Set a maximum width */
        
    }}

    /* Additional styling for other elements (optional) */
    .stVideo {{ /* Style the video embed */
        margin-top: 2px;
        margin-bottom: 20px;
    }}

    </style>
    """,
        unsafe_allow_html=True
    )

# Add background image (replace 'hi5.jpg' with your actual image path)
add_bg_from_local('hi5.jpg')
4. Build the Streamlit App
Set Title and Custom CSS
st.title("📚YouTube Video to Note Cards🎓")

st.markdown("""
    <style>
    .note-card {
        border: 2px solid #000;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        font-size: 1.1em;
        line-height: 1.5em;
        color: #000;
    }
    .note-card h3 {
        margin-top: 0;
    }
    .note-card p {
        margin: 0;
    }
    .note-card ul {
        padding-left: 20px;
    }
    .note-card li {
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)
Set Background Image
st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://imgur.com/a/Cab4ZMk") center center;
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)
Input YouTube Link and Generate Note Cards
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.video(f"https://www.youtube.com/watch?v={video_id}")

        if st.button("Generate Note Cards"):
            with st.spinner("Extracting transcript..."):
                full_transcript = extract_transcript_details(video_id)

            if full_transcript:
                with st.spinner("Generating note cards..."):
                    note_cards_content = generate_note_cards_from_transcript(full_transcript)
                if note_cards_content:
                    formatted_note_cards = format_note_cards(note_cards_content)
                    st.markdown("## Note Cards:")
                    # Adjust the number of note cards based on video length
                    min_cards = 5
                    max_cards = 10
                    video_length = len(full_transcript.split())
                    num_cards = min(max(min_cards, int(video_length / 200)), max_cards)
                    for card in formatted_note_cards[:num_cards]:
                        st.markdown(card, unsafe_allow_html=True)
                else:
                    st.error("Failed to generate note cards.")
    else:
        st.error("Failed to extract video ID from the URL.")
Conclusion
By following these instructions, you should be able to set up and run the Streamlit app on your system. If you encounter any issues, please feel free to ask for further assistance. janhvi0802@gmail.com & jk422331@gmail.com Happy experimenting!

