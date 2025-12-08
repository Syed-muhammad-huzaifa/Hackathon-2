# Todo CLI App

A simple command-line todo application with in-memory storage.

## Features

- Add new tasks with titles and optional descriptions
- List all tasks with status indicators
- Mark tasks as complete/incomplete
- Update task titles and descriptions
- Delete tasks
- All data stored in memory (lost on exit)

## Prerequisites

- Python 3.13+
- UV package manager

## Installation

1. Clone the repository
2. Navigate to the project directory
3. Install dependencies:

```bash
uv sync
```

## Usage

Run the application using:

```bash
uv run python -m src.cli.main [command]
```

Or install and run as a command:

```bash
uv build
uv pip install .
todo [command]
```

### Available Commands

- `todo add <title> [description]` - Add a new task
- `todo list` - List all tasks
- `todo complete <task_id>` - Mark task as complete
- `todo incomplete <task_id>` - Mark task as incomplete
- `todo delete <task_id>` - Delete a task
- `todo update <task_id> <title> [description]` - Update a task
- `todo help` - Show help message

### Examples

```bash
# Add a task
todo add "Buy groceries" "Milk, bread, eggs"

# List all tasks
todo list

# Mark task #1 as complete
todo complete 1

# Update task #1
todo update 1 "Buy weekly groceries" "Milk, bread, eggs, fruits"

# Delete task #1
todo delete 1
```

## Project Structure

```
src/
    models/           # Data models
        task.py       # Task model
    services/         # Business logic
        task_service.py # Task operations
    storage/          # Data storage
        in_memory_store.py # In-memory storage
    cli/              # Command-line interface
        main.py       # Main CLI entry point
```

## Architecture

The application follows a layered architecture:

- **Models**: Define the data structures (Task)
- **Storage**: Handle data persistence (InMemoryStore)
- **Services**: Implement business logic (TaskService)
- **CLI**: Handle user interaction (main.py)
