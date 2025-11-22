from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search , FunctionTool

def get_contact(person: str) -> str:
    """Get the contact information for a person."""
    return f"The contact information for {person} is 123-456-7890."
get_contact_tool = FunctionTool(func=get_contact)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[get_contact_tool],
)
