from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()  # Load API keys from .env

def create_csv_chat_agent(csv_path: str, model_name="gpt-4o-mini", temperature=0):
    """
    Creates a LangChain CSV chat agent for a given CSV file.
    
    Args:
        csv_path (str): Path to the CSV file.
        model_name (str): OpenAI model to use.
        temperature (float): Model temperature (creativity).
    
    Returns:
        LangChain agent object that can be queried with `invoke()`.
    """
    # Define system behavior
    system_prompt = SystemMessage(
        content=(
            "You are a helpful and expert data analyst. "
            "Always provide explanations in clear, beginner-friendly terms. "
            "When relevant, include tables and examples in your response."
        )
    )

    # Initialize model with system prompt
    llm = ChatOpenAI(
        temperature=temperature,
        model=model_name,
        messages=[system_prompt]
    )

    # Create and return the CSV agent
    agent = create_csv_agent(
        llm,
        csv_path,
        verbose=True,
        agent_type="openai-tools",
        allow_dangerous_code=True
    )
    return agent
