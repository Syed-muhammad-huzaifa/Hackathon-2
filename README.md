# AI-DRIVEN-DEVELOPMENT Hackathon-2 - Todo CLI App

This project contains a simple command-line todo application built with Python 3.13+. The application allows you to manage tasks from the command line with features like adding, listing, completing, updating, and deleting tasks.

## Project Structure

```
Hackathon-2/
├── CLAUDE.md              # Claude Code Rules and project instructions
├── README.md              # This file
├── specs/                 # Feature specifications and plans
├── history/               # Prompt History Records and ADRs
├── .specify/              # SpecKit Plus templates and scripts
└── todo-cli/              # Main todo CLI application
    ├── README.md          # Detailed documentation for the todo app
    ├── main.py            # Entry point
    ├── pyproject.toml     # Project configuration
    ├── src/               # Source code
    │   ├── cli/           # Command-line interface
    │   ├── models/        # Data models
    │   ├── services/      # Business logic
    │   └── storage/       # Data storage
    └── tests/             # Test files
```

## Prerequisites

- Python 3.13+
- UV package manager (recommended) or pip

## Installation and Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd AI-DRIVEN-DEVELOPMENT/Hackathon-2
   ```

2. **Navigate to the todo-cli directory**:
   ```bash
   cd todo-cli
   ```

3. **Install UV package manager** (if not already installed):
   ```bash
   # On macOS/Linux:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows:
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

4. **Install dependencies using UV**:
   ```bash
   uv sync
   ```

## How to Run the Project

### Method 1: Using UV (Recommended)
Run the application directly without installation:
```bash
uv run python -m src.cli.main [command]
```

For convenience, you can also run:
```bash
uv run src.cli.main [command]
```

### Method 2: Install and Run as a Command
1. **Build and install the package**:
   ```bash
   uv build
   uv pip install .
   ```

2. **Run the application**:
   ```bash
   todo [command]
   ```

### Method 3: Direct Python Execution
```bash
python -m src.cli.main [command]
```

## Available Commands

- `todo add <title> [description]` - Add a new task
- `todo list` - List all tasks
- `todo complete <task_id>` - Mark task as complete
- `todo incomplete <task_id>` - Mark task as incomplete
- `todo delete <task_id>` - Delete a task
- `todo update <task_id> <title> [description]` - Update a task
- `todo help` - Show help message

## Examples

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

## Development

### Running Tests

To run the tests:
```bash
cd todo-cli
uv run pytest
```

### Development Workflow

1. Make your changes to the source code in the `src/` directory
2. Run tests to ensure everything works:
   ```bash
   uv run pytest
   ```
3. Run the application to test your changes:
   ```bash
   uv run python -m src.cli.main [command]
   ```

## Architecture

The application follows a layered architecture:

- **Models**: Define the data structures (Task)
- **Storage**: Handle data persistence (JSONStore)
- **Services**: Implement business logic (TaskService)
- **CLI**: Handle user interaction (main.py)

## Project Configuration

The project uses:
- Python 3.13+ (as specified in pyproject.toml)
- UV for package management
- JSON file for data persistence
- Standard library only (no external dependencies)

## Troubleshooting

If you encounter issues:

1. **Module not found errors**: Ensure you're running from the `todo-cli` directory
2. **Permission errors**: Make sure you have proper permissions to install packages
3. **Python version issues**: Verify you're using Python 3.13+

For more detailed information about the todo application, see the README.md file in the `todo-cli/` directory.
