# Our Imports
import asyncio
import time
import uuid
from dotenv import load_dotenv

from google.adk.sessions import DatabaseSessionService
from google.adk.agents   import Agent
from google.adk.runners  import Runner
from google.genai        import types
from google.adk.events.event import Event

# We are going to create our own habit agent!

load_dotenv()

DB_URL   = "sqlite:///./habit_data.db"         # persistent storage file
APP_NAME = "Habit Tracker"
USER_ID  = "bob"

# All of the tools our agent will have access to

# Adding the habit
def add_habit(habit: str, tool_context=None) -> dict:
    """Add a new habit to track"""
    if tool_context and hasattr(tool_context, 'state'):
        # Use tool_context.state if available (proper ADK way)
        habits = tool_context.state.get("habits", [])
        habits.append({"habit": habit})
        tool_context.state["habits"] = habits
        print(f"[State] Added habit: {habit}")
        print_habits(habits)
        return {"action": "add_habit", "habit": habit, "message": f"Added habit: {habit}"}
    else:
        # Fallback: manually update session state and persist to database
        session = service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        habits = session.state.get("habits", [])
        habits.append({"habit": habit})
        
        # Create an event with state delta to persist changes
        from google.adk.sessions import types as session_types
        
        # Here we create an event to keep track of the action we just did - adding a new task
        event = Event(
            id=str(uuid.uuid4()),
            author="user",
            content=types.Content(
                role="user", 
                parts=[types.Part(text=f"Add habit: {habit}")]
            ),
            actions=session_types.Actions(
                state_delta={"habits": habits}
            ),
            timestamp=time.time(),
            turn_complete=True
        )
        
        # Append the event to persist state changes
        service.append_event(session=session, event=event)
        
        print(f"[State] Added habit: {habit}")
        print_habits(habits)
        return {"action": "add_habit", "habit": habit, "message": f"Added habit: {habit}"}

# Viewing the habit
def view_habits(tool_context=None) -> dict:
    """View all current habits"""
    if tool_context and hasattr(tool_context, 'state'):
        
        # Use tool_context.state if available (proper ADK way)
        habits = tool_context.state.get("habits", [])
        print_habits(habits)
        return {"action": "view_habits", "message": "Here are your current habits"}
    
    else:
        # Fallback: again we manually get session state
        session = service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        habits = session.state.get("habits", [])
        print_habits(habits)
        return {"action": "view_habits", "message": "Here are your current habits"}

# Deleting the habit
def delete_habit(index: int, tool_context=None) -> dict:
    """Delete a habit by its index (1-based)"""
    if tool_context and hasattr(tool_context, 'state'):
        # Use tool_context.state if available (proper ADK way)
        habits = tool_context.state.get("habits", [])
        
        if 1 <= index <= len(habits):
            removed = habits.pop(index - 1)
            tool_context.state["habits"] = habits
            
            print(f"[State] Deleted habit {index}: {removed['habit']}")
            print_habits(habits)
            return {"action": "delete_habit", "index": index, "message": f"Deleted habit {index}: {removed['habit']}"}
        else:
            print(f"[State] Invalid index for delete: {index}")
            return {"action": "delete_habit", "index": index, "message": f"Invalid habit index: {index}"}
    else:
        # Fallback: manually update session state and persist to database
        session = service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        habits = session.state.get("habits", [])
        
        if 1 <= index <= len(habits):
            removed = habits.pop(index - 1)
            
            # Create an event with state delta to persist changes
            from google.adk.sessions import types as session_types
            
            event = Event(
                id=str(uuid.uuid4()),
                author="user",
                content=types.Content(
                    role="user", 
                    parts=[types.Part(text=f"Delete habit {index}: {removed['habit']}")]
                ),
                actions=session_types.Actions(
                    state_delta={"habits": habits}
                ),
                timestamp=time.time(),
                turn_complete=True
            )
            
            # Append the event to persist state changes
            service.append_event(session=session, event=event)
            
            print(f"[State] Deleted habit {index}: {removed['habit']}")
            print_habits(habits)
            return {"action": "delete_habit", "index": index, "message": f"Deleted habit {index}: {removed['habit']}"}
        else:
            print(f"[State] Invalid index for delete: {index}")
            return {"action": "delete_habit", "index": index, "message": f"Invalid habit index: {index}"}

# defining our agent here!
habit_agent = Agent(
    name="habit_agent",
    model="gemini-2.0-flash",
    description="Persistent habit-tracking assistant",
    instruction="""
You help users track daily habits. You have access to the current state and can modify it.

When the user:
  • says "add X"          → call add_habit("X")
  • says "view"           → call view_habits()
  • says "delete N"       → call delete_habit(N)

Always greet the user by name and confirm any action taken.

Current state:
- user_name: {user_name}
- habits: {habits}
""",
    tools=[add_habit, view_habits, delete_habit],
)

# creating our session state
service = DatabaseSessionService(db_url=DB_URL)
initial_state = {"user_name": "Bob", "habits": []}

# seeing if we have a pre-existing session
resp = service.list_sessions(app_name=APP_NAME, user_id=USER_ID)
if resp.sessions:
    SESSION_ID = resp.sessions[0].id
    print("Continuing session:", SESSION_ID)
else:
    SESSION_ID = service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    ).id
    print("Created new session:", SESSION_ID)

# creating our runner
runner = Runner(agent=habit_agent, app_name=APP_NAME, session_service=service)

# Printing habits - FOR DEBUGGING PURPOSES (can delete if needed)
def print_habits(habits):
    if not habits:
        print("[Habits] (none)")
    else:
        print("[Habits]")
        for idx, h in enumerate(habits, 1):
            print(f"  {idx}. {h.get('habit')}")

# function to call the agent
async def ask_agent(text: str): # for improved efficiency
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    
    async for ev in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=msg
    ):
        # Only print the assistant's text part, ignore warnings about non-text parts
        if ev.is_final_response() and ev.content and ev.content.parts:
            # Only print text parts
            for part in ev.content.parts:
                if hasattr(part, 'text') and part.text:
                    print("\nAssistant:", part.text)


# our loop to chat with our agent
async def main():
    print("\nHabit Tracker ready (type 'quit' to exit)\n")
    while True:
        q = input("You: ")
        if q.lower() in ("quit", "exit"):
            print("Session saved. Bye!")
            break
        await ask_agent(q)

if __name__ == "__main__":
    asyncio.run(main())