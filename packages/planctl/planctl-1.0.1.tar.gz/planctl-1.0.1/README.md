# PlanCtl

A CLI tool for managing daily engineering tasks and priorities. Perfect for organizing your day-to-day work, tracking progress, and keeping notes for standup meetings.

## Features

- **Task Management**: Add, complete, and track todos with support for side initiatives and priority levels
- **Parking Lot**: Keep track of items to discuss later or follow up on
- **Archive System**: Clean up completed tasks to keep reports focused
- **Daily Reports**: Generate organized reports of your work
- **Rich CLI Interface**: Beautiful, colorful command-line interface

## Installation

### From Source
```bash
git clone https://github.com/wilsongomes-swe/planctl.git
cd planctl
pip install -e .
```

### From PyPI
```bash
pip install planctl
```

## Usage

### Basic Commands

Add a task:
```bash
planctl add-todo "Fix authentication bug"
```

Add a task with priority (lower number = higher priority):
```bash
planctl add-todo "Critical security fix" --priority 0
```

Add a side initiative:
```bash
planctl add-todo "Research new framework" --side
```

Add a side initiative with priority:
```bash
planctl add-todo "Optimize database queries" --side --priority 1
```

Mark task as done:
```bash
planctl done 1
```

List all tasks (sorted by priority):
```bash
planctl list-todos
```

Add to parking lot:
```bash
planctl add-parking "Discuss API changes with team"
```

Generate daily report (todos sorted by priority):
```bash
planctl report
```

Archive completed tasks:
```bash
planctl archive
```

Resolve parking lot item:
```bash
planctl resolve-parking 1
```

### All Commands

| Command | Description |
|---------|-------------|
| `add-todo DESCRIPTION [--side] [--priority NUMBER]` | Add a new task (optionally mark as side initiative and set priority) |
| `done ID` | Mark task as completed |
| `undone ID` | Mark task as incomplete |
| `list-todos` | List all active tasks (sorted by priority) |
| `add-parking DESCRIPTION` | Add item to parking lot |
| `list-parking` | List parking lot items |
| `resolve-parking ID` | Mark parking lot item as resolved |
| `report` | Generate daily report (todos sorted by priority) |
| `archive` | Archive all completed tasks |

## Data Storage

PlanCtl stores data in `planctl_data.json` in your current working directory. This file contains:
- Active todos with completion status, side initiative flags, and priority levels
- Parking lot items with resolution status
- Archived completed tasks

## License

MIT License
