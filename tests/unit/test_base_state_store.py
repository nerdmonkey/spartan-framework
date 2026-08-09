import pytest

from app.services.state_store import BaseStateStore


def test_base_state_store_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseStateStore()


def test_base_state_store_subclass_must_implement_all_methods():
    class IncompleteStateStore(BaseStateStore):
        def set_state(self, key, value):
            return value

    with pytest.raises(TypeError):
        IncompleteStateStore()


def test_base_state_store_subclass_with_all_methods_instantiates():
    class InMemoryStateStore(BaseStateStore):
        def __init__(self):
            self._data = {}

        def set_state(self, key, value):
            self._data[key] = value
            return value

        def get_state(self, key):
            return self._data.get(key)

        def remove_state(self, key):
            return self._data.pop(key, None)

    store = InMemoryStateStore()
    assert store.set_state("k", {"a": 1}) == {"a": 1}
    assert store.get_state("k") == {"a": 1}
    assert store.remove_state("k") == {"a": 1}
    assert store.get_state("k") is None
