from typing import Any, Dict

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

# Load environment variables
load_dotenv()


# Mock tool implementation
def get_current_time(city: str) -> Dict[str, Any]:
    """Returns the current time in a specified city."""
    # In a real app, this would call an API
    return {"status": "success", "city": city, "time": "10:30 AM"}


# Define the agent
root_agent = Agent(
    model="gemini-2.5-flash",  # Using a cost-effective model
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
)
