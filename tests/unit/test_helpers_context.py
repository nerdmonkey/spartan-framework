import json

from app.helpers.context import (
    MockCloudEvent,
    MockCloudFunctionsContext,
    MockCloudRunContext,
)


def test_mock_cloud_functions_context_attributes():
    ctx = MockCloudFunctionsContext()
    assert ctx.event_id == "mock_event_id_123456"
    assert ctx.event_type == "google.cloud.pubsub.topic.v1.messagePublished"
    assert ctx.timestamp is not None
    assert ctx.resource == "projects/mock-project/topics/mock-topic"
    assert ctx.request_id == "mock_request_id_abc123"


def test_mock_cloud_run_context_attributes():
    ctx = MockCloudRunContext()
    assert ctx.request_id == "mock_request_id_xyz789"
    assert ctx.service == "mock-cloud-run-service"
    assert ctx.revision == "mock-cloud-run-service-00001-abc"


def test_mock_cloud_event_to_dict_and_json():
    event = MockCloudEvent()
    d = event.to_dict()
    assert d["specversion"] == "1.0"
    assert d["type"] == "google.cloud.pubsub.topic.v1.messagePublished"
    assert d["source"].startswith("//pubsub.googleapis.com")
    assert d["id"] == "mock_event_id_123456"
    assert "data" in d
    assert "message" in d["data"]

    j = event.to_json()
    parsed = json.loads(j)
    assert parsed["type"] == "google.cloud.pubsub.topic.v1.messagePublished"
