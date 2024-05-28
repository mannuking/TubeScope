import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
import plotly.graph_objects as go 
import matplotlib.pyplot as plt
from googleapiclient.discovery import build #for youtube data api 
import pandas as pd
import base64

# --- Page Configuration (Move to the very top) ---
st.set_page_config(page_title="TubeScope", page_icon="clapperboard.png", layout="wide")

# Load API key from .env
load_dotenv()
api_key = os.getenv("YOUR_API_KEY")
youtube_api_key= os.getenv("YOUR_YOUTUBE_API_KEY")

if not api_key or not youtube_api_key:
    st.error("API keys not found. Please set your environment variables correctly.")
    st.stop()

genai.configure(api_key=api_key)

# --- Functions ---

def extract_video_id(youtube_url):
    """Extracts video ID from YouTube URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        st.error("Invalid YouTube URL.")
        return None

def extract_transcript_details(video_id):
    """Extracts transcript from YouTube video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript_list
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

def extract_video_details(video_id):
    """Fetches video details using YouTube Data API v3, handling missing 'likeCount'."""
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()

    if response['items']:
        item = response['items'][0]
        statistics = item['statistics']
        return {
            "title": item['snippet']['title'],
            "viewCount": int(statistics['viewCount']),
            "likeCount": int(statistics.get('likeCount', 0)),  # Use get() with default
            "commentCount": int(statistics.get('commentCount', 0)),  # Use get() with default
        }
    else:
        st.error(f"Video not found with ID: {video_id}")
        return None

def generate_analysis_prompt(transcript, video_details, competitor_details=None):
    """Creates a prompt for video analysis, optionally comparing to a competitor."""
    prompt = f"""Analyze the following YouTube video transcript and details to assess its quality and potential for viewer engagement:

    **Video Title:** {video_details['title']}
    **View Count:** {video_details['viewCount']}
    
    **Transcript:**
    {transcript}
   
    Provide:
    * **Quality Assessment:** Rate the overall quality of the video (Poor, Fair, Good, Excellent) based on content, clarity, and production value.
    * **Engagement Factors:** Identify specific elements within the transcript or video details that contribute to viewer engagement (e.g., interesting topics, humor, visuals, etc.).
    * **Improvement Suggestions:** Offer 2-3 suggestions on how the video could be improved."""

    if competitor_details:
        prompt += f"""
        **Competitor Video Title:** {competitor_details['title']}
        **Competitor View Count:** {competitor_details['viewCount']}
    
        **Competitive Analysis:** Compare this video to the competitor video, highlighting strengths, weaknesses, and areas for improvement.
        """

    prompt += """
    * **Estimated Reach Potential:** Predict the potential reach of the video (Low, Moderate, High) based on its current metrics and content.
    """
    return prompt

