import os
from dotenv import load_dotenv

load_dotenv()

# Groq is our primary AI provider
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 1. Configuration for CrewAI & LangGraph (Using Groq)
# Models are typically passed as strings like "groq/llama-3.3-70b-versatile"
# CrewAI handles the initialization internally when passed the model string.

# 2. Configuration for AutoGen (Using Dictionary Config Base)
autogen_llm_config = {
    "config_list": [
        {
            "model": "llama-3.3-70b-versatile",
            "api_key": GROQ_API_KEY,
            "api_type": "groq"
        }
    ],
    "temperature": 0.3
}
