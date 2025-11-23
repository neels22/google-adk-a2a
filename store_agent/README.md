# Store Agent Explanation

## What This Code Does

This code demonstrates how to create an AI agent that can **remember and update user information** using structured outputs. The agent stores information about a user (their name, favorite color, and favorite subject) and can update these values when asked.

## How It Works (Step by Step)

### 1. Setting up the Data Structure (lines 12-15)
- Defines a Pydantic schema called `StateOutput` with three fields:
  - `fav_color`: The user's favorite color
  - `name`: The user's name
  - `fav_subject`: The user's favorite subject
- This schema ensures the agent always returns data in a consistent format

### 2. Creating the Agent (lines 18-43)
- Creates an agent named "InformationAgent" that:
  - Knows the current state (name, favorite color, favorite subject)
  - Can update the state when the user asks (returns JSON with new values)
  - Answers questions in plain text otherwise
- Uses `output_schema=StateOutput` to enforce structured output
- Uses `output_key="state"` to specify where the structured output will be stored

### 3. Setting up Storage (lines 46-59)
- Creates an in-memory session service to store state
- Creates a new session with initial values:
  - Name: "Vaibhav"
  - Favorite color: "green"
  - Favorite subject: "Mathematics"

### 4. Running the Agent (lines 62-81)
- Creates a runner to execute the agent
- Sends a user message: "Please change my favorite color to red and my favourite subject to Computer Science."
- The agent processes this request and returns structured output
- Prints the raw response from the agent

### 5. Updating the Stored State (lines 84-103)
- Retrieves the session after the agent runs
- Checks if structured output exists under the "state" key
- If found, applies the updates to the session state:
  - Updates only the fields that changed
  - Preserves existing values for fields that weren't mentioned
- Removes the temporary "state" key to clean up

### 6. Showing the Result (lines 106-108)
- Prints the final session state to confirm the updates were applied correctly

## The Key Concept

**Structured Outputs**: Instead of just returning free-form text, the agent can return structured data (JSON) that matches a specific schema. This makes it easy for the code to automatically update stored information when the user requests changes, without having to parse natural language responses.

## Example Flow

**Initial State:**
- `name`: "Vaibhav"
- `fav_color`: "green"
- `fav_subject`: "Mathematics"

**User Request:**
"Please change my favorite color to red and my favourite subject to Computer Science."

**Final State:**
- `name`: "Vaibhav" (unchanged)
- `fav_color`: "red" (updated)
- `fav_subject`: "Computer Science" (updated)

The code automatically handles the update using the structured output from the agent!