def generate_analysis(prompt):
    """Generates video analysis using Google Gemini Pro."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating analysis: {e}")
        return None
    
def estimate_reach_potential(analysis_text, video_details):
    """Estimates reach potential based on keywords and video metrics."""

    view_count = video_details["viewCount"]

    # Keyword-based factors
    quality_keywords = {
        "poor": -2,
        "fair": -1,
        "good": 1,
        "excellent": 2,
    }
    engagement_keywords = {
        "low engagement": -2,
        "moderate engagement": 0,
        "high engagement": 2,
    }

    quality_score = sum(quality_keywords.get(word, 0) for word in analysis_text.lower().split())
    engagement_score = sum(engagement_keywords.get(word, 0) for word in analysis_text.lower().split())

    # View count-based factor (adjust weights as needed)
    view_count_score = 0
    if view_count < 1000:
        view_count_score = -2
    elif view_count < 10000:
        view_count_score = -1
    elif view_count < 100000:
        view_count_score = 1
    else:
        view_count_score = 2

    # Combine scores and determine reach potential
    total_score = quality_score + engagement_score + view_count_score

    if total_score >= 3:
        return "High"
    elif total_score >= 0:
        return "Moderate"
    else:
        return "Low"
        
def create_video_stats_table(video_details):
    """Creates a visually appealing table displaying video statistics."""
    df = pd.DataFrame({
        "Metric": ["Title", "View Count", "Like Count", "Comment Count"],
        "Value": [video_details[k] for k in ["title", "viewCount", "likeCount", "commentCount"]]
    })

    # Custom CSS to align the table
    st.markdown(
        """
        <style>
        table {
            width: 100%; /* Make the table take full width */
        }
        thead th {
            text-align: left;  /* Left-align table headers */
            background-color: #f0f0f5;
        }
        tbody th {
            text-align: left; /* Left-align metric names in the table body */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display the table
    st.table(df) 
    
def create_reach_graph(estimated_reach, competitor_reach=None):
    """Visualizes reach potential using Plotly, optionally with a competitor comparison."""

    categories = ["Low", "Moderate", "High"]
    scores = {"Low": 1, "Moderate": 2, "High": 3}

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=[scores[estimated_reach]],
        name="Your Video",
        marker_color="skyblue"
    ))

    if competitor_reach:
        fig.add_trace(go.Bar(
            x=categories,
            y=[scores[competitor_reach]],
            name="Competitor Video",
            marker_color="lightcoral"
        ))

    fig.update_layout(
        title="Video Reach Potential Assessment",
        xaxis_title="Estimated Reach Potential",
        yaxis_title="Relative Reach Score"
    )

    st.plotly_chart(fig)


# --- Streamlit App ---


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
        background-color: rgba(255, 255, 255, 0.8);  /* Semi-transparent white background */
        padding: 20px;
        border-radius: 10px; /* Optional rounded corners */
        margin: 20px auto; /* Center the container horizontally */
        max-width: 900px;  /* Set a maximum width */
    }}

    /* Additional styling for other elements (optional) */
    .stVideo {{ /* Style the video embed */
        margin-bottom: 20px;
    }}

    </style>
    """,
        unsafe_allow_html=True
    )


# Add background image (replace 'your_background_image.png' with your actual image path)
add_bg_from_local('gg.avif')





st.title("📽️ YouTube Video Analyzer ")

st.markdown(
    """
    Analyze your YouTube videos to gain insights into their quality, engagement potential, and estimated reach.
    """
)


youtube_link = st.text_input("Enter Your YouTube Video Link:")
competitor_link = st.text_input("Enter Competitor's YouTube Video Link (Optional):") 


if youtube_link:
    video_id = extract_video_id(youtube_link)

    if video_id:
        with st.spinner("Fetching video details..."):
            video_details = extract_video_details(video_id)

        if video_details:
            st.markdown("<div class='main'>", unsafe_allow_html=True)  # Start main container

            st.video(youtube_link)  
            create_video_stats_table(video_details)

            if st.button("Analyze Video"):
                with st.spinner("Analyzing video..."):
                    transcript_list = extract_transcript_details(video_id)
                    if transcript_list:
                        transcript = " ".join([t['text'] for t in transcript_list])

                        competitor_details = None
                        if competitor_link:
                            competitor_id = extract_video_id(competitor_link)
                            if competitor_id:
                                competitor_details = extract_video_details(competitor_id)
                            else:
                                st.warning("Invalid competitor video link. Skipping competitive analysis.")

                        prompt = generate_analysis_prompt(transcript, video_details, competitor_details)
                        analysis = generate_analysis(prompt)

                        st.markdown("## 📝 Video Analysis:")
                        st.write(analysis)

                        estimated_reach = estimate_reach_potential(analysis, video_details)
                        if competitor_details:
                            competitor_reach = estimate_reach_potential(analysis, competitor_details)  # Pass competitor_details
                            create_reach_graph(estimated_reach, competitor_reach)  # Show comparison graph
                        else:
                            create_reach_graph(estimated_reach)  # Show only your video's graph
                    else:
                        st.error("Error extracting transcript. Please try a different video.")

            st.markdown("</div>", unsafe_allow_html=True)  # End main container
