from google.adk.agents.llm_agent import Agent
from pydantic import BaseModel , Field


class GreetingOutput(BaseModel):
    greeting: str = Field(description="The greeting to the user")

root_agent = Agent(
    model='gemini-2.5-flash',
    name='output_schema_agent',
    description='A helpful assistant for user questions.',
    instruction='given person names, respond with a a JSON object with the greeting to the user',
    output_schema=GreetingOutput,
    output_key='greeting',
)
