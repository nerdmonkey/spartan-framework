import json
from datetime import datetime, timezone


class MockCloudFunctionsContext:
    """
    Mock implementation of the GCP Cloud Functions context object.

    Attributes:
        event_id (str): The unique ID of the event that triggered the function.
        event_type (str): The type of event that triggered the function.
        timestamp (str): Event timestamp (ISO 8601 format).
        resource (str): The resource that triggered the function.
        request_id (str): The unique request ID for this function invocation.
    """

    def __init__(self):
        self.event_id = "mock_event_id_123456"
        self.event_type = "google.cloud.pubsub.topic.v1.messagePublished"
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.resource = "projects/mock-project/topics/mock-topic"
        self.request_id = "mock_request_id_abc123"


class MockCloudRunContext:
    """
    MockCloudRunContext is a mock implementation of the GCP Cloud Run context object.

    Attributes:
        request_id (str): The unique request ID for this invocation.
        service (str): The name of the Cloud Run service.
        revision (str): The revision of the Cloud Run service.
    """

    def __init__(self):
        self.request_id = "mock_request_id_xyz789"
        self.service = "mock-cloud-run-service"
        self.revision = "mock-cloud-run-service-00001-abc"


class MockCloudEvent:
    """
    A mock class to simulate a GCP CloudEvent.

    Attributes:
        event (dict): A dictionary representing the mock event data
            with predefined key-value pairs following CloudEvents specification.
    """

    def __init__(self):
        self.event = {
            "specversion": "1.0",
            "type": "google.cloud.pubsub.topic.v1.messagePublished",
            "source": "//pubsub.googleapis.com/projects/mock-project/topics/mock-topic",
            "id": "mock_event_id_123456",
            "time": datetime.now(timezone.utc).isoformat(),
            "data": {
                "message": {
                    # Base64 encoded "Hello Cloud Functions"
                    "data": "SGVsbG8gQ2xvdWQgRnVuY3Rpb25z",
                    "attributes": {
                        "key1": "value1",
                        "key2": "value2",
                    },
                },
            },
        }

    def to_dict(self):
        """
        Convert the MockCloudEvent to a dictionary.

        Returns:
            dict: The dictionary representation of the event.
        """
        return self.event

    def to_json(self):
        """
        Convert the MockCloudEvent to a JSON string.

        Returns:
            str: The JSON string representation of the event.
        """
        return json.dumps(self.event, default=str)
