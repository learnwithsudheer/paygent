"""
Payment Agent Module

This module implements a sophisticated payment and investment assistant using LangChain.
It provides functionality for cryptocurrency investment checks, price bargaining,
and payment processing through the Payman system.

The agent can:
- Check cryptocurrency prices against moving averages
- Attempt price negotiations
- Process payments
- Manage payees
- Handle money requests
"""

import requests
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_payman_tool import (
    AddPayeeTool,
    AskForMoneyTool,
    GetBalanceTool,
    SearchPayeesTool,
    SendPaymentTool,
)

# Load environment variables at module initialization
load_dotenv()

# API configuration
API_BASE_URL = "http://localhost:8000"


@tool
def check_crypto_investment(coin_name: str) -> bool:
    """
    Check if a cryptocurrency is below its 50-day moving average.

    Args:
        coin_name (str): The name of the cryptocurrency to check

    Returns:
        bool: True if the current price is below the 50-day moving average,
              False otherwise or in case of error
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/check-crypto-price",
            json={"coin_name": coin_name}
        )
        if response.status_code == 200:
            return response.json()["below_ma"]
    except requests.RequestException:
        return False
    return False


@tool
def attempt_bargain(target_price: float, offered_price: float) -> bool:
    """
    Attempt to bargain for a better price.

    Args:
        target_price (float): The original asking price
        offered_price (float): The price being offered

    Returns:
        bool: True if the bargain was successful, False otherwise
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/bargain",
            json={
                "target_price": float(target_price),
                "offered_price": float(offered_price)
            }
        )
        if response.status_code == 200:
            return response.json()["success"]
    except requests.RequestException:
        return False
    return False


def create_payment_agent() -> AgentExecutor:
    """
    Create and configure a payment agent with all necessary tools and prompts.

    The agent is configured with tools for:
    - Payment processing
    - Payee management
    - Cryptocurrency investment checking
    - Price bargaining

    Returns:
        AgentExecutor: Configured agent executor ready to process requests
    """
    # Initialize all available tools
    tools = [
        SendPaymentTool(),
        SearchPayeesTool(),
        AddPayeeTool(),
        AskForMoneyTool(),
        GetBalanceTool(),
        check_crypto_investment,
        attempt_bargain
    ]
    
    # Configure the agent's system prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a sophisticated payment and investment assistant that can \
help with payments, investments, and price negotiations. You have access to the \
following payees in the Payman system:
- Kiran (for business transactions)
- Coinbase (for cryptocurrency purchases)

When handling requests:

For bargaining and purchases:
- Always try to negotiate for a better price starting with 15% below asking
- If bargaining is successful, automatically process the payment to the correct payee
- For Kiran: Use SendPaymentTool to send the payment after successful bargaining

For cryptocurrency investments:
- Check if the price is below the 50-day moving average
- If price is favorable, use SendPaymentTool to send funds to Coinbase
- Always verify Coinbase is in the payee list before proceeding

General guidelines:
- Always search for payees using SearchPayeesTool before transactions
- Verify all payment details before processing
- Provide clear explanations of your actions
- If a payee is not found, inform the user

Remember to handle transactions step by step:
1. Verify payee existence
2. Check conditions (bargaining or crypto price)
3. Calculate final amounts
4. Process payments if conditions are met"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Initialize the language model and create the agent
    llm = ChatOpenAI(temperature=0)
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)