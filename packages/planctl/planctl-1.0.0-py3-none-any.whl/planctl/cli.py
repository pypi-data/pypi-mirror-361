#!/usr/bin/env python3
"""
PlanCtl - A CLI tool for managing daily engineering tasks and priorities
"""

import json
import os
import typer
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="PlanCtl - Manage daily engineering tasks and priorities")
console = Console()

class PlanCtl:
    def __init__(self, data_file: str = "planctl_data.json"):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file or create empty structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "todos": [],
            "parking_lots": [],
            "archived_todos": []
        }

    def save_data(self) -> None:
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_todo(self, description: str, side_initiative: bool = False, priority: int = 2) -> None:
        """Add a new todo item"""
        todo = {
            "id": len(self.data["todos"]) + 1,
            "description": description,
            "done": False,
            "side_initiative": side_initiative,
            "priority": priority,
            "created_at": datetime.now().isoformat()
        }
        self.data["todos"].append(todo)
        self.save_data()
        initiative_type = "side-initiative" if side_initiative else "todo"
        console.print(f"✓ Added {initiative_type} with priority {priority}: {description}", style="green")

    def mark_todo_done(self, todo_id: int) -> None:
        """Mark a todo as done"""
        for todo in self.data["todos"]:
            if todo["id"] == todo_id:
                todo["done"] = True
                todo["completed_at"] = datetime.now().isoformat()
                self.save_data()
                console.print(f"✓ Marked todo {todo_id} as done: {todo['description']}", style="green")
                return
        console.print(f"✗ Todo {todo_id} not found", style="red")

    def mark_todo_undone(self, todo_id: int) -> None:
        """Mark a todo as undone"""
        for todo in self.data["todos"]:
            if todo["id"] == todo_id:
                todo["done"] = False
                if "completed_at" in todo:
                    del todo["completed_at"]
                self.save_data()
                console.print(f"✓ Marked todo {todo_id} as undone: {todo['description']}", style="green")
                return
        console.print(f"✗ Todo {todo_id} not found", style="red")

    def list_todos(self) -> None:
        """List all todos"""
        if not self.data["todos"]:
            console.print("No todos found", style="yellow")
            return

        table = Table(title="📋 Todos")
        table.add_column("ID", style="cyan")
        table.add_column("Priority", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Type", style="blue")
        table.add_column("Description", style="white")

        sorted_todos = sorted(self.data["todos"], key=lambda x: x.get("priority", 2))

        for todo in sorted_todos:
            status = "✅ Done" if todo["done"] else "⏳ Pending"
            todo_type = "🔄 Side" if todo.get("side_initiative", False) else "📝 Main"
            priority = str(todo.get("priority", 2))
            table.add_row(str(todo["id"]), priority, status, todo_type, todo["description"])

        console.print(table)

    def add_parking_lot(self, description: str) -> None:
        """Add a new parking lot item"""
        parking_lot = {
            "id": len(self.data["parking_lots"]) + 1,
            "description": description,
            "resolved": False,
            "created_at": datetime.now().isoformat()
        }
        self.data["parking_lots"].append(parking_lot)
        self.save_data()
        console.print(f"✓ Added to parking lot: {description}", style="green")

    def list_parking_lots(self) -> None:
        """List all parking lot items"""
        active_parking = [p for p in self.data["parking_lots"] if not p.get("resolved", False)]
        if not active_parking:
            console.print("No parking lot items found", style="yellow")
            return

        table = Table(title="🅿️ Parking Lot")
        table.add_column("ID", style="cyan")
        table.add_column("Description", style="white")

        for item in active_parking:
            table.add_row(str(item["id"]), item["description"])

        console.print(table)

    def generate_standup_report(self) -> None:
        """Generate a standup report"""
        console.print("\n📊 Daily Report", style="bold blue")
        console.print("=" * 50, style="blue")

        completed_todos = [t for t in self.data["todos"] if t["done"]]
        if completed_todos:
            completed_todos = sorted(completed_todos, key=lambda x: x.get("priority", 2))
            console.print("\n✅ Completed:", style="bold green")
            for todo in completed_todos:
                side_indicator = " (side-initiative)" if todo.get("side_initiative", False) else ""
                priority_indicator = f" [P{todo.get('priority', 2)}]"
                console.print(f"  • {todo['description']}{side_indicator}{priority_indicator}")

        pending_main_todos = [t for t in self.data["todos"] if not t["done"] and not t.get("side_initiative", False)]
        if pending_main_todos:
            pending_main_todos = sorted(pending_main_todos, key=lambda x: x.get("priority", 2))
            console.print("\n⏳ In Progress/Planned:", style="bold yellow")
            for todo in pending_main_todos:
                priority_indicator = f" [P{todo.get('priority', 2)}]"
                console.print(f"  • {todo['description']}{priority_indicator}")

        pending_side_todos = [t for t in self.data["todos"] if not t["done"] and t.get("side_initiative", False)]
        if pending_side_todos:
            pending_side_todos = sorted(pending_side_todos, key=lambda x: x.get("priority", 2))
            console.print("\n🔄 Side Initiatives:", style="bold cyan")
            for todo in pending_side_todos:
                priority_indicator = f" [P{todo.get('priority', 2)}]"
                console.print(f"  • {todo['description']}{priority_indicator}")

        active_parking = [p for p in self.data["parking_lots"] if not p.get("resolved", False)]
        if active_parking:
            console.print("\n🅿️ Parking Lot:", style="bold magenta")
            for item in active_parking:
                console.print(f"  • {item['description']}")

        if not completed_todos and not pending_main_todos and not pending_side_todos and not active_parking:
            console.print("\nNo items to report", style="yellow")

    def archive_completed_todos(self) -> None:
        """Archive all completed todos"""
        if "archived_todos" not in self.data:
            self.data["archived_todos"] = []

        completed_todos = [t for t in self.data["todos"] if t["done"]]
        if not completed_todos:
            console.print("No completed todos to archive", style="yellow")
            return

        for todo in completed_todos:
            todo["archived_at"] = datetime.now().isoformat()
            self.data["archived_todos"].append(todo)

        self.data["todos"] = [t for t in self.data["todos"] if not t["done"]]
        self.save_data()
        console.print(f"✓ Archived {len(completed_todos)} completed todos", style="green")

    def resolve_parking_lot(self, parking_id: int) -> None:
        """Mark a parking lot item as resolved"""
        for item in self.data["parking_lots"]:
            if item["id"] == parking_id:
                item["resolved"] = True
                item["resolved_at"] = datetime.now().isoformat()
                self.save_data()
                console.print(f"✓ Resolved parking lot item {parking_id}: {item['description']}", style="green")
                return
        console.print(f"✗ Parking lot item {parking_id} not found", style="red")

cli = PlanCtl()

@app.command()
def add_todo(
    description: str = typer.Argument(..., help="Todo description"),
    side_initiative: bool = typer.Option(False, "--side", "-s", help="Mark as side initiative"),
    priority: int = typer.Option(2, "--priority", "-p", help="Set priority (lower number = higher priority)")
):
    """Add a new todo item"""
    cli.add_todo(description, side_initiative, priority)

@app.command()
def done(todo_id: int = typer.Argument(..., help="Todo ID to mark as done")):
    """Mark a todo as done"""
    cli.mark_todo_done(todo_id)

@app.command()
def undone(todo_id: int = typer.Argument(..., help="Todo ID to mark as undone")):
    """Mark a todo as undone"""
    cli.mark_todo_undone(todo_id)

@app.command()
def list_todos():
    """List all todos"""
    cli.list_todos()

@app.command()
def add_parking(description: str = typer.Argument(..., help="Parking lot item description")):
    """Add an item to the parking lot"""
    cli.add_parking_lot(description)

@app.command()
def list_parking():
    """List all parking lot items"""
    cli.list_parking_lots()

@app.command()
def report():
    """Generate a daily report"""
    cli.generate_standup_report()

@app.command()
def archive():
    """Archive all completed todos"""
    cli.archive_completed_todos()

@app.command()
def resolve_parking(parking_id: int = typer.Argument(..., help="Parking lot ID to resolve")):
    """Mark a parking lot item as resolved"""
    cli.resolve_parking_lot(parking_id)

if __name__ == "__main__":
    app()
