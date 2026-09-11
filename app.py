import os
import json
import re
import io
import time
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import requests
import imageio.v2 as imageio

from xai_sdk import Client
from xai_sdk.chat import user

load_dotenv()

# ============================================================
# PROFESSIONAL CHILDREN'S LEARNING STUDIO
# Grok / xAI API + Streamlit
#
# IMPORTANT:
# xAI's API is not currently a free API service. API usage is
# billed according to xAI's current pricing. The software stack
# itself is free/open-source to install.
# ============================================================

st.set_page_config(
    page_title="Grok Kids Learning Studio",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEXT_MODEL = "grok-4.6"
IMAGE_MODEL = "grok-imagine-image-2.0"


def get_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def get_client() -> Client:
    api_key = get_secret("XAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "XAI_API_KEY is missing. Add it to Streamlit Cloud → "
            "Settings → Secrets, or create a local .env file."
        )
    return Client(api_key=api_key)


def extract_json(text: str) -> Any:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.I)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
        if not starts:
            raise
        start = min(starts)
        end = max(text.rfind("}"), text.rfind("]"))
        if end <= start:
            raise
        return json.loads(text[start:end + 1])


def generate_lesson(topic: str, age: str, language: str,
                    level: str, length: str) -> dict:
    client = get_client()

    prompt = f"""
Create a professional but warm educational lesson for a child.

Topic: {topic}
Child age: {age}
Language: {language}
Learning level: {level}
Lesson length: {length}

Return ONLY valid JSON. No Markdown fences.

Schema:
{{
  "title": "short engaging title",
  "welcome": "friendly introduction",
  "learning_goals": ["goal 1", "goal 2", "goal 3"],
  "explanation": "clear explanation suitable for the child's age and level",
  "examples": [
    {{
      "title": "example title",
      "explanation": "step-by-step child-friendly example",
      "visual_prompt": "detailed prompt for an educational illustration"
    }},
    {{
      "title": "example title",
      "explanation": "step-by-step child-friendly example",
      "visual_prompt": "detailed prompt for an educational illustration"
    }},
    {{
      "title": "example title",
      "explanation": "step-by-step child-friendly example",
      "visual_prompt": "detailed prompt for an educational illustration"
    }}
  ],
  "animation": {{
    "narration": "short narration that connects all scenes",
    "scenes": [
      {{
        "title": "scene title",
        "description": "what the child should see and learn",
        "visual_prompt": "high-quality educational image prompt"
      }},
      {{
        "title": "scene title",
        "description": "what the child should see and learn",
        "visual_prompt": "high-quality educational image prompt"
      }},
      {{
        "title": "scene title",
        "description": "what the child should see and learn",
        "visual_prompt": "high-quality educational image prompt"
      }},
      {{
        "title": "scene title",
        "description": "what the child should see and learn",
        "visual_prompt": "high-quality educational image prompt"
      }}
    ]
  }},
  "remember": ["short point", "short point", "short point"],
  "quiz": [
    {{
      "question": "question",
      "options": ["A", "B", "C", "D"],
      "answer": "exact option text",
      "explanation": "short explanation of the correct answer"
    }}
  ]
}}

Rules:
- Exactly 5 quiz questions.
- Exactly 4 options per quiz question.
- Answer must exactly equal one option.
- Use simple, encouraging language.
- Match the selected age, language, level and length.
- Teach using concrete everyday examples.
- Never request personal information.
- Avoid unsafe experiments or activities.
- Keep the lesson factually accurate.
- The visual prompts should be colorful, educational, child-friendly,
  non-scary, and suitable for high-resolution image generation.
"""

    chat = client.chat.create(model=TEXT_MODEL)
    chat.append(user(prompt))

    # A short retry for transient API errors.
    last_error = None
    for attempt in range(3):
        try:
            response = chat.sample()
            content = getattr(response, "content", None)
            if content:
                data = extract_json(content)
                if isinstance(data, dict):
                    return data
            raise RuntimeError("Grok returned an empty or invalid lesson.")
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))
            else:
                raise RuntimeError(f"Grok lesson generation failed: {exc}") from exc

    raise RuntimeError(str(last_error))


