# SaveKit

**SaveKit** is a lightweight and easy-to-use key-value storage toolkit that uses JSON files for persistent local storage.  
Perfect for saving configurations, user preferences, flags, or simple application state in any Python project.

## Features

- ✅ Simple key-value storage using JSON
- 🐍 Pure Python, no external dependencies
- 💾 Data persists between runs
- 🔄 Lazy loading (file is read only when accessed)
- 🧪 Tested and ready for integration

## Installation

```bash
pip install savekit
```

## Usage

```python
from savekit import SaveKit

# Initialize the store
db = SaveKit()

# Set a value
db.set_item("theme", "dark")

# Get a value
print(db.get_item("theme"))  # Output: dark

# Get with default fallback
print(db.get_item("language", default="en"))

# Delete a value
db.delete_item("theme")

# Get all stored data
print(db.get_all_items())  # Output: {}

# Clear all data
db.clear_store()

# Export to another file
db.export_store("backup.json")

# Import from a file
db.import_store("backup.json")

# Reload from file (discard in-memory changes)
db.reload_store()
```

## License

This project is licensed under the MIT License.
