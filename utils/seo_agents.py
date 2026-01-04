import json
from typing import List
from pydantic import BaseModel, Field

# Modern LangChain Imports
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


# ===============================================================
# STRICT DATA STRUCTURE (Pydantic)
# ===============================================================
class Timestamp(BaseModel):
    time: str = Field(description="Timestamp in MM:SS format")
    description: str = Field(description="Short description")

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
    composition: str

class SeoData(BaseModel):
    tags: List[str]
    description: str
    timestamps: List[Timestamp]
    titles: List[Title]

class FinalOutput(BaseModel):
    analysis: str
    seo: SeoData
    thumbnails: dict


# ===============================================================
# MAIN SEO ENGINE
# ===============================================================
def run_seo_analysis_with_langchain(
    video_url,
    metadata,
    language="English",
    provider="OpenAI",
    model_name="gpt-4o"
):
    # ---------------- LLM Selection ----------------
    try:
        if provider == "Ollama (Local)":
            print(f"🔌 Using Ollama model: {model_name}")
            llm = ChatOllama(
                model=model_name,
                temperature=0.7,
                format="json"
            )
        else:
            print(f"☁️ Using OpenAI model: {model_name}")
            llm = ChatOpenAI(
                model=model_name,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
    except Exception as e:
        print(f"❌ Model init failed: {e}")
        return generate_fallback_data(metadata, language)

    # ---------------- JSON Parser ----------------
    parser = JsonOutputParser(pydantic_object=FinalOutput)

    # ---------------- Context Handling ----------------
    transcript = metadata.get("transcript_text", "")
    max_len = 15000 if provider == "Ollama (Local)" else 30000
    if len(transcript) > max_len:
        transcript = transcript[:max_len] + " ... (truncated)"

    video_info = f"""
Title: {metadata.get('title')}
Author: {metadata.get('author')}
Platform: {metadata.get('platform', 'YouTube')}
Duration: {metadata.get('duration')} seconds

Transcript Snippet:
{transcript}
"""

    # ---------------- Prompt ----------------
    prompt_text = """
You are an Elite YouTube SEO Strategist + Growth Expert.

LANGUAGE: {language}

Analyze the provided video and produce the BEST SEO optimization plan.

VIDEO DATA:
{video_info}

REQUIREMENTS:

1️⃣ Deep content analysis.

2️⃣ EXACTLY 35 SEO Tags.
- No duplicates
- No hashtags
- High traffic search intent

3️⃣ YouTube Description
- 350–500 words
- Hook
- SEO rich
- CTA

4️⃣ Timestamps
- Helpful navigation

5️⃣ Titles
- 5 Ranked CTR titles

6️⃣ Thumbnails
- 3 structured thumbnail design ideas

Return ONLY VALID JSON.
No markdown.
{format_instructions}
"""

    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["video_info", "language"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    # ===============================================================
    # EXECUTE + HARDEN RESPONSE
    # ===============================================================
    try:
        print("🚀 Invoking SEO Agent...")
        response = chain.invoke({
            "video_info": video_info,
            "language": language
        })

        # ---------------------------------------
        # ALWAYS convert to dict
        # ---------------------------------------
        if hasattr(response, "dict"):
            response = response.dict()

        # ---------------------------------------
        # THUMBNAILS SAFE NORMALIZATION
        # ---------------------------------------
        if "thumbnails" not in response or response["thumbnails"] is None:
            response["thumbnails"] = {}

        if isinstance(response["thumbnails"], list):
            response["thumbnails"] = {"thumbnail_concepts": response["thumbnails"]}

        if "thumbnail_concepts" not in response["thumbnails"]:
            response["thumbnails"]["thumbnail_concepts"] = []

        # ---------------------------------------
        # TAGS: ensure exactly 35
        # ---------------------------------------
        try:
            tags = response.get("seo", {}).get("tags", [])
        except:
            tags = []

        if len(tags) < 35:
            diff = 35 - len(tags)
            tags += [f"extra_tag_{i}" for i in range(diff)]
        elif len(tags) > 35:
            tags = tags[:35]

        if "seo" not in response:
            response["seo"] = {}

        response["seo"]["tags"] = tags

        return response

    except Exception as e:
        print(f"❌ Chain Execution Failed: {e}")
        return generate_fallback_data(metadata, language)


# ===============================================================
# FALLBACK SAFE MODE
# ===============================================================
def generate_fallback_data(metadata, language):
    title = metadata.get("title", "Untitled Video")

    return {
        "analysis": f"SEO Analysis temporarily unavailable for {title}.",
        "seo": {
            "tags": [
                "youtube", "video", "content", "viral", "trending",
                "growth", "algorithm", "seo", "engagement", "audience"
            ] * 4,
            "description": f"""
This is a YouTube video titled {title}.
Full AI SEO optimization failed temporarily.
""",
            "timestamps": [
                {"time": "00:00", "description": "Introduction"},
                {"time": "00:30", "description": "Key Content Begins"}
            ],
            "titles": [
                {"rank": 1, "title": title, "reason": "Fallback title"}
            ]
        },
        "thumbnails": {
            "thumbnail_concepts": [
                {
                    "concept": "Bold contrast thumbnail",
                    "text_overlay": "WATCH THIS",
                    "colors": ["#FF0000", "#FFFFFF", "#000000"],
                    "focal_point": "Center",
                    "tone": "Bold",
                    "composition": "Centered"
                }
            ]
        }
    }
