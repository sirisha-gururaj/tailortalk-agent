# TailorTalk - Google Drive Discovery Agent

## Live Application
- **Live Streamlit App:** [https://tailortalk-frontend-mpof.onrender.com/]
- **Live FastAPI Backend:** [https://tailortalk-backend-kmq8.onrender.com/]

## Project Overview
TailorTalk is a conversational AI agent designed to assist users in searching, filtering, and discovering files within a designated Google Drive repository. It engages in natural back-and-forth conversation, understands search intent, and executes precise queries utilizing the Google Drive API's `q` parameter.

## Technical Stack
- **Backend:** Python with FastAPI
- **Agent Framework:** LangGraph
- **LLM:** Groq (llama-3.3-70b-versatile) for high-speed, accurate tool calling
- **Frontend:** Streamlit
- **Integration:** Google Drive API via Service Account

## Features
- **Natural Language to API Translation:** Uses LangGraph and Groq to translate conversational requests into valid Google Drive `q` parameter strings.
- **Advanced Discoverability:** Capable of executing complex searches using `files.list`, including:
  - Exact and partial file names (`name contains`)
  - File types (`mimeType`)
  - Full-text OCR search within documents (`fullText contains`)
  - Multi-condition logical operators (AND/OR)
- **Robust Deployment:** Fully separated frontend and backend architectures deployed via Render.

## Local Setup Instructions

1. **Clone the repository:**

```bash
git clone [https://github.com/YOUR_USERNAME/tailortalk-agent.git](https://github.com/YOUR_USERNAME/tailortalk-agent.git)
cd tailortalk-agent
```
   
2. **Set up a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Environment Variables:**
- Create a .env file in the root directory and add your Groq API key:

```bash
GROQ_API_KEY=your_api_key_here
```

5. **Google Drive Credentials:**
- Place your Service Account JSON key inside the root directory and name it service_account.json. Ensure the target Google Drive folder is shared with the service account's client email.

6. **Run the Backend (FastAPI):**

```bash
uvicorn backend.main:app --reload
```

7. **Run the Frontend (Streamlit):**
- Open a new terminal, activate the environment, and run:

```bash
streamlit run frontend/app.py
```