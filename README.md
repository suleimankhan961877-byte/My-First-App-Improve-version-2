# 🌟 Grok Kids Learning Studio

A professional Streamlit application that uses the **xAI Grok API** to create age-appropriate educational lessons for children.

The app asks for only:

- 📚 Topic
- 👧 Child's age
- 🌍 Language
- 📈 Learning level
- ⏱️ Lesson length

It then generates a complete learning experience containing explanations, examples, educational images, animation scenes, and a quiz.

---

## ✨ Main Features

### 1. Child-friendly lesson creation

The user selects:

**Age**
- 4–6
- 7–9
- 10–12
- 13–15
- 16–17

**Language**
- English
- Urdu
- Arabic
- Spanish
- French
- German
- Chinese
- Turkish
- Hindi
- Portuguese

**Learning level**
- Simple
- Medium
- Advanced

**Lesson length**
- Short
- Medium
- Long

### 2. AI teaching

Grok generates:

- Lesson title
- Introduction
- Learning goals
- Explanation
- Key learning points
- Real-world examples
- Memory/review points

### 3. High-resolution educational illustrations

The app uses xAI's image-generation API to create educational illustrations.

The application requests:

- 2K resolution
- 16:9 aspect ratio
- Child-friendly educational style
- Clear visual storytelling

### 4. Animation

The application generates several educational scenes and combines the images into an animated GIF.

The animation can be downloaded from the Streamlit interface.

### 5. Quiz

Each generated lesson contains five multiple-choice questions.

The application automatically checks the answers and displays the score.

---

# 🛠️ Project Structure

```text
Grok_Kids_Learning_Studio/
│
├── app.py
├── requirements.txt
├── README.md
└── secrets.toml.example
```

---

# 🔑 xAI API Key

This project uses the **xAI API**, not OpenAI and not Gemini.

The environment variable is:

```text
XAI_API_KEY
```

Create/get your API credentials through the official xAI developer platform:

https://console.x.ai/

Important:

> The xAI API is not currently a completely free API. The xAI SDK is free to install, but API requests and image generation can incur charges according to xAI's current pricing.

Check the current pricing before deploying the application for public use.

---

# 🚀 Option 1 — Run Locally on Windows

## Step 1 — Install Python

Install Python 3.10 or newer.

Python:

https://www.python.org/downloads/

During installation, enable:

```text
Add Python to PATH
```

---

## Step 2 — Download the project

Extract the ZIP file.

Open the project folder:

```text
Grok_Kids_Learning_Studio
```

---

## Step 3 — Open Command Prompt

Inside the project folder, open Command Prompt or PowerShell.

Check Python:

```bash
python --version
```

Example:

```text
Python 3.12.x
```

---

## Step 4 — Install dependencies

Run:

```bash
pip install -r requirements.txt
```

---

## Step 5 — Create your API key

Create an xAI API key from the official xAI developer console.

Do not put the key directly inside `app.py`.

---

## Step 6 — Create `.env`

Create a file named:

```text
.env
```

inside the same folder as `app.py`.

Put:

```text
XAI_API_KEY=YOUR_XAI_API_KEY
```

Replace `YOUR_XAI_API_KEY` with your actual key.

Example:

```text
XAI_API_KEY=xai-your-real-key
```

Never publish this file to GitHub.

---

## Step 7 — Start Streamlit

Run:

```bash
streamlit run app.py
```

Streamlit will display a local address such as:

```text
http://localhost:8501
```

Open that address in your browser.

---

# ☁️ Option 2 — Deploy on Streamlit Community Cloud

## Step 1 — Create a GitHub repository

Create a new GitHub repository.

For example:

```text
Grok-Kids-Learning-Studio
```

Upload:

```text
app.py
requirements.txt
README.md
```

Do NOT upload:

```text
.env
```

and do not upload a real API key.

---

## Step 2 — Open Streamlit Community Cloud

Go to:

https://share.streamlit.io/

Sign in with GitHub.

Create a new application.

Select your GitHub repository.

Use:

```text
Branch:
main
```

and:

```text
Main file:
app.py
```

---

## Step 3 — Add the API Secret

In Streamlit Cloud open:

```text
Manage app
    ↓
Settings
    ↓
Secrets
```

Add:

```toml
XAI_API_KEY = "YOUR_XAI_API_KEY"
```

Save the secret.

---

## Step 4 — Reboot

After saving the secret:

