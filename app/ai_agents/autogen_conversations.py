import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent

load_dotenv()


def run_complex_debate(query: str) -> str:
    """Run AutoGen debate powered by Groq for blazing fast inference."""

    # Groq config for AutoGen (uses OpenAI-compatible API)
    groq_config = {
        "config_list": [
            {
                "model": "llama-3.3-70b-versatile",
                "api_key": os.getenv("GROQ_API_KEY"),
                "api_type": "groq",
                "base_url": "https://api.groq.com/openai/v1",
            }
        ],
        "temperature": 0.7,
    }

    # 1. Financial Strategist
    financial_strategist = AssistantAgent(
        name="Financial_Strategist",
        system_message=(
            "You are a senior financial strategist. Provide cutting "
            "edge strategies for ROI based on data. If the risk analyst "
            "criticizes your plan, you must defend it with better "
            "metrics or adjust the strategy."
        ),
        llm_config=groq_config,
    )

    # 2. Risk Analyst
    risk_analyst = AssistantAgent(
        name="Risk_Analyst",
        system_message=(
            "You are a highly critical risk analyst. You must harshly "
            "analyze the financial strategist's plans, poke holes in "
            "their assumptions, and demand concrete evidence. "
            "Do not agree easily."
        ),
        llm_config=groq_config,
    )

    # 3. User Proxy (no human input)
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        is_termination_msg=lambda x: x.get(
            "content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )

    # Run the debate
    user_proxy.initiate_chat(
        financial_strategist,
        message=f"Create a strategic framework for this query: {query}",
        summary_method="reflection_with_llm",
    )

    user_proxy.initiate_chat(
        risk_analyst,
        message="Now analyze the strategist's latest plan for risks.",
        summary_method="reflection_with_llm",
        clear_history=False,
    )

    chat_history = user_proxy.chat_messages[risk_analyst]
    if chat_history:
        return chat_history[-1]["content"]

    return "No discussion was generated."
