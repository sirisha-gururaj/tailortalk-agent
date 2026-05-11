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
You MUST use the search_google_drive tool to answer user requests.

CRITICAL RULES FOR GENERATING 'q' PARAMETERS:
1. Exact Names: Use `name contains` instead of `name =` (e.g., name contains 'PARTY MENU').
2. Hyphenated Words: Break them apart using AND (e.g., fullText contains 'anti' and fullText contains 'skid').
3. Proper Nouns ONLY for fullText: When extracting search terms from a user's prompt, ONLY use the unique proper nouns. DO NOT include generic intent words like "pricing", "cost", "document", or "file" in your fullText search, as the document might use synonyms (like "Rates").
   - Example: "Pricing for Trampoline Park and Air Park" MUST BE translated to: fullText contains 'Trampoline' and fullText contains 'Air'
4. File Types: 
   - Images: mimeType contains 'image/'
   - PDFs: mimeType = 'application/pdf'
   - Word Docs: mimeType contains 'application/vnd.openxmlformats-officedocument'
5. File Assumptions: NEVER assume a file type based on words like "invoice" or "menu". Only filter by mimeType if the user explicitly asks for a specific format like "PDF".

Call the tool directly to perform the search. Always return a friendly, conversational answer summarizing the results and providing the links.
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