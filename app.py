import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import json
from io import BytesIO
from PIL import Image
import requests

# Import utility functions
from utils.video_extractor import get_video_metadata
from utils.seo_agents import run_seo_analysis_with_langchain
from utils.thumbnails import generate_thumbnail_with_dalle, create_thumbnail_preview

# Load environment variables
load_dotenv()

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Video SEO Optimizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; color: #1E88E5; margin-bottom: 1rem; }
    .section-title { font-size: 1.5rem; color: #0D47A1; margin-top: 1rem; }
    .tag-pill { background-color: #E3F2FD; color: #1565C0; padding: 5px 10px; border-radius: 15px; margin: 2px; display: inline-block; }
    .timestamp-card { background-color: #2196F3; padding: 10px; border-radius: 5px; margin-bottom: 5px; color: #FFFFFF; }
    .timestamp-card b { color: #FF5252; font-weight: bold; }
    .stButton>button { background-color: #1E88E5; color: white; }
    .platform-badge { font-weight: bold; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-bottom: 10px; }
    .youtube-badge { background-color: #FF0000; color: white; }
    .thumbnail-concept { border: 1px solid #DDDDDD; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    .color-swatch { height: 25px; width: 25px; display: inline-block; margin-right: 5px; border: 1px solid #CCCCCC; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=SEO+Agent", width=150)
    st.title("Configuration")

    # Provider selection
    st.subheader("AI Model Provider")
    provider_option = st.radio(
        "Select Backend:",
        ["OpenAI (Cloud)", "Ollama (Local)"],
        index=0
    )

    openai_api_key = None
    model_name = "gpt-4o"

    # ---------------- OpenAI Mode ----------------
    if provider_option == "OpenAI (Cloud)":
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key

        model_name = st.selectbox(
            "Select Model",
            ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        )

    # ---------------- Ollama Mode ----------------
    else:
        st.info("Ensure Ollama is running (`ollama serve`).")

        model_name = st.text_input(
            "Local Model Name",
            value="qwen2.5:3b",
            help="Recommended: qwen2.5:3b / phi3 / mistral (light + fast)"
        )

        dalle_key = st.text_input("OpenAI Key (For Images Only)", type="password")
        if dalle_key:
            os.environ["OPENAI_API_KEY"] = dalle_key

        # Check if Ollama is running & model exists
        try:
            res = requests.get("http://localhost:11434/api/tags").json()
            installed = [m["name"] for m in res.get("models", [])]

            if model_name not in installed:
                st.warning(
                    f"⚠️ Model `{model_name}` is not installed.\n\n"
                    f"Run: `ollama pull {model_name}`"
                )
        except:
            st.error("❌ Cannot connect to Ollama. Make sure it is running.")

    st.divider()

    # Language
    st.subheader("Language Settings")
    selected_language = st.selectbox(
        "Select Output Language",
        [
            "English", "Spanish", "French", "German", "Italian", "Portuguese",
            "Hindi", "Japanese", "Korean", "Chinese", "Russian", "Arabic"
        ],
        index=0
    )

    st.caption(f"Running on: {provider_option}")

# =====================================================
# MAIN
# =====================================================
st.markdown("<h1 class='main-title'>Video SEO Optimizer Pro</h1>", unsafe_allow_html=True)
st.write("Analyze videos from YouTube to generate SEO recommendations.")

video_url = st.text_input("Enter video URL", placeholder="https://www.youtube.com/watch?v=...")

# Session State
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'video_metadata' not in st.session_state:
    st.session_state.video_metadata = None

# =====================================================
# PROCESS URL
# =====================================================
if video_url:
    try:
        if st.session_state.video_metadata is None:
            with st.spinner("Fetching video information..."):
                metadata = get_video_metadata(video_url)
                st.session_state.video_metadata = metadata

        metadata = st.session_state.video_metadata

        col1, col2 = st.columns([2, 1])

        # ---------------- Video Info ----------------
        with col1:
            st.subheader("Video Details")

            platform = metadata.get("platform", "Unknown")
            badge_class = f"{platform.lower()}-badge"
            st.markdown(
                f"<div class='platform-badge {badge_class}'>{platform}</div>",
                unsafe_allow_html=True
            )

            st.write(f"**Title:** {metadata.get('title','N/A')}")
            if metadata.get("author"):
                st.write(f"**Creator:** {metadata.get('author')}")

            if metadata.get("duration"):
                minutes = metadata["duration"] // 60
                seconds = metadata["duration"] % 60
                st.write(f"**Duration:** {minutes}m {seconds}s")

            if metadata.get("views"):
                st.write(f"**Views:** {metadata['views']:,}")

        with col2:
            if metadata.get("thumbnail_url"):
                st.image(metadata["thumbnail_url"], caption="Current Thumbnail", width="content")

        st.divider()

        st.write(f"Ready to analyze using **{model_name}** ({provider_option}) in **{selected_language}**")

        # =====================================================
        # RUN SEO AGENT
        # =====================================================
        if st.button("Generate SEO Recommendations"):
            if provider_option == "OpenAI (Cloud)" and not os.getenv("OPENAI_API_KEY"):
                st.error("Please add OpenAI API Key.")
            else:
                with st.spinner("Analyzing video..."):
                    try:
                        results = run_seo_analysis_with_langchain(
                            video_url=video_url,
                            metadata=metadata,
                            language=selected_language,
                            provider=provider_option,
                            model_name=model_name
                        )
                        st.session_state.analysis_results = results
                        st.session_state.analysis_complete = True
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")

                        if provider_option == "Ollama (Local)":
                            st.info(f"""
**Troubleshooting**
• Run: `ollama serve`
• Install model: `ollama pull {model_name}`
• Prefer lightweight models: qwen2.5:3b, phi3, mistral
                            """)

    except Exception as e:
        st.error(f"Error processing video URL: {str(e)}")

# =====================================================
# RESULTS
# =====================================================
if st.session_state.analysis_complete and st.session_state.analysis_results:
    results = st.session_state.analysis_results

    st.success("Analysis complete! Here are your SEO recommendations:")

    tabs = st.tabs(["Content Analysis", "Tags", "Description", "Timestamps", "Titles", "Thumbnails"])

    # ---------------- Content ----------------
    with tabs[0]:
        st.markdown("<h2 class='section-title'>Content Analysis</h2>", unsafe_allow_html=True)
        st.write(results.get("analysis","No analysis generated."))

    # ---------------- Tags ----------------
    with tabs[1]:
        seo = results.get("seo",{})
        tags = seo.get("tags", [])
        st.markdown("<h2 class='section-title'>Recommended Tags</h2>", unsafe_allow_html=True)

        if tags:
            for t in tags:
                st.markdown(f"<div class='tag-pill'>#{t}</div>", unsafe_allow_html=True)
        else:
            st.warning("No tags generated")

    # ---------------- Description ----------------
    with tabs[2]:
        desc = results.get("seo",{}).get("description","")
        st.text_area("Optimized Description", desc, height=300)

    # ---------------- TimeStamps ----------------
    with tabs[3]:
        timestamps = results.get("seo",{}).get("timestamps",[])
        if timestamps:
            for ts in timestamps:
                st.markdown(
                    f"<div class='timestamp-card'><b>{ts['time']}</b> - {ts['description']}</div>",
                    unsafe_allow_html=True
                )
        else:
            st.warning("No timestamps generated")

    # ---------------- Titles ----------------
    with tabs[4]:
        titles = results.get("seo",{}).get("titles",[])
        for t in titles:
            st.write(f"### {t['title']}")
            if 'reason' in t:
                st.caption(t['reason'])

    # ---------------- Thumbnails ----------------
    with tabs[5]:
        thumbnails = results.get("thumbnails",{}).get("thumbnail_concepts",[])
        if not thumbnails:
            st.warning("No thumbnail concepts generated.")
        else:
            for i, concept in enumerate(thumbnails):
                st.write(f"### Concept {i+1}: {concept.get('text_overlay')}")
                st.write(concept.get("concept"))

st.divider()
st.caption("Video SEO Optimizer Pro • Powered by LangChain & Ollama")
