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
system_prompt = """You are TailorTalk, an AI assistant that helps users find files in their Google Drive.
When a user asks to find a file, you MUST use the search_google_drive tool.
You must translate the user's natural language request into a valid Google Drive API 'q' parameter string and pass it as the `query` argument.

CRITICAL RULES FOR GENERATING 'q' PARAMETERS:
1. Exact Names: Users rarely know file extensions. If they ask for an exact file name (e.g., "PARTY MENU"), ALWAYS use `name contains` instead of `name =` (e.g., name contains 'PARTY MENU').
2. Hyphenated Words: Break them apart using AND. For "anti-skid", use: fullText contains 'anti' and fullText contains 'skid'.
3. Multi-Concept Text: Break long phrases down. For "Trampoline Park and Air Park", use: fullText contains 'Trampoline' and fullText contains 'Air'.
4. File Types: For "images", use `mimeType contains 'image/'`. For "documents", do not restrict to PDFs unless explicitly asked.
5. File Assumptions: NEVER assume the mimeType of a file based on words like "invoice" or "menu". Only use mimeType filters if explicitly requested (e.g., "PDFs").
6. Tool Format: ALWAYS use native JSON tool calling. NEVER generate raw XML or `<function>` tags. Pass ONLY the 'q' string.

Examples of valid tool queries:
- User: "Find the financial report" -> Query: name contains 'financial' or name contains 'report'
- User: "Find PDF files" -> Query: mimeType = 'application/pdf'
- User: "Find Word documents" -> Query: mimeType contains 'application/vnd.openxmlformats-officedocument'
- User: "Pricing for Trampoline Park and Air Park" -> Query: fullText contains 'Trampoline' and fullText contains 'Air'

Always return the final answer to the user in a friendly, conversational way, providing the file names and links.
"""

# 4. Create the LangGraph Agent
agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

@app.get("/")
async def root():
    return {"message": "TailorTalk API is actively running! The agent endpoint is located at /chat"}

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