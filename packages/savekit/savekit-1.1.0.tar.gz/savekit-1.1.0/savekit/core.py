import json
import os
from typing import Any, Optional


class SaveKit:
    """
    SaveKit: A lightweight persistent key-value storage system using JSON files.

    This class provides simple methods to store, retrieve, update, delete, export,
    and import key-value pairs using a local JSON file. Ideal for storing configuration
    settings, user preferences, session flags, or temporary cache data.

    Lazy loading is supported: the file is only read when data is first accessed.

    Attributes:
        filename (str): Path to the JSON file used for storage.
        _data (dict): In-memory dictionary loaded from the JSON file.
    """

    def __init__(self, filename: str = 'savekit.json'):
        """
        Initializes a SaveKit instance with the specified JSON file.

        Args:
            filename (str): Name or path of the JSON file to use.
                            Defaults to 'savekit.json'.
        """
        self.filename = filename
        self._data = None

    @property
    def data(self) -> dict:
        """
        Loads and returns the in-memory data from the JSON file (if not already loaded).

        Returns:
            dict: Dictionary containing all key-value pairs.
        """
        if self._data is None:
            self._data = self._load_data()
        return self._data

    def _load_data(self) -> dict:
        """
        Reads the JSON file and loads its contents into memory.

        Returns:
            dict: Parsed dictionary from the file.

        If the file does not exist or is corrupted, a new empty file is created.
        """
        if not os.path.exists(self.filename):
            self._create_empty_file()
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._create_empty_file()
            return {}

    def _create_empty_file(self):
        """
        Creates a new empty JSON file with an empty dictionary structure.
        """
        with open(self.filename, 'w') as f:
            json.dump({}, f, indent=4)

    def _save(self):
        """
        Writes the current in-memory data back to the JSON file.
        """
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def set_item(self, key: str, value: Any):
        """
        Adds or updates a key-value pair in the storage.

        Args:
            key (str): Unique key identifier.
            value (Any): The value to store (must be JSON-serializable).
        """
        self.data[key] = value
        self._save()

    def get_item(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves the value associated with a given key.

        Args:
            key (str): The key to retrieve.
            default (Any, optional): The default value to return if key is not found.

        Returns:
            Any: The stored value or the default.
        """
        return self.data.get(key, default)

    def delete_item(self, key: str):
        """
        Deletes a key-value pair from storage if it exists.

        Args:
            key (str): The key to delete.
        """
        if key in self.data:
            del self.data[key]
            self._save()

    def get_all_items(self) -> dict:
        """
        Returns all stored key-value pairs.

        Returns:
            dict: The entire dictionary of stored data.
        """
        return self.data

    def clear_store(self):
        """
        Clears all data and resets the JSON file to an empty state.
        """
        self._data = {}
        self._save()

    def export_store(self, export_path: str):
        """
        Exports the current data to another JSON file (for backup or sharing).

        Args:
            export_path (str): Path to the destination export file.
        """
        with open(export_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def import_store(self, import_path: str):
        """
        Imports data from another JSON file, replacing the current content.

        Args:
            import_path (str): Path to the JSON file to import from.
        """
        with open(import_path, 'r') as f:
            self._data = json.load(f)
        self._save()

    def reload_store(self):
        """
        Reloads data from the JSON file, discarding any unsaved in-memory changes.
        """
        self._data = self._load_data()
