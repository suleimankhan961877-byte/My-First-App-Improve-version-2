import io
import json
import os
import re
import time
from pathlib import Path

import imageio.v2 as imageio
import streamlit as st
from PIL import Image, ImageDraw
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user

load_dotenv()

st.set_page_config(
    page_title="Grok Kids Learning Studio",
    page_icon="🌟",
    layout="wide",
)

# Current xAI models documented by xAI.
TEXT_MODEL = "grok-4.6"
IMAGE_MODEL = "grok-imagine-image-2.0"


def get_secret(name: str) -> str:
    """Read a Streamlit Secret first, then a local .env variable."""
    try:
        value = st.secrets.get(name)
        if value:
            return str(value).strip()
    except Exception:
        pass
    return os.getenv(name, "").strip()


def get_api_key() -> str:
    return get_secret("XAI_API_KEY")


def is_demo_mode() -> bool:
    # Demo mode is intentionally key-free. It lets you test the Streamlit
    # interface without making an xAI API request.
    return not bool(get_api_key())


def make_client() -> Client:
    key = get_api_key()
    if not key:
        raise RuntimeError("No XAI_API_KEY was supplied.")
    return Client(api_key=key)


def clean_json(text: str):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.I)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def validate_api_key():
    """Validate the key before generating a lesson."""
    client = make_client()
    info = client.auth.get_api_key_info()
    return info


def generate_lesson_with_grok(topic, age, language, level, length):
    client = make_client()

    prompt = f"""
Create an age-appropriate educational lesson.

Topic: {topic}
Child age: {age}
Language: {language}
Learning level: {level}
Lesson length: {length}

Return ONLY valid JSON.

Required schema:
{{
  "title": "short title",
  "welcome": "friendly introduction",
  "learning_goals": ["goal 1", "goal 2", "goal 3"],
  "explanation": "clear age-appropriate explanation",
  "examples": [
    {{
      "title": "example",
      "explanation": "simple example",
      "visual_prompt": "detailed educational illustration prompt"
    }},
    {{
      "title": "example",
      "explanation": "simple example",
      "visual_prompt": "detailed educational illustration prompt"
    }},
    {{
      "title": "example",
      "explanation": "simple example",
      "visual_prompt": "detailed educational illustration prompt"
    }}
  ],
  "animation": {{
    "narration": "short narration",
    "scenes": [
      {{
        "title": "scene 1",
        "description": "what the child learns",
        "visual_prompt": "educational illustration prompt"
      }},
      {{
        "title": "scene 2",
        "description": "what the child learns",
        "visual_prompt": "educational illustration prompt"
      }},
      {{
        "title": "scene 3",
        "description": "what the child learns",
        "visual_prompt": "educational illustration prompt"
      }},
      {{
        "title": "scene 4",
        "description": "what the child learns",
        "visual_prompt": "educational illustration prompt"
      }}
    ]
  }},
  "remember": ["key point 1", "key point 2", "key point 3"],
  "quiz": [
    {{
      "question": "question",
      "options": ["A", "B", "C", "D"],
      "answer": "exact correct option",
      "explanation": "short explanation"
    }}
  ]
}}

Rules:
- Exactly 5 quiz questions.
- Exactly 4 options per question.
- The answer must exactly match one option.
- Use the requested language.
- Match the requested age, level and length.
- Use concrete everyday examples.
- Keep the content safe, factual and encouraging.
- Do not request personal information.
- Visual prompts must be child-friendly and suitable for high-resolution
  educational image generation.
"""

    last_error = None
    for attempt in range(3):
        try:
            chat = client.chat.create(model=TEXT_MODEL)
            chat.append(user(prompt))
            response = chat.sample()
            content = getattr(response, "content", None)

            if not content:
                raise RuntimeError("xAI returned an empty response.")

            data = clean_json(content)
            if not isinstance(data, dict):
                raise RuntimeError("xAI returned invalid lesson JSON.")
            return data

        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

    raise RuntimeError(str(last_error))


