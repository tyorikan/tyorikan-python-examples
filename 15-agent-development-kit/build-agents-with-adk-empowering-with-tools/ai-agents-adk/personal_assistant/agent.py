from custom_agents import google_search_agent
from custom_functions import get_fx_rate
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, agent_tool, langchain_tool
from third_party_tools import langchain_wikipedia_tool

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge in Japanese',
    tools=[
        FunctionTool(get_fx_rate),
        agent_tool.AgentTool(agent=google_search_agent),
        langchain_tool.LangchainTool(langchain_wikipedia_tool),
    ]
)
