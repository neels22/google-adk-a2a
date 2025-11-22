from google.adk.agents.llm_agent import Agent


# root agent name to the object is required 
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions in a pirate manner',
)

# google adk has inbuilt converstation memory 