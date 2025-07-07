from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# Set up environment variables for API key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize the chatbot model
model = ChatGroq(model="llama3-8b-8192")

# FastAPI app setup
app = FastAPI()

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Message format used to send user input to the model
class ChatMessage(BaseModel):
    content: str

# Endpoint to interact with the AI chatbot
@app.post("/chat")
async def chat_with_ai(message: ChatMessage):
    try:
        # Define the system message (acting as the assistant description)
        system_message = SystemMessage(content= "You are a medical assistant chatbot trained to assist users with health-related queries. "
        "Provide only subheadings relevant to the user's query without any additional description. "
        "Your response should be short, clear, and free from any formatting like markdown, symbols, or special characters (e.g., **, _, etc.). "
        "Focus on adaptability, inclusivity, context awareness, and relevance in your answers.")
        
        # Define the user message
        human_message = HumanMessage(content=message.content)

        # Interact with the model
        response = model.invoke([system_message, human_message])
        
        # Return the model's response
        return {"response": response.content}
    
    except Exception as e:
        # Return error message if there's an issue interacting with the model
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")