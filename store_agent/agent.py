import uuid                      
from dotenv import load_dotenv   
from pydantic import BaseModel, Field # We are going to use structured outputs again!
from google.adk.sessions import InMemorySessionService
from google.adk.agents   import Agent
from google.adk.runners  import Runner
from google.genai        import types

load_dotenv()  

# Defining our schema using pydantic
class StateOutput(BaseModel):
    fav_color: str    = Field(description="Favourite colour of user.")
    name:      str    = Field(description="Name of the user.")
    fav_subject: str  = Field(description="Favourite subject of the user.")

# Creating the same agent but this time with structured outputs!
chef = Agent(
    name="InformationAgent",
    model="gemini-2.0-flash",
    instruction="""
You are a helpful assistant that knows the user's name, favorite colour, and favorite subject.

Current state:
- name: {name}
- fav_color: {fav_color}
- fav_subject: {fav_subject}

If the user asks to update anything, reply *only* with JSON matching this schema: 

{
  "fav_color": "<new colour>",
  "name": "<new name>",
  "fav_subject": "<new subject>"
}

When updating, preserve existing values for fields that should remain the same. Only change the specific fields mentioned by the user.

Otherwise, answer their question in plain text.
""",
    output_schema=StateOutput,    # Enforces that the model returns exactly those three fields
    output_key="state"            # Key under which the structured output will appear
)

# We are setting up the in-memory session service again
service    = InMemorySessionService()
session_id = str(uuid.uuid4())

service.create_session(
    app_name="InformationApp",
    user_id="vaibhav",
    session_id=session_id,
    # same state as before
    state={
        "fav_color":   "green",
        "name":        "Vaibhav",
        "fav_subject": "Mathematics",
    },
)

# creating the same runner
waiter = Runner(
    agent=chef,
    session_service=service,
    app_name="InformationApp"
)

# building the user message but this time also saying to update it
msg = types.Content(
    role="user",
    parts=[types.Part(text=(
        "Please change my favorite color to red and my favourite subject to Computer Science."
    ))]
)

# Running the agent and capture raw output
for ev in waiter.run(user_id="vaibhav", session_id=session_id, new_message=msg):
    if ev.is_final_response() and ev.content and ev.content.parts:
        raw = ev.content.parts[0].text
        print(raw, "\n")
        print("------------------------")

# Get the updated session and apply structured output
session = service.get_session(
    app_name="InformationApp",
    user_id="vaibhav",
    session_id=session_id
)

# Checks if structured output exists in session state under the output_key
if "state" in session.state:
    structured_data = session.state["state"]
    print("✅ Updating session state:")
    
    # Applying the structured updates to the main session state keys through for-loop
    for key, value in structured_data.items():
        session.state[key] = value
        print(f"  - {key} updated to: {value}")
    
    # Removes the temporary "state" key to clean up
    del session.state["state"]
else:
    print("No structured output found in session state.")

# Printing the new session state to confirm
print("\n📘 Final session state:")
for key, value in session.state.items():
    print(f"{key}: {value}")