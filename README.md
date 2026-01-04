video-seo-optimizer/
├── .env
├── app.py
├── requirements.txt
├── README.md
│
├── utils/
│   ├── __init__.py
│   ├── video_extractor.py
│   ├── seo_agents.py
│   └── thumbnails.py
│
└── assets/
    └── logo.png

## Activate / Create Environment.

conda create -n lang6 python=3.11 -y

conda activate lang6

pip install -r requirements.txt

streamlit run app.py