def generate_image(prompt: str, resolution: str = "2k") -> Image.Image:
    client = get_client()

    enhanced_prompt = f"""
Create a high-resolution educational illustration for children.

{prompt}

Style:
- professional educational illustration
- bright, friendly, clean composition
- clear visual storytelling
- age-appropriate
- no scary content
- no violence
- no unsafe activity
- simple enough for a child to understand
- accurate visual representation of the topic
- no unnecessary text inside the image
"""

    response = client.image.sample(
        prompt=enhanced_prompt,
        model=IMAGE_MODEL,
        resolution=resolution,
        aspect_ratio="16:9",
        quality="medium",
    )

    # xAI returns a temporary hosted image URL by default.
    url = getattr(response, "url", None)
    if not url:
        image_bytes = getattr(response, "image", None)
        if image_bytes:
            return Image.open(io.BytesIO(image_bytes)).convert("RGB")
        raise RuntimeError("Grok image generation returned no image URL.")

    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def make_fallback_slide(topic: str, title: str, description: str) -> Image.Image:
    """Used only when the image API is unavailable."""
    img = Image.new("RGB", (1280, 720), "white")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((40, 40, 1240, 680), outline="black", width=5)
    draw.text((80, 80), topic, fill="black")
    draw.text((80, 160), title, fill="black")
    draw.text((80, 250), description[:250], fill="black")
    draw.ellipse((850, 220, 1050, 420), outline="black", width=6)
    draw.line((950, 420, 950, 560), fill="black", width=6)
    return img


def make_animation(images: list[Image.Image], duration=900) -> bytes:
    frames = [img.convert("RGB") for img in images]
    buffer = io.BytesIO()
    # imageio's Pillow writer creates an animated GIF without requiring
    # a system-level FFmpeg installation.
    imageio.mimsave(
        buffer,
        frames,
        format="GIF",
        duration=duration / 1000.0,
        loop=0,
    )
    return buffer.getvalue()