def demo_lesson(topic, age, language, level, length):
    """Free local lesson so the app can be tested without an xAI API key."""
    return {
        "title": f"Let's learn about {topic}",
        "welcome": (
            f"Welcome! Today we will explore {topic} using simple explanations, "
            "examples and pictures."
        ),
        "learning_goals": [
            f"Understand the main idea of {topic}.",
            "Connect the idea to an everyday example.",
            "Remember three important facts.",
        ],
        "explanation": (
            f"This is a free demonstration lesson for {topic}. "
            f"Your selected age is {age}, language is {language}, "
            f"level is {level}, and lesson length is {length}. "
            "Add an xAI API key to replace this demonstration content with "
            "AI-generated Grok lessons."
        ),
        "examples": [
            {
                "title": "Everyday example",
                "explanation": f"Think about something you see every day that relates to {topic}.",
                "visual_prompt": f"Friendly educational illustration for children explaining {topic}.",
            },
            {
                "title": "A simple example",
                "explanation": f"Break {topic} into one small idea and explain it step by step.",
                "visual_prompt": f"Colorful classroom illustration teaching {topic} to children.",
            },
            {
                "title": "Let's remember",
                "explanation": f"Say the main idea of {topic} in your own words.",
                "visual_prompt": f"Clean educational poster illustration summarizing {topic} for children.",
            },
        ],
        "animation": {
            "narration": f"Let's learn about {topic}, one step at a time.",
            "scenes": [
                {"title": "Start", "description": f"Introduce {topic}.",
                 "visual_prompt": f"Educational opening scene about {topic} for children."},
                {"title": "Explore", "description": f"Show one important idea about {topic}.",
                 "visual_prompt": f"Children exploring an educational concept about {topic}."},
                {"title": "Example", "description": f"Show a practical example of {topic}.",
                 "visual_prompt": f"Simple real-world example demonstrating {topic}."},
                {"title": "Review", "description": f"Review the main idea of {topic}.",
                 "visual_prompt": f"Friendly educational review scene about {topic}."},
            ],
        },
        "remember": [
            f"{topic} has a main idea we can explain simply.",
            "Examples help us understand difficult ideas.",
            "Practice makes learning easier.",
        ],
        "quiz": [
            {"question": f"What are we learning about?", "options": [topic, "Music", "Cooking", "Sports"],
             "answer": topic, "explanation": "The selected topic is the subject of the lesson."},
            {"question": "What helps us understand an idea?", "options": ["Examples", "Ignoring it", "Guessing only", "Skipping it"],
             "answer": "Examples", "explanation": "Examples connect ideas to things we understand."},
            {"question": "Which learning style is selected?", "options": [level, "Unknown", "None", "Different"],
             "answer": level, "explanation": "This is the level selected in the app."},
            {"question": "What can pictures do?", "options": ["Help explain ideas", "Erase learning", "Stop questions", "Do nothing"],
             "answer": "Help explain ideas", "explanation": "Pictures can make concepts easier to understand."},
            {"question": "What should a learner do after a lesson?", "options": ["Review and practice", "Never think about it", "Forget it", "Skip all examples"],
             "answer": "Review and practice", "explanation": "Review and practice reinforce learning."},
        ],
    }


def make_local_illustration(title, description, topic, index=0):
    """Free local illustration used in Demo Mode."""
    img = Image.new("RGB", (1280, 720), "white")
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((35, 35, 1245, 685), outline="black", width=5)
    draw.text((75, 75), f"{topic}", fill="black")
    draw.text((75, 145), f"{index + 1}. {title}", fill="black")

    # Simple educational visual elements.
    cx, cy = 950, 330
    draw.ellipse((cx - 130, cy - 130, cx + 130, cy + 130), outline="black", width=7)
    draw.line((cx, cy + 130, cx, cy + 245), fill="black", width=7)
    draw.line((cx - 70, cy + 185, cx + 70, cy + 185), fill="black", width=7)

    draw.text((75, 260), description[:400], fill="black")
    draw.text((75, 580), "Free Demo Illustration", fill="black")
    return img


