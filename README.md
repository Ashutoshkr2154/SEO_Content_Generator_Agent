# 📹 Video SEO Optimizer Pro

### AI Powered Multi-Agent SEO Optimization Engine for YouTube Creators

Video SEO Optimizer Pro is an **AI-powered Streamlit application** that analyzes YouTube videos and generates **complete SEO optimization recommendations** using **LLMs, LangChain, Ollama or OpenAI**.

It intelligently processes video metadata + transcripts and produces:

* ✅ Deep Content Analysis
* ✅ 35 High-Traffic SEO Tags
* ✅ 400+ Word SEO Optimized Description
* ✅ Engaging CTR-Focused Title Suggestions
* ✅ Structured Video Timestamps
* ✅ AI-Designed Thumbnail Concepts
* ✅ Multi-Language Output Support

Built for **content creators, SEO strategists, marketing teams, and AI enthusiasts** 🚀

---

## ⚙️ Tech Stack

| Component        | Technology                                 |
| ---------------- | ------------------------------------------ |
| Frontend         | Streamlit                                  |
| AI Engine        | LangChain                                  |
| Local AI         | Ollama (qwen2.5 / mistral / phi3 / llama3) |
| Cloud AI         | OpenAI (GPT-4o / GPT-4 Turbo / GPT-3.5)    |
| Transcripts      | youtube-transcript-api                     |
| Thumbnails       | DALL·E 3 (optional)                        |
| Language Support | Multi-Language                             |

---

## ✨ Features

### 🎯 Intelligent SEO Engine

The SEO Agent analyzes:

* Content theme
* Audience intent
* Emotional tone
* Engagement factors

Then generates:

* 🔥 35 Powerful SEO tags
* 📝 SEO-rich 400+ word description
* 🕒 Smart timestamps
* 🎬 CTR optimized video titles

---

### 🧠 AI Powered Thumbnail Concepts

Generates:

* Visual concept ideas
* Short punchline overlay
* Color palette (hex)
* Tone & focal direction

Optionally:

* Uses DALL-E to generate real images

---

### 🌐 Multi-Language Support

Generate SEO in:
English, Hindi, Spanish, French, German, Korean, Japanese, Chinese, Portuguese, Russian, Italian, Arabic

---

### 💻 Dual AI Backend Support

Run using:

* **OpenAI (Cloud)** – Best Accuracy
* **Ollama (Local)** – Completely Offline & Free

Recommended local models:

* `qwen2.5:3b`
* `mistral`
* `phi3`

---

## 🚀 Installation & Setup

### 1️⃣ Clone Repo

```
git clone https://github.com/Ashutoshkr2154/SEO_Content_Generator_Agent

cd video-seo-optimizer
```

---

### 2️⃣ Create Virtual Environment

## Activate / Create Environment.

conda create -n lang6 python=3.11 -y

conda activate lang6

pip install -r requirements.txt

streamlit run app.py


### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ (Optional) Enable OpenAI

Create `.env`

```
OPENAI_API_KEY=your_key_here
```

---

### 5️⃣ (Optional) Setup Ollama

Install Ollama → [https://ollama.ai](https://ollama.ai)

Pull model:

```
ollama pull qwen2.5:3b
```

or

```
ollama pull mistral
```

Run:

```
ollama serve
```

---

## ▶️ Run Application

```
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

---

## 🧠 How It Works (Architecture)

```
User Enters YouTube URL
        ↓
Metadata & Transcript Extractor
        ↓
SEO Multi-Agent Pipeline (LangChain)
        ↓
LLM Generates → JSON Structured Output
        ↓
Streamlit UI Displays SEO Suite
```

Modules:

* `video_extractor.py` → Fetches metadata + transcript
* `seo_agents.py` → Main AI engine
* `thumbnails.py` → AI Thumbnail generator
* `analysis_functions.py` → Backup analysis engine
* `app.py` → Streamlit interface

---

## 🐞 Error Handling

* Works even if transcript missing
* Safe fallback output
* JSON guaranteed
* Handles weak models
* Prevents UI crashes

---

## 🎯 Ideal Use Cases

✔️ YouTube Creators
✔️ SEO Agencies
✔️ Marketing Teams
✔️ AI Automation Builders
✔️ Students / Portfolio Projects

---

## 📌 Future Enhancements

* Support Instagram / LinkedIn / Shorts SEO
* Auto Thumbnail Image Generation
* Export SEO Pack as PDF
* Bulk Channel Optimization
* Creator Dashboard Analytics

---

## 👨‍💻 Author

**Ashutosh Kumar**
AI Engineer • Full-Stack Developer • ML Enthusiast

---

## ⭐ Contributions

Contributions are welcome!

* Fork repo
* Create PR
* Open Issues

---

If you want, I can also generate:

* `requirements.txt`
* `project folder structure documentation`
* `architecture diagram`
* `portfolio explanation script for interview`

