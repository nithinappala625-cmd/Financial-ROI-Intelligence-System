import os
import sys
from dotenv import load_dotenv

# Load .env FIRST before any other imports
load_dotenv(override=True)

# Fix rich recursion bug on Windows
sys.setrecursionlimit(5000)

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Verify keys
print(f"GROQ_API_KEY loaded: {os.getenv('GROQ_API_KEY', 'not_set')[:12]}...")


def test_crewai_langgraph():
    print("\n--- Testing CrewAI + LangGraph Pipeline ---")
    from app.ai_agents.workflow import process_query_agentic

    query = ("What is the budget status of Project Alpha, "
             "and are we at risk of an overrun?")
    print(f"Query: {query}\n")
    try:
        response = process_query_agentic(query)
        print("\n" + "=" * 60)
        print("[CREWAI RESPONSE]:")
        print("=" * 60)
        print(response)
        print("=" * 60)
    except Exception as e:
        print(f"\n[Error in CrewAI/LangGraph Phase]: {e}")


def test_autogen():
    print("\n--- Testing AutoGen Debate Pipeline ---")
    from app.ai_agents.autogen_conversations import run_complex_debate

    query = ("We have a $500k budget for a new neural network "
             "training cluster. How should we allocate it?")
    print(f"Query: {query}\n")
    try:
        response = run_complex_debate(query)
        print("\n" + "=" * 60)
        print("[AUTOGEN RESPONSE]:")
        print("=" * 60)
        print(response)
        print("=" * 60)
    except Exception as e:
        print(f"\n[Error in AutoGen Phase]: {e}")


if __name__ == "__main__":
    # Test 1: CrewAI + LangGraph
    test_crewai_langgraph()

    # Test 2: AutoGen
    test_autogen()
