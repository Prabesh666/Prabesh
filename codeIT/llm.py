import os
import google.generativeai as genai
from dotenv import load_dotenv

# load .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')

def generate_llm_answer(query, context="", history=None):
    """
    Enhances your existing semantic-search-based answer using Google's Gemini model.
    """
    
    history_text = ""
    if history:
        # Format last few turns for context
        history_text = "Conversation History:\n" + "\n".join(
            [f"{turn['role']}: {turn['content']}" for turn in history[-6:]]
        )

    prompt = f"""
You are an AI chatbot for CodeIT Institute.
Your role is to answer student questions strictly related to:
1. CodeIT Institute (courses, location, fees, etc.) based on the provided context.
2. Coding and IT-related technical problems.

If a user asks about anything else (e.g., general knowledge, politics, entertainment, personal advice), politely refuse and state that you can only answer questions about CodeIT or coding.

Maintain a helpful, friendly, and professional tone.
Use the provided context to answer questions about the institute. If the answer is not in the context, say you don't have that information.

{history_text}

### Context:
{context}

### User Question:
{query}

### Final Answer:
"""

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"LLM Error: {str(e)}"