def safe_list(value, default=None):
    return value if isinstance(value, list) else (default or [])


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <style>
    .hero {
        padding: 28px 30px;
        border-radius: 20px;
        border: 1px solid rgba(120,120,120,.25);
        margin-bottom: 20px;
    }
    .small-card {
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(120,120,120,.2);
        min-height: 110px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🌟 Grok Kids Learning Studio</h1>
        <p>
        Enter a topic and the studio builds an age-appropriate lesson with
        explanations, real-world examples, high-resolution illustrations,
        an animated visual lesson and a short quiz.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# ONLY THE USER INPUTS REQUESTED
# ============================================================
with st.sidebar:
    st.header("🎓 Learning settings")

    age = st.selectbox(
        "👧 Child's age",
        ["4–6", "7–9", "10–12", "13–15", "16–17"],
        index=1,
    )

    language = st.selectbox(
        "🌍 Language",
        [
            "English",
            "Urdu",
            "Arabic",
            "Spanish",
            "French",
            "German",
            "Chinese",
            "Turkish",
            "Hindi",
            "Portuguese",
        ],
        index=0,
    )

    level = st.selectbox(
        "📈 Learning level",
        ["Simple", "Medium", "Advanced"],
        index=0,
    )

    length = st.selectbox(
        "⏱️ Lesson length",
        ["Short", "Medium", "Long"],
        index=0,
    )

    st.divider()
    st.caption("Powered by xAI Grok")
    st.caption(f"Text model: {TEXT_MODEL}")
    st.caption(f"Image model: {IMAGE_MODEL}")

topic = st.text_input(
    "📚 What would you like to teach?",
    placeholder="Example: Solar System, Fractions, Plants, Gravity, Water Cycle",
)

create = st.button(
    "✨ Create Complete Lesson",
    type="primary",
    use_container_width=True,
)

if create:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    with st.spinner("Grok is designing the lesson..."):
        try:
            lesson = generate_lesson(
                topic=topic.strip(),
                age=age,
                language=language,
                level=level,
                length=length,
            )
            st.session_state.lesson = lesson
            st.session_state.topic = topic.strip()
            st.session_state.age = age
            st.session_state.language = language
            st.session_state.level = level
            st.session_state.length = length
            st.session_state.images = {}
            st.session_state.animation_images = []
            st.session_state.quiz_score = None
        except Exception as exc:
            st.error(f"Could not create the lesson: {exc}")
            st.info(
                "Check XAI_API_KEY and your xAI API account/credits. "
                "The xAI API is a paid API; Grok itself has a free consumer product, "
                "but API usage is billed separately."
            )
            st.stop()

if "lesson" not in st.session_state:
    st.info("👆 Enter a topic and click **Create Complete Lesson**.")
    st.stop()

lesson = st.session_state.lesson
topic = st.session_state.topic

# ============================================================
# LESSON
# ============================================================
st.divider()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Age", st.session_state.age)
with c2:
    st.metric("Language", st.session_state.language)
with c3:
    st.metric("Level", st.session_state.level)
with c4:
    st.metric("Length", st.session_state.length)

st.header(f"📖 {lesson.get('title', topic)}")
st.write(lesson.get("welcome", ""))

goals = safe_list(lesson.get("learning_goals"))
if goals:
    st.subheader("🎯 Learning goals")
    for goal in goals:
        st.write(f"• {goal}")

st.subheader("🧠 Let's understand it")
st.write(lesson.get("explanation", ""))

# ============================================================
# EXAMPLES
# ============================================================
st.subheader("🔎 Learn through examples")

examples = safe_list(lesson.get("examples"))

for i, example in enumerate(examples[:3]):
    with st.expander(
        f'Example {i + 1}: {example.get("title", "Let\'s try an example")}',
        expanded=(i == 0),
    ):
        st.write(example.get("explanation", ""))

        prompt = example.get("visual_prompt", "")
        if prompt:
            key = f"example_{i}"
            if key not in st.session_state.images:
                if st.button(
                    f"🖼️ Generate high-resolution example {i + 1}",
                    key=f"gen_ex_{i}",
                ):
                    with st.spinner("Grok Imagine is creating a 2K illustration..."):
                        try:
                            st.session_state.images[key] = generate_image(prompt, "2k")
                        except Exception as exc:
                            st.error(f"Image generation failed: {exc}")

            if key in st.session_state.images:
                st.image(
                    st.session_state.images[key],
                    caption=f"High-resolution example {i + 1}",
                    use_container_width=True,
                )

# ============================================================
# ANIMATION
# ============================================================
st.subheader("🎬 Learn through animation")

animation = lesson.get("animation", {})
scenes = safe_list(animation.get("scenes"))

st.write(animation.get("narration", ""))

if scenes:
    if st.button(
        "🎬 Generate animated lesson",
        type="secondary",
        use_container_width=True,
    ):
        images = []
        progress = st.progress(0)

        for i, scene in enumerate(scenes[:4]):
            prompt = scene.get("visual_prompt", "")
            try:
                with st.spinner(f"Creating scene {i + 1} of {min(4, len(scenes))}..."):
                    image = generate_image(prompt, "2k")
            except Exception:
                image = make_fallback_slide(
                    topic,
                    scene.get("title", f"Scene {i + 1}"),
                    scene.get("description", ""),
                )

            images.append(image)
            progress.progress((i + 1) / min(4, len(scenes)))

        st.session_state.animation_images = images

    if st.session_state.get("animation_images"):
        animation_bytes = make_animation(
            st.session_state.animation_images,
            duration=1100,
        )

        st.image(
            animation_bytes,
            caption="Animated lesson — each scene teaches one idea.",
        )

        st.download_button(
            "⬇️ Download animated lesson",
            data=animation_bytes,
            file_name="grok_kids_lesson.gif",
            mime="image/gif",
            use_container_width=True,
        )

        for i, scene in enumerate(scenes[:4]):
            st.markdown(
                f"**Scene {i + 1} — {scene.get('title', '')}**  \n"
                f"{scene.get('description', '')}"
            )

# ============================================================
# REMEMBER
# ============================================================
remember = safe_list(lesson.get("remember"))
if remember:
    st.subheader("⭐ Remember these")
    cols = st.columns(min(3, len(remember)))
    for i, item in enumerate(remember[:3]):
        with cols[i]:
            st.markdown(
                f'<div class="small-card"><b>⭐</b><br>{item}</div>',
                unsafe_allow_html=True,
            )

# ============================================================
# QUIZ
# ============================================================
st.subheader("🧩 Check your learning")

quiz = safe_list(lesson.get("quiz"))

if not quiz:
    st.warning("No quiz was returned. Please create the lesson again.")
else:
    answers = {}
    for i, q in enumerate(quiz[:5]):
        options = safe_list(q.get("options"))
        if options:
            answers[i] = st.radio(
                f"{i + 1}. {q.get('question', '')}",
                options,
                key=f"answer_{i}",
            )

    if st.button("✅ Check answers", use_container_width=True):
        score = 0
        for i, q in enumerate(quiz[:5]):
            if answers.get(i) == q.get("answer"):
                score += 1

        st.session_state.quiz_score = score

    if st.session_state.get("quiz_score") is not None:
        score = st.session_state.quiz_score
        total = min(5, len(quiz))

        if score == total:
            st.success(f"🏆 Excellent! You scored {score}/{total}.")
        elif score >= total * 0.6:
            st.success(f"🌟 Great work! You scored {score}/{total}.")
        else:
            st.info(
                f"You scored {score}/{total}. Let's review the examples "
                "and try again!"
            )

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "Grok Kids Learning Studio • Streamlit + official xAI Python SDK • "
    "Designed for age-appropriate educational content."
)
