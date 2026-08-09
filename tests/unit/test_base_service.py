import pytest

from app.services.base import BaseService


def test_base_service_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseService()


def test_base_service_subclass_must_implement_all_methods():
    class IncompleteService(BaseService):
        def get_by_id(self, id):
            return None

    with pytest.raises(TypeError):
        IncompleteService()


def test_base_service_subclass_with_all_methods_instantiates():
    class CompleteService(BaseService):
        def get_by_id(self, id):
            return {"id": id}

        def list(self, *args, **kwargs):
            return []

        def create(self, request):
            return request

        def update(self, id, request):
            return request

        def delete(self, id):
            return True

    service = CompleteService()
    assert service.get_by_id("1") == {"id": "1"}
    assert service.list() == []
    assert service.create({"a": 1}) == {"a": 1}
    assert service.update("1", {"a": 2}) == {"a": 2}
    assert service.delete("1") is True