```text
Manage app
    ↓
Reboot app
```

The application should start.

---

# 🧪 Test the Application

Try:

```text
Topic:
Solar System

Age:
7–9

Language:
English

Level:
Simple

Length:
Short
```

Click:

```text
✨ Create Complete Lesson
```

The application should generate:

```text
📖 Lesson
     ↓
🎯 Learning Goals
     ↓
🧠 Explanation
     ↓
🔎 Examples
     ↓
🖼️ Educational Images
     ↓
🎬 Animation
     ↓
⭐ Remember
     ↓
🧩 Quiz
```

---

# 🌍 Example Topics

You can test the application with:

### Science

```text
Solar System
Water Cycle
Plants
Gravity
Animals
Human Body
States of Matter
Electricity
```

### Mathematics

```text
Fractions
Addition
Multiplication
Geometry
Decimals
Percentages
```

### General Knowledge

```text
Dinosaurs
Oceans
Weather
Space
Countries
Transportation
```

---

# 🧠 How the Application Works

```text
                    USER
                     │
                     ▼
             Enter learning topic
                     │
                     ▼
       ┌────────────────────────────┐
       │ Age                        │
       │ Language                   │
       │ Learning Level             │
       │ Lesson Length              │
       └────────────────────────────┘
                     │
                     ▼
               xAI Grok API
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
       Lesson     Examples     Quiz
          │          │
          │          ▼
          │     Grok Imagine
          │          │
          │          ▼
          │     2K Images
          │          │
          │          ▼
          │      Animation
          │
          ▼
       Streamlit
          │
          ▼
    Child-friendly lesson
```

---

# 🔐 Security

Never place an API key directly into:

```python
app.py
```

Bad:

```python
XAI_API_KEY = "xai-your-real-key"
```

Use:

```text
.env
```

for local development or:

```text
Streamlit Secrets
```

for Streamlit Cloud.

Also add `.env` to `.gitignore`:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

# ⚠️ API Cost

The application uses two xAI capabilities:

```text
Grok text generation
+
Grok image generation
```

Image generation can cost more than text generation because every generated illustration is an API request.

For development, generate images only when needed and avoid repeatedly regenerating the same scene.

For a public children's application, consider adding:

- Usage limits
- Caching
- Daily generation limits
- Parent/admin controls
- Cost monitoring
- Content moderation
- Error handling
- Authentication

before releasing it publicly.

---

# 🧒 Child Safety

This application is intended as an educational prototype.

For a public deployment for children, add additional safeguards such as:

- No collection of children's personal information
- No open-ended personal chat
- Age-appropriate content filtering
- Parent/teacher controls
- Safe topic restrictions
- Human review for educational material
- Clear privacy policy
- Appropriate compliance review for the countries where the app will operate

The current app instructs the AI to avoid unsafe activities and requests for personal information, but AI-generated content should still be reviewed before being used in a production children's service.

---

# 🧰 Troubleshooting

## Error: `XAI_API_KEY is missing`

Check Streamlit Cloud Secrets:

```toml
XAI_API_KEY = "YOUR_XAI_API_KEY"
```

Make sure the secret name is exactly:

```text
XAI_API_KEY
```

---

## Error: `401 Unauthorized`

The API key may be invalid, expired, or unavailable to the selected API account.

Create/check your API credentials in the xAI developer console.

---

## Error: `429`

This usually indicates a rate limit or account/usage limitation.

Wait and retry, or check the current xAI account usage and limits.

---

## Error: `503`

This is generally a temporary service availability/high-demand problem.

The application retries transient errors automatically. Wait briefly and try again.

---

## Error: `ModuleNotFoundError`

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Then restart Streamlit:

```bash
streamlit run app.py
```

---

# 📦 Requirements

The project uses:

```text
streamlit
xai-sdk
python-dotenv
Pillow
requests
imageio
```

The exact pinned versions are provided in:

```text
requirements.txt
```

---

# 🎯 Future Development

Recommended upgrades for a production version:

1. Voice narration
2. Text-to-speech teacher
3. Interactive animated characters
4. Real video generation
5. Student progress tracking
6. Teacher dashboard
7. Parent dashboard
8. Lesson history
9. PDF lesson export
10. Certificate generation
11. More languages
12. Interactive exercises
13. Adaptive difficulty
14. Accessibility features
15. Usage/cost monitoring

---

## License

This project is provided as a development prototype. Add your preferred software license before distributing it publicly.
