# README: Autonomous Life Assistant Agent

## Overview
This project implements an autonomous life assistant agent that continuously loops, reasons, and acts to help the user achieve their goals. The agent uses Ollama (API at http://umbrel.local:11434, model: tinyllama) for LLM reasoning, and follows a structured deployment methodology defined in `deployment_plan.md`.

## Features
- Infinite reasoning and action loop
- Reads and modifies `plan.md`, `tasks.md`, `cron.md`
- Accepts human overrides via `human_input.md`
- Persists knowledge in `memory.json`
- Executes structured Python functions
- Automatically edits markdown files
- Reflects and logs thoughts after each cycle
- Logs all changes to `change_log.md`
- Follows `deployment_plan.md` as a reference guide

## File Structure
- `loop.py`: Main execution loop
- `thinker.py`: LLM prompt/response handler
- `editor.py`: Markdown file editor
- `functions.py`: Callable functions (reminders, web search, etc.)
- `function_executor.py`: Executes model-suggested actions
- `utils.py`: Helper utilities
- `plan.md`, `tasks.md`, `cron.md`, `deployment_plan.md`: Project logic and routines
- `human_input.md`: Human overrides
- `memory.json`: Persistent memory
- `change_log.md`: Change log
- `self_review.md`: Agent's self-reflection

## Setup
1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install requests markdown
   ```
3. Ensure Ollama is running and accessible at `http://umbrel.local:11434` with the `tinyllama` model.

## Usage
Run the main loop:
```bash
python loop.py
```
To run as a module (recommended due to subfolder structure):
```bash
python -m src.loop
```

## Architecture
- The agent loops, consulting `deployment_plan.md` at each cycle.
- Uses `thinker.py` to reason and plan actions.
- Executes actions via `function_executor.py` and `functions.py`.
- Edits markdown files with `editor.py`.
- Logs all changes and self-reflections.
- Accepts human input at any time via `human_input.md`.

---
For more details, see `deployment_plan.md` and `plan.md`.
