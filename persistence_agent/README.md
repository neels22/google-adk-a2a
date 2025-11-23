# Persistence Agent Explanation

## What This Code Does

This code creates a **persistent habit-tracking assistant** that can remember habits across multiple sessions. Unlike the store agent (which uses in-memory storage), this agent saves data to a **SQLite database**, so your habits persist even after you close the program.

## How It Works (Step by Step)

### 1. Setting up Persistent Storage (lines 17-19)
- Uses `DatabaseSessionService` instead of `InMemorySessionService`
- Stores data in a SQLite database file: `habit_data.db`
- Defines the app name and user ID for the session

### 2. Creating Tools for the Agent (lines 24-144)

The agent has three tools it can use:

#### **`add_habit(habit: str)`** (lines 24-67)
- Adds a new habit to the user's list
- Updates the session state with the new habit
- Persists the change to the database using events
- Prints confirmation and shows updated habit list

#### **`view_habits()`** (lines 70-88)
- Shows all current habits in a numbered list
- Reads from the session state
- Returns a message confirming the action

#### **`delete_habit(index: int)`** (lines 91-144)
- Removes a habit by its position (1-based index)
- Validates the index before deleting
- Updates the session state and persists to database
- Shows updated habit list after deletion

**Key Feature**: Each tool has two ways to work:
- **Preferred way**: Uses `tool_context.state` (the proper ADK way)
- **Fallback way**: Manually gets the session and creates events to persist changes

### 3. Creating the Agent (lines 147-166)
- Creates an agent named "habit_agent"
- Gives it instructions on when to use each tool:
  - "add X" → calls `add_habit("X")`
  - "view" → calls `view_habits()`
  - "delete N" → calls `delete_habit(N)`
- Provides access to all three tools
- Shows the agent the current state (user name and habits list)

### 4. Setting up the Session (lines 169-183)
- Creates a `DatabaseSessionService` connected to the SQLite database
- Defines initial state: `{"user_name": "Bob", "habits": []}`
- **Smart session handling**:
  - Checks if a session already exists for this user
  - If yes: continues with the existing session (preserves your habits!)
  - If no: creates a new session with empty habits

### 5. Creating the Runner (line 186)
- Sets up a runner to execute the agent
- Connects it to the database session service

### 6. Interactive Chat Loop (lines 198-222)
- Creates an async function `ask_agent()` that:
  - Takes user input as text
  - Sends it to the agent
  - Prints the agent's response
- Creates a `main()` function that:
  - Runs an infinite loop
  - Prompts for user input
  - Calls the agent with each message
  - Allows typing "quit" or "exit" to end the session
  - Saves the session before exiting

### 7. Running the Program (line 225)
- Uses `asyncio.run()` to start the async main function
- Begins the interactive chat loop

## Key Concepts

### **Persistent Storage**
- Data is saved to a SQLite database file (`habit_data.db`)
- Your habits persist between program runs
- If you run the program again, it will find your existing session and continue where you left off

### **State Management with Events**
- When tools modify state, they create `Event` objects
- Events contain `state_delta` (the changes to make)
- Events are appended to the session to persist changes
- This ensures all changes are saved to the database

### **Tool Context**
- Tools receive a `tool_context` parameter
- This provides access to the current session state
- Tools can read and modify state directly through `tool_context.state`
- This is the preferred way, but the code also has fallback logic

## Example Usage Flow

1. **First Run:**
   ```
   You: add exercise
   Assistant: Added habit: exercise
   [Habits]
     1. exercise
   ```

2. **Add More Habits:**
   ```
   You: add reading
   Assistant: Added habit: reading
   [Habits]
     1. exercise
     2. reading
   ```

3. **View Habits:**
   ```
   You: view
   Assistant: Here are your current habits
   [Habits]
     1. exercise
     2. reading
   ```

4. **Delete a Habit:**
   ```
   You: delete 1
   Assistant: Deleted habit 1: exercise
   [Habits]
     1. reading
   ```

5. **Close and Reopen:**
   - Type "quit" to exit
   - Run the program again
   - It will find your existing session and show your remaining habits!

## Differences from Store Agent

| Feature | Store Agent | Persistence Agent |
|---------|-------------|-------------------|
| Storage | In-memory (temporary) | SQLite database (permanent) |
| Session | Single use | Resumes existing sessions |
| Interaction | One-shot execution | Interactive chat loop |
| Tools | None (uses structured output) | Three tools (add/view/delete) |
| State Updates | Manual application | Automatic via tool context |

## Technical Details

- **Async/Await**: Uses async functions for better efficiency when handling multiple requests
- **Event System**: Uses Google ADK's event system to track and persist state changes
- **Session Management**: Automatically handles session creation and resumption
- **Error Handling**: Validates habit indices before deletion to prevent errors

