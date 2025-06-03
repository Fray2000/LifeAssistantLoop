# Life Assistant with Dual-Model Architecture

A sophisticated personal assistant system leveraging a dual-model architecture with:
- Llama3.2 for frontend user interaction
- Llama3.2 for backend task execution
- Bidirectional communication between components

## Key Features

- **Dual-Model Architecture**: Separates user interaction and task execution into independent components
- **Continuous Backend Loop**: The backend runs continuously to process tasks from the frontend
- **Bidirectional Communication**: Frontend and backend communicate through JSON message exchange
- **Memory Management**: Persistent memory shared between frontend and backend
- **Debug Mode**: Shows internal model interactions for transparency

## How It Works

1. The frontend component (`frontend_assistant.py`) handles direct user interactions
2. The frontend processes user input and creates structured directives
3. These directives are sent to the backend via a JSON message
4. The backend (`backend_loop.py`) monitors for requests and processes them
5. Results are sent back to the frontend
6. The frontend presents the results to the user in a friendly way

## Split Memory Architecture

The system uses a dual-model architecture with split memory:

- **Frontend Memory** (data-user/memory.json): 
  - Stores user-facing information, preferences, and conversation history
  - Only accessible by the frontend component
  - Optimized for user interaction

- **Backend Memory** (data-backend/backend_memory.json):
  - Stores backend processing state, task queues, and execution history
  - Only accessible by the backend component
  - Optimized for task execution

- **Communication Buffer** (src/task_buffer.json):
  - Facilitates task transfer between frontend and backend
  - Frontend adds tasks for background processing
  - Backend processes tasks from this buffer

### Memory Flow

```
┌───────────────────┐     ┌────────────────┐
│   User Interface  │     │  Task Buffer   │
│  (frontend.py)    │◄───►│ (JSON)         │◄─────┐
└───────────────┬───┘     └────────────────┘      │
                │                                 │
                ▼                                 ▼
┌───────────────────┐     ┌────────────────┐     ┌───────────────────┐
│  User Memory      │     │ Communication  │     │  Backend Memory   │
│  (data-user/)     │     │ Files (src/)   │     │  (data-backend/)  │
└───────────────────┘     └────────────────┘     └───────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running with Llama3.2 model available

### Installation

1. Initialize the memory system:
```
python init_simple_memory.py
```

2. Start both frontend and backend:
```
python start_assistant.py
```

For debug mode (to see internal model interactions):
```
python start_assistant.py --debug
```

### Manual Start (Advanced)

You can start the components individually:

1. Start the backend:
```
python backend_loop.py
```

2. Start the frontend in a different terminal:
```
python frontend_assistant.py
```

## Components

- **frontend_assistant.py**: Handles user interaction
- **backend_loop.py**: Processes tasks and executes actions
- **user_interaction_model.py**: Frontend model logic
- **task_execution_model.py**: Backend model logic
- **memory_manager.py**: Manages shared memory
- **function_executor.py**: Executes actions on the system

## Available Directives

- `add_task`: Add a task to your list
- `complete_task`: Mark a task as complete
- `list_tasks`: Show your current tasks
- `remember`: Store information in memory
- `search_info`: Search for information
- `help`: Get assistance with using the system

## Communication Protocol

The frontend and backend communicate through JSON messages with the following structure:

### Request Format
```json
{
  "id": "request_id",
  "type": "command|query|task",
  "content": {/* directive object */},
  "timestamp": "ISO datetime",
  "response_required": true
}
```

### Response Format
```json
{
  "id": "request_id",
  "status": "success|error",
  "content": "execution results",
  "actions": [/* list of executed actions */],
  "timestamp": "ISO datetime"
}
```

## Debug Mode

Type `debug on` in the frontend to see internal model interactions and communication.
Type `debug off` to hide them again.
