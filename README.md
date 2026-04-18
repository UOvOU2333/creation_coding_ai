# creation_coding_ai

## Role Track
AI/LLM

## Tech Stack
- Language: Python 3.10+
- Framework: Streamlit
- AI Framework: LangChain / LangChain Classic
- LLM Provider: OpenAI-compatible API (`deepseek-chat` model)
- Database: SQLite
- UI Library: streamlit-antd-components
- Env management: python-dotenv

## Features Implemented
- Streamlit-based task management dashboard with a homepage and task management page
- Task CRUD (create, read, update, delete) for tasks, types, and states
- SQLite persistence with schema initialization in `data/db_init.py`
- Task filtering and sorting by type, state, priority, and keyword
- Task overview for today and next 5 days
- AI assistant powered by LangChain agent for natural language task operations
- Tool-based agent actions: `add_task`, `search_task`, `update_task`, `add_type`, `update_type`, `search_type`, `search_state`, `update_state`
- Color-coded task type and state labels with preset color management
- Agent execution trace display for debugging and transparency

## Overview
`creation_coding_ai` is an intelligent task management workspace that combines a Streamlit UI with an LLM-powered agent. Users can manage tasks and task metadata through the UI, while also using natural language prompts to create, query, and update tasks.

The AI assistant is designed to follow a strict tool contract: it may only use available tool functions and cannot invent unsupported operations.

> Development note: this project was developed with the assistance of AI tools, including GitHub Copilot and an LLM-based coding assistant, to help structure the implementation and documentation.

## Setup Instructions
1. Prerequisites
   - Python 3.10 or later
   - `OPENAI_API_KEY` for the OpenAI-compatible endpoint
   - Optional: `OPENAI_API_BASE` if using a custom API base URL

2. Install dependencies
   ```bash
   pip install streamlit streamlit-antd-components langchain-openai langchain-classic langchain-core python-dotenv
   ```

3. Initialize the database
   ```bash
   python data/db_init.py
   ```

4. Create a `.env` file in the project root with:
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_API_BASE=https://api.openai.com/v1
   ```
   - `OPENAI_API_BASE` is optional if the default provider endpoint is used.

5. Run the application
   ```bash
   streamlit run app.py
   ```

## Application Structure
```
app.py
config.py
README.md
requirements.txt
chains/
  agent.py
  loger.py
  prompt.py
data/
  db_init.py
pages/
  managingPage.py
  subPages/
    tasks/
      createTask.py
      showTasks.py
      updateTask.py
    tags/
      statesManage.py
      typesManage.py
    widgets/
      agent.py
      capsule.py
      navbar.py
      presetColor.py
services/
  preset_color_service.py
  state_service.py
  task_service.py
  type_service.py
tools/
  add_task.py
  add_type.py
  delete_task.py
  search_state.py
  search_task.py
  search_type.py
  update_state.py
  update_task.py
  update_type.py
```

## How the AI Assistant Works
The AI assistant is built with LangChain's tool-calling agent pattern.
- `chains/agent.py` constructs a `ChatOpenAI` LLM with the `deepseek-chat` model.
- `chains/prompt.py` contains the system prompt and business rules.
- The assistant only has access to the supported tools defined in `tools/`.
- The UI in `pages/subPages/widgets/agent.py` exposes a chat interface and shows tool execution steps.

### Supported natural language operations
- Create tasks with natural language instructions
- Query tasks by name, type, state, and priority
- Update task fields by ID
- Manage task types and states through the agent

### Tool set available to the agent
- `add_task`
- `add_type`
- `update_task`
- `search_task`
- `search_type`
- `search_state`
- `update_state`

## Implementation Details
### Task model
Each task supports:
- `task_name`
- `type_id` / `type_name`
- `state_id` / `state_name`
- `scheduled_start`
- `scheduled_end`
- `priority` (0-10)
- `is_archived`
- `created_at`

### Database
- SQLite file stored at `data/database.db`
- Seeded tables for `task_state`, `task_type`, and `preset_colors`
- Default type `未设置` and default states created by `data/db_init.py`

### UI features
- Homepage with today’s task summary and 5-day schedule overview
- Task management page with:
  - Create task form
  - Update/Delete task form
  - Full task list with filtering, sorting, and keyword search
  - Type and state CRUD management
- Color preview and preset color management for labels

## Limitations
- No external REST API endpoints are provided; the application is frontend/UI-driven.
- Natural language parsing is handled by the agent prompt and available tools, not by a standalone date parser.
- No user authentication or multi-user support.
- There is no vector database or semantic search backend.
- `requirements.txt` is currently empty and dependencies are listed in this README.

## Challenges & Solutions
- Challenge: Recovering task metadata and UI state from a Streamlit session while supporting agent-driven operations.
  - Solution: Stored chat history and agent intermediate steps in `st.session_state`.
- Challenge: Ensuring tool-based LLM actions remain safe and traceable.
  - Solution: Limited the agent to explicit LangChain tool functions and surfaced tool calls in the UI.
- Challenge: Managing task type and state consistency across both direct UI management and agent operations.
  - Solution: Centralized task type/state lookup and validation in service layers and tool wrappers.

## Future Improvements
- Add REST API endpoints for task CRUD and agent interaction
- Implement semantic search or embeddings-based task retrieval
- Improve natural language date parsing and due-date extraction
- Add user accounts and authentication
- Add unit/integration tests and CI workflow
- Add Dockerfile / docker-compose for reproducible deployment
- Add task dependency tracking and completion constraints

## Time Spent
Approximately 3-4 hours