def generate_grok_image(prompt):
    client = make_client()
    response = client.image.sample(
        prompt=(
            "Create a professional, high-resolution educational illustration "
            "for children. Use a clean, colorful, friendly, non-scary visual "
            "style. Make the concept accurate and easy to understand. "
            "Avoid unnecessary text in the image.\n\n" + prompt
        ),
        model=IMAGE_MODEL,
        resolution="2k",
        aspect_ratio="16:9",
        quality="medium",
    )

    url = getattr(response, "url", None)
    if not url:
        raise RuntimeError("xAI image API returned no image URL.")

    import requests
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def build_animation(images):
    buffer = io.BytesIO()
    imageio.mimsave(
        buffer,
        [img.convert("RGB") for img in images],
        format="GIF",
        duration=1.1,
        loop=0,
    )
    return buffer.getvalue()


def render_quiz(quiz):
    st.subheader("🧩 Check your learning")

    answers = {}
    for i, question in enumerate(quiz[:5]):
        options = question.get("options", [])
        if options:
            answers[i] = st.radio(
                f"{i + 1}. {question.get('question', '')}",
                options,
                key=f"quiz_{i}",
            )

    if st.button("✅ Check answers", use_container_width=True):
        score = 0
        for i, question in enumerate(quiz[:5]):
            if answers.get(i) == question.get("answer"):
                score += 1

        st.session_state.score = score

    if st.session_state.get("score") is not None:
        total = min(5, len(quiz))
        score = st.session_state.score

        if score == total:
            st.success(f"🏆 Excellent! {score}/{total}")
        elif score >= 3:
            st.success(f"🌟 Great work! {score}/{total}")
        else:
            st.info(f"Keep practicing! {score}/{total}")


# ------------------------------------------------------------
# UI
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .hero {
        padding: 28px;
        border: 1px solid rgba(120,120,120,.25);
        border-radius: 20px;
        margin-bottom: 20px;
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
        Learn through explanations, examples, pictures, animation and quizzes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
            "English", "Urdu", "Arabic", "Spanish", "French",
            "German", "Chinese", "Turkish", "Hindi", "Portuguese",
        ],
    )

    level = st.selectbox(
        "📈 Learning level",
        ["Simple", "Medium", "Advanced"],
    )

    length = st.selectbox(
        "⏱️ Lesson length",
        ["Short", "Medium", "Long"],
    )

    st.divider()

    if is_demo_mode():
        st.warning(
            "FREE DEMO MODE\n\n"
            "No XAI_API_KEY was found. You can test the interface for free. "
            "Real Grok generation requires a valid xAI API key."
        )
    else:
        st.success("xAI API key detected.")

    st.caption(f"Text model: {TEXT_MODEL}")
    st.caption(f"Image model: {IMAGE_MODEL}")

topic = st.text_input(
    "📚 What would you like to teach?",
    placeholder="Example: Solar System, Fractions, Plants, Gravity",
)

col1, col2 = st.columns([3, 1])
with col1:
    create = st.button(
        "✨ Create Complete Lesson",
        type="primary",
        use_container_width=True,
    )
with col2:
    test_key = st.button(
        "🔑 Test API Key",
        use_container_width=True,
    )

if test_key:
    if is_demo_mode():
        st.info(
            "No API key is configured. The app is working in free Demo Mode. "
            "For real Grok generation, add XAI_API_KEY to Streamlit Secrets."
        )
    else:
        try:
            info = validate_api_key()
            st.success(
                "API key accepted by xAI. "
                f"Team ID: {getattr(info, 'team_id', 'available')}"
            )
        except Exception as exc:
            st.error(
                "The XAI_API_KEY is not accepted by xAI.\n\n"
                f"Details: {exc}"
            )
            st.info(
                "Create a fresh API key in the xAI Console and replace the "
                "old Streamlit Secret. Do not paste an API key into app.py."
            )

