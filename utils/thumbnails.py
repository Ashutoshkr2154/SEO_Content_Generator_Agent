from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# ------------------------------------------------------------------
# SAFE VALUE FETCHER
# ------------------------------------------------------------------
def safe_get(obj, key, default=None):
    """Safely read value from dict or Pydantic model"""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

# ------------------------------------------------------------------
# 1️⃣ DALL·E IMAGE GENERATION
# ------------------------------------------------------------------
def generate_thumbnail_with_dalle(client, concept, video_title, platform="YouTube"):
    """
    Generates thumbnail using DALL·E (Only when OPENAI key present)
    Returns: Image URL or None
    """
    try:
        # Size per platform
        platform_sizes = {
            "YouTube": "1792x1024",
            "Instagram": "1024x1024",
            "LinkedIn": "1792x1024"
        }

        size = platform_sizes.get(platform, "1792x1024")

        text_overlay = safe_get(concept, "text_overlay", "")
        focal = safe_get(concept, "focal_point", "")
        tone = safe_get(concept, "tone", "")
        concept_desc = safe_get(concept, "concept", "")

        colors = safe_get(concept, "colors", ["#ffffff", "#000000"])
        main_color = colors[0] if colors else "#ffffff"

        prompt = f"""
Create a highly engaging professional {platform} thumbnail in {size}.
- Aspect ratio must strictly match platform requirements
- Sharp composition, cinematic depth, clear subject visibility
- Strong readable foreground text: "{text_overlay}"
- Focus Subject: {focal}
- Emotional Tone: {tone}
- Visual Concept: {concept_desc}
- Strong contrast colors, readable on mobile
- Inspired by high CTR YouTube thumbnails
- Avoid clutter and tiny text
- Include emotional punch and curiosity
Video Title Context: "{video_title}"
"""

        print("🎨 Generating DALL·E Thumbnail...")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )

        return response.data[0].url

    except Exception as e:
        print(f"❌ DALL·E Error: {e}")
        return None


# ------------------------------------------------------------------
# 2️⃣ FALLBACK — LOCAL PREVIEW GENERATOR
# ------------------------------------------------------------------
def create_thumbnail_preview(concept, video_title, base_image_url=None):
    """
    Local thumbnail preview when no DALL·E
    Returns PIL Image
    """
    try:
        if base_image_url:
            img = load_remote_image(base_image_url)
        else:
            img = create_gradient_background(concept)

        draw = ImageDraw.Draw(img)

        if safe_get(concept, "text_overlay"):
            add_text_with_outline(img, draw, concept)

        add_watermark(img, draw)

        return img

    except Exception as e:
        print(f"Local preview failed: {e}")
        # Absolute fallback
        return Image.new("RGB", (1280, 720), "#222222")


# ------------------------------------------------------------------
# 3️⃣ IMAGE HELPERS
# ------------------------------------------------------------------
def load_remote_image(url):
    try:
        r = requests.get(url, timeout=8)
        img = Image.open(BytesIO(r.content)).convert("RGB")
        return img.resize((1280, 720))
    except:
        return create_gradient_background({})


def create_gradient_background(concept, width=1280, height=720):
    colors = safe_get(concept, "colors", ["#3366CC", "#FFFFFF"])

    if len(colors) < 2:
        colors = ["#3366CC", "#FFFFFF"]

    c1 = hex_to_rgb_safe(colors[0])
    c2 = hex_to_rgb_safe(colors[1])

    img = Image.new("RGB", (width, height), c1)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    tone = safe_get(concept, "tone", "").lower()

    if "professional" in tone:
        add_professional_pattern(img, draw)
    elif "energetic" in tone:
        add_energetic_pattern(img, draw)
    elif "dramatic" in tone:
        add_dramatic_pattern(img, draw)

    return img


# ------------------------------------------------------------------
# 4️⃣ TEXT & STYLING
# ------------------------------------------------------------------
def add_text_with_outline(img, draw, concept):
    text = safe_get(concept, "text_overlay", "THUMBNAIL")
    colors = safe_get(concept, "colors", ["#FFFFFF", "#000000"])

    text_color = hex_to_rgb_safe(colors[0])
    outline_color = hex_to_rgb_safe(colors[1] if len(colors) > 1 else "#000000")

    font = load_font(80)

    # Size
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (img.width - w) // 2
    y = (img.height - h) // 2

    comp = safe_get(concept, "composition", "").lower()
    if "top" in comp:
        y = img.height // 4
    elif "bottom" in comp:
        y = img.height * 3 // 4
    elif "left" in comp:
        x = img.width // 4
    elif "right" in comp:
        x = img.width * 3 // 4 - w

    outline = 3
    for ox in range(-outline, outline + 1):
        for oy in range(-outline, outline + 1):
            draw.text((x + ox, y + oy), text, font=font, fill=outline_color)

    draw.text((x, y), text, font=font, fill=text_color)


def add_watermark(img, draw):
    text = "AI Generated Preview"
    font = load_font(20)
    draw.text((img.width - 240, img.height - 35), text, fill=(255, 255, 255), font=font)


# ------------------------------------------------------------------
# 5️⃣ FONT HANDLING
# ------------------------------------------------------------------
def load_font(size):
    possible = ["arial.ttf", "Arial.ttf", "Impact.ttf", "Verdana.ttf", "Tahoma.ttf"]

    for f in possible:
        try:
            return ImageFont.truetype(f, size)
        except:
            continue

    return ImageFont.load_default()


# ------------------------------------------------------------------
# 6️⃣ COLOR
# ------------------------------------------------------------------
def hex_to_rgb_safe(color):
    try:
        color = color.lstrip("#")
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    except:
        return (255, 255, 255)


# ------------------------------------------------------------------
# 7️⃣ STYLE PATTERNS
# ------------------------------------------------------------------
def add_professional_pattern(img, draw):
    w, h = img.size
    for i in range(0, w, 40):
        draw.line([(i, 0), (i, h)], fill=(255, 255, 255, 15))
    for i in range(0, h, 40):
        draw.line([(0, i), (w, i)], fill=(255, 255, 255, 15))


def add_energetic_pattern(img, draw):
    w, h = img.size
    for i in range(-h, w + h, 60):
        draw.line([(i, 0), (i + h, h)], fill=(255, 255, 255, 25), width=3)
        draw.line([(i, h), (i + h, 0)], fill=(255, 255, 255, 25), width=3)


def add_dramatic_pattern(img, draw):
    w, h = img.size
    cx, cy = w // 2, h // 2
    for r in range(50, max(w, h), 120):
        draw.arc([(cx - r, cy - r), (cx + r, cy + r)], 0, 360, fill=(255, 255, 255, 30), width=2)
