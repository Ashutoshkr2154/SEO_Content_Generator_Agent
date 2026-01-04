import json
from typing import List
from pydantic import BaseModel, Field

# LangChain
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


# ==========================================================
# 1️⃣ STRICT DATA STRUCTURES
# ==========================================================
class Timestamp(BaseModel):
    time: str = Field(description="MM:SS format timestamp")
    description: str


class Title(BaseModel):
    rank: int
    title: str
    reason: str


class ThumbnailConcept(BaseModel):
    concept: str
    text_overlay: str
    colors: List[str]
    focal_point: str
    tone: str


class SeoData(BaseModel):
    tags: List[str]
    description: str
    timestamps: List[Timestamp]
    titles: List[Title]


class FinalOutput(BaseModel):
    analysis: str
    seo: SeoData
    thumbnails: dict


# ==========================================================
# 2️⃣ MAIN ENGINE
# ==========================================================
def run_seo_analysis_with_langchain(
    video_url,
    metadata,
    language="English",
    provider="OpenAI",
    model_name="gpt-4o"
):
    """
    Runs full SEO pipeline using OpenAI or Ollama.
    Returns clean JSON in required structure.
    """

    # ---------------- MODEL SELECTION ----------------
    try:
        if provider == "Ollama (Local)":
            print(f"🔌 Using Ollama Model: {model_name}")
            llm = ChatOllama(
                model=model_name,
                temperature=0.7,
                format="json"
            )
        else:
            print(f"☁️ Using OpenAI Model: {model_name}")
            llm = ChatOpenAI(
                model=model_name,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
    except Exception as e:
        print(f"❌ Model Init Failed: {e}")
        return generate_fallback_data(metadata, language)

    # ---------------- PARSER ----------------
    parser = JsonOutputParser(pydantic_object=FinalOutput)

    # ---------------- CONTEXT HANDLING ----------------
    transcript = metadata.get("transcript_text", "")
    max_len = 15000 if provider == "Ollama (Local)" else 30000

    if len(transcript) > max_len:
        transcript = transcript[:max_len] + " ... (truncated)"

    video_info = f"""
Title: {metadata.get('title')}
Author: {metadata.get('author')}
Platform: {metadata.get('platform')}
Duration: {metadata.get('duration')} seconds

Transcript Preview:
{transcript}
"""

    # ---------------- PROMPT ----------------
    prompt_text = """
You are a world-class YouTube SEO Strategist + Growth Expert.

LANGUAGE: {language}

Analyze the video and produce the BEST SEO optimization blueprint.

VIDEO DATA:
{video_info}

OUTPUT REQUIREMENTS:

1️⃣ ANALYSIS
Deep insight on:
- audience intent
- tone
- value proposition
- why viewers watch
- engagement potential

2️⃣ TAGS
- EXACTLY 35 SEO tags
- No hashtags
- No duplicates
- Short & powerful
- High search intent

3️⃣ DESCRIPTION
- 350 to 500 words
- Hook in first line
- Keyword rich
- Engaging tone
- CTA included

4️⃣ TIMESTAMPS
- Helpful
- Clear
- Useful structure

5️⃣ TITLES
- 5 high CTR titles
- Ranked by performance
- Include brief reason

6️⃣ THUMBNAILS
Provide 3 thumbnail concepts with:
- concept
- text_overlay
- 3 color hex codes
- focal_point
- tone

Return ONLY VALID JSON. No Markdown. No explanations.
{format_instructions}
"""

    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["video_info", "language"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    # ---------------- RUN ----------------
    try:
        print("🚀 Running SEO Engine...")
        response = chain.invoke({
            "video_info": video_info,
            "language": language
        })

        # ---------------- FIX MODEL ISSUES ----------------

        # normalize thumbnails
        thumbs = response.thumbnails
        if isinstance(thumbs, list):
            response.thumbnails = {"thumbnail_concepts": thumbs}

        # ensure 35 tags
        tags = response.seo.tags
        if len(tags) < 35:
            needed = 35 - len(tags)
            tags += [f"extra_tag_{i}" for i in range(needed)]
        elif len(tags) > 35:
            response.seo.tags = tags[:35]

        return response.dict()

    except Exception as e:
        print(f"❌ SEO Chain Failed: {e}")
        return generate_fallback_data(metadata, language)


# ==========================================================
# 3️⃣ SAFE MODE FALLBACK
# ==========================================================
def generate_fallback_data(metadata, language):
    title = metadata.get("title", "Untitled Video")

    return {
        "analysis": f"SEO Analysis is temporarily unavailable for {title}.",
        "seo": {
            "tags": [
                "youtube", "seo", "video", "growth", "algorithm",
                "viral", "content", "creator", "engagement", "strategy"
            ] * 4,
            "description": f"""
This is a YouTube video titled '{title}'.
Full AI SEO optimization could not be generated right now.
""",
            "timestamps": [
                {"time": "00:00", "description": "Video Starts"},
                {"time": "00:30", "description": "Main Content"}
            ],
            "titles": [
                {"rank": 1, "title": title, "reason": "Fallback original"}
            ]
        },
        "thumbnails": {
            "thumbnail_concepts": [
                {
                    "concept": "Bold modern thumbnail with strong central text",
                    "text_overlay": "WATCH THIS",
                    "colors": ["#FF0000", "#FFFFFF", "#000000"],
                    "focal_point": "Center Subject",
                    "tone": "Strong & Engaging"
                }
            ]
        }
    }