if create:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    try:
        with st.spinner("Preparing your lesson..."):
            if is_demo_mode():
                lesson = demo_lesson(topic.strip(), age, language, level, length)
                st.session_state.demo_mode = True
            else:
                lesson = generate_lesson_with_grok(
                    topic.strip(), age, language, level, length
                )
                st.session_state.demo_mode = False

            st.session_state.lesson = lesson
            st.session_state.topic = topic.strip()
            st.session_state.example_images = {}
            st.session_state.animation_images = []
            st.session_state.score = None

    except Exception as exc:
        st.error(f"Could not create the lesson: {exc}")
        st.info(
            "If you are using real Grok mode, check XAI_API_KEY in Streamlit "
            "Secrets. If you want to test the interface without API costs, "
            "remove the secret and the app will automatically use Demo Mode."
        )
        st.stop()

if "lesson" not in st.session_state:
    st.info("Enter a topic and click **Create Complete Lesson**.")
    st.stop()

lesson = st.session_state.lesson
topic = st.session_state.topic

if st.session_state.get("demo_mode"):
    st.info(
        "🆓 Free Demo Mode is active. The lesson and illustrations are local "
        "test content. No xAI API request is made."
    )
else:
    st.success("🤖 Grok Mode is active.")

st.divider()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Age", age)
c2.metric("Language", language)
c3.metric("Level", level)
c4.metric("Length", length)

st.header(f"📖 {lesson.get('title', topic)}")
st.write(lesson.get("welcome", ""))

st.subheader("🎯 Learning goals")
for goal in lesson.get("learning_goals", []):
    st.write(f"• {goal}")

st.subheader("🧠 Explanation")
st.write(lesson.get("explanation", ""))

st.subheader("🔎 Learn through examples")

for i, example in enumerate(lesson.get("examples", [])[:3]):
    with st.expander(
        f'Example {i + 1}: {example.get("title", "Example")}',
        expanded=(i == 0),
    ):
        st.write(example.get("explanation", ""))

        key = f"example_{i}"
        if key not in st.session_state.example_images:
            if st.button(
                f"🖼️ Create illustration {i + 1}",
                key=f"image_button_{i}",
            ):
                try:
                    with st.spinner("Creating illustration..."):
                        if st.session_state.get("demo_mode"):
                            image = make_local_illustration(
                                example.get("title", ""),
                                example.get("explanation", ""),
                                topic,
                                i,
                            )
                        else:
                            image = generate_grok_image(
                                example.get("visual_prompt", "")
                            )
                        st.session_state.example_images[key] = image
                except Exception as exc:
                    st.error(f"Image generation failed: {exc}")

        if key in st.session_state.example_images:
            st.image(
                st.session_state.example_images[key],
                caption=f"Educational illustration {i + 1}",
                use_container_width=True,
            )

st.subheader("🎬 Learn through animation")

animation = lesson.get("animation", {})
scenes = animation.get("scenes", [])

st.write(animation.get("narration", ""))

if st.button("🎬 Generate animated lesson", use_container_width=True):
    images = []
    progress = st.progress(0)

    for i, scene in enumerate(scenes[:4]):
        try:
            with st.spinner(f"Preparing scene {i + 1}..."):
                if st.session_state.get("demo_mode"):
                    image = make_local_illustration(
                        scene.get("title", ""),
                        scene.get("description", ""),
                        topic,
                        i,
                    )
                else:
                    image = generate_grok_image(
                        scene.get("visual_prompt", "")
                    )
                images.append(image)
        except Exception as exc:
            st.error(f"Scene {i + 1} failed: {exc}")
            break

        progress.progress((i + 1) / min(4, len(scenes)))

    if len(images) == min(4, len(scenes)):
        st.session_state.animation_images = images

if st.session_state.get("animation_images"):
    animation_bytes = build_animation(
        st.session_state.animation_images
    )

    st.image(animation_bytes, caption="Animated lesson")

    st.download_button(
        "⬇️ Download animation",
        data=animation_bytes,
        file_name="kids_learning_animation.gif",
        mime="image/gif",
        use_container_width=True,
    )

st.subheader("⭐ Remember")
for item in lesson.get("remember", []):
    st.write(f"• {item}")

render_quiz(lesson.get("quiz", []))

st.divider()
st.caption(
    "Grok Kids Learning Studio • Streamlit • xAI API • "
    "Free local Demo Mode available"
)
