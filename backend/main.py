import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from backend.drive_tools import search_google_drive

# Load your Groq API key from the .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(title="TailorTalk API")

# Define the structure for incoming chat messages
class ChatRequest(BaseModel):
    message: str

# 1. Initialize the Groq LLM
# The llama3-70b-8192 model is excellent for complex tool-calling tasks
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# 2. Give the agent access to our Drive search tool
tools = [search_google_drive]

# 3. Create the System Prompt
# This teaches the LLM how to format the 'q' parameter string properly
# 3. Create the System Prompt
system_prompt = """You are TailorTalk, an AI assistant that helps users find files in their Google Drive.
When a user asks to find a file, you must use the search_google_drive tool.
You must translate the user's natural language request into a valid Google Drive API 'q' parameter string.

CRITICAL RULES FOR GENERATING 'q' PARAMETERS:
1. Exact Names: Users rarely know file extensions. If they ask for an exact file name (e.g., "PARTY MENU"), ALWAYS use `name contains` instead of `name =` to avoid extension mismatch errors (e.g., name contains 'PARTY MENU').
2. Hyphenated Words: Google Drive search struggles with hyphens. If the user asks for a hyphenated word like "anti-skid", break it apart using AND: fullText contains 'anti' and fullText contains 'skid'.
3. Multi-Concept Text: If a user asks for a document containing a long phrase or multiple concepts (like "Trampoline Park and Air Park"), DO NOT search for the entire long phrase as one string. Break it down into key terms: fullText contains 'Trampoline' and fullText contains 'Air'.
4. File Types: If they ask for "images" or "pictures", use `mimeType contains 'image/'`. If they ask for "documents", do not restrict it to PDFs unless explicitly asked.

Examples of 'q' parameters:
- "Find the financial report" -> name contains 'financial' or name contains 'report'
- "Find PDF files" -> mimeType = 'application/pdf'
- "Find documents modified last week" -> modifiedTime > '2023-10-24T12:00:00'
- "Pricing for Trampoline Park and Air Park" -> fullText contains 'Trampoline' and fullText contains 'Air'

Always return the final answer to the user in a friendly, conversational way, providing the file names and links.
"""

# 4. Create the LangGraph Agent
agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

# 5. Create the API Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Pass the user's message to the agent
        response = agent_executor.invoke(
            {"messages": [HumanMessage(content=request.message)]}
        )
        # The final answer from the LLM is the last message in the list
        final_answer = response["messages"][-1].content
        return {"response": final_answer}
    except Exception as e:
        return {"error": str(e)}