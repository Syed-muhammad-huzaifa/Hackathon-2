"""
Main CLI entry point for the todo app.
"""
import sys
from typing import Optional
from src.storage.json_store import JSONStore
from src.services.task_service import TaskService


def main():
    """
    Main entry point for the CLI application.
    """
    # Initialize storage and service
    store = JSONStore("tasks.json")
    service = TaskService(store)

    if len(sys.argv) < 2:
        show_menu(service)
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: todo add <title> [description]")
            return

        title = sys.argv[2]
        description = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""

        try:
            task_id = service.add_task(title, description)
            print(f"Task added successfully with ID: {task_id}")
        except ValueError as e:
            print(f"Error: {e}")
    elif command == "list":
        tasks = service.view_tasks()
        if not tasks:
            print("No tasks found.")
        else:
            for task in tasks:
                status_indicator = "✓" if task.status == "completed" else "○"
                print(f"[{status_indicator}] ID: {task.id}, Title: {task.title}")
                if task.description:
                    print(f"    Description: {task.description}")
    elif command == "complete":
        if len(sys.argv) < 3:
            print("Usage: todo complete <task_id>")
            return

        try:
            task_id = int(sys.argv[2])
            success = service.toggle_task_status(task_id)
            if success:
                print(f"Task {task_id} marked as completed.")
            else:
                print(f"Task {task_id} not found.")
        except ValueError:
            print("Task ID must be a number.")
    elif command == "incomplete":
        if len(sys.argv) < 3:
            print("Usage: todo incomplete <task_id>")
            return

        try:
            task_id = int(sys.argv[2])
            success = service.toggle_task_status(task_id)
            if success:
                print(f"Task {task_id} marked as incomplete.")
            else:
                print(f"Task {task_id} not found.")
        except ValueError:
            print("Task ID must be a number.")
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: todo delete <task_id>")
            return

        try:
            task_id = int(sys.argv[2])
            success = service.delete_task(task_id)
            if success:
                print(f"Task {task_id} deleted successfully.")
            else:
                print(f"Task {task_id} not found.")
        except ValueError:
            print("Task ID must be a number.")
    elif command == "update":
        if len(sys.argv) < 4:
            print("Usage: todo update <task_id> <title> [description]")
            return

        try:
            task_id = int(sys.argv[2])
            title = sys.argv[3]
            description = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""

            success = service.update_task(task_id, title, description)
            if success:
                print(f"Task {task_id} updated successfully.")
            else:
                print(f"Task {task_id} not found.")
        except ValueError:
            print("Task ID must be a number.")
    elif command == "help" or command == "--help":
        show_menu(service)
    else:
        print(f"Unknown command: {command}")
        show_menu(service)


def show_menu(service):
    """
    Display the help menu with available commands.
    """
    print("Todo CLI App - Available Commands:")
    print("  todo add <title> [description]     - Add a new task")
    print("  todo list                          - List all tasks")
    print("  todo complete <task_id>            - Mark task as complete")
    print("  todo incomplete <task_id>          - Mark task as incomplete")
    print("  todo delete <task_id>              - Delete a task")
    print("  todo update <task_id> <title> [desc] - Update a task")
    print("  todo help                          - Show this help message")


if __name__ == "__main__":
    main()
