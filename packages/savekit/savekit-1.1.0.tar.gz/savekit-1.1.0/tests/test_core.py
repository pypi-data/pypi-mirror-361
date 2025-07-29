import os
import pytest
from savekit import SaveKit

TEST_FILE = "test_savekit.json"

@pytest.fixture
def store():
    # Create instance using test file
    kit = SaveKit(TEST_FILE)
    # Clear data before each test
    kit.clear_store()
    yield kit
    # Delete file after each test
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_set_and_get_item(store):
    store.set_item("key1", "value1")
    assert store.get_item("key1") == "value1"

def test_get_item_with_default(store):
    assert store.get_item("nonexistent", default=42) == 42

def test_delete_item(store):
    store.set_item("key2", 100)
    store.delete_item("key2")
    assert store.get_item("key2") is None

def test_get_all_items(store):
    store.set_item("k1", 1)
    store.set_item("k2", 2)
    all_data = store.get_all_items()
    assert isinstance(all_data, dict)
    assert all_data == {"k1": 1, "k2": 2}

def test_clear_store(store):
    store.set_item("temp", "data")
    store.clear_store()
    assert store.get_all_items() == {}

def test_reload_store(store):
    store.set_item("reload_test", "initial")
    # Modify file directly to simulate external change
    with open(TEST_FILE, "w") as f:
        f.write('{"reload_test": "changed"}')
    store.reload_store()
    assert store.get_item("reload_test") == "changed"
