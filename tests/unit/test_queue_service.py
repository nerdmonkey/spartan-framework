import boto3
import pytest
from moto import mock_aws

from app.services.queue import QueueService


@mock_aws
def test_send_message_to_standard_queue():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    sqs.create_queue(QueueName="TestQueue")
    queue_url = sqs.get_queue_by_name(QueueName="TestQueue").url
    queue_service = QueueService()
    message = {"key": "value"}

    # Test
    response = queue_service.send_message(queue_url, message, str(1), str(1))

    # Assert
    assert "MessageId" in response


@mock_aws
def test_send_message_to_fifo_queue():
    # Mock the SQS service
    sqs = boto3.resource("sqs", region_name="us-east-1")

    # Create a FIFO queue
    queue = sqs.create_queue(
        QueueName="TestQueue.fifo",
        Attributes={
            "FifoQueue": "true",
            "ContentBasedDeduplication": "true",
        },
    )
    queue_url = queue.url

    # Test sending a message to the FIFO queue
    queue_service = QueueService()
    response = queue_service.send_message(
        queue_url, {"key": "value"}, "group1", "dedup1"
    )

    # Assert
    assert "MessageId" in response


@mock_aws
def test_receive_message():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    queue_service.send_message(queue_url, message, 1, 1)

    # Test
    response = queue_service.receive_message(queue_url)

    # Assert
    assert "Messages" in response
    assert response["Messages"][0]["Body"] == '{"key": "value"}'


@mock_aws
def test_delete_message():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    queue_service.send_message(queue_url, message, "1", "1")

    # Receive the message to get the correct receipt handle
    receive_response = queue_service.receive_message(queue_url)
    receipt_handle = receive_response["Messages"][0]["ReceiptHandle"]

    # Test
    delete_response = queue_service.delete_message(queue_url, receipt_handle)

    # Assert
    assert delete_response["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_send_message_with_invalid_queue_url():
    # Setup
    queue_service = QueueService()
    message = {"key": "value"}
    invalid_queue_url = (
        "https://sqs.us-east-1.amazonaws.com/123456789012/InvalidQueue"
    )

    # Test and Assert
    with pytest.raises(Exception):
        queue_service.send_message(invalid_queue_url, message, "1", "1")


@mock_aws
def test_receive_message_with_no_messages():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()

    # Test
    response = queue_service.receive_message(queue_url)

    # Assert
    assert "Messages" not in response


@mock_aws
def test_delete_message_with_invalid_receipt_handle():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    invalid_receipt_handle = "InvalidReceiptHandle"

    # Test and Assert
    with pytest.raises(Exception):
        queue_service.delete_message(queue_url, invalid_receipt_handle)


@mock_aws
def test_send_message_with_delay():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}

    # Test
    response = queue_service.send_message(
        queue_url, message, "1", "1", delay_seconds=10
    )

    # Assert
    assert "MessageId" in response


@mock_aws
def test_send_message_with_attributes():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    attributes = {
        "AttributeOne": {"DataType": "String", "StringValue": "ValueOne"}
    }

    # Test
    response = queue_service.send_message(
        queue_url, message, "1", "1", message_attributes=attributes
    )

    # Assert
    assert "MessageId" in response


@mock_aws
def test_receive_message_with_attributes():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    attributes = {
        "AttributeOne": {"DataType": "String", "StringValue": "ValueOne"}
    }
    queue_service.send_message(
        queue_url, message, "1", "1", message_attributes=attributes
    )

    # Test
    response = queue_service.receive_message(
        queue_url, message_attribute_names=["All"]
    )

    # Assert
    assert "Messages" in response
    assert response["Messages"][0]["Body"] == '{"key": "value"}'
    assert "MessageAttributes" in response["Messages"][0]
    assert (
        response["Messages"][0]["MessageAttributes"]["AttributeOne"][
            "StringValue"
        ]
        == "ValueOne"
    )


@mock_aws
def test_delete_message_batch():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    queue_service.send_message(queue_url, message, "1", "1")

    # Receive the message to get the correct receipt handle
    receive_response = queue_service.receive_message(queue_url)
    receipt_handle = receive_response["Messages"][0]["ReceiptHandle"]

    # Test
    delete_response = queue_service.delete_message_batch(
        queue_url, [receipt_handle]
    )

    # Assert
    assert delete_response["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_purge_queue():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    queue_service.send_message(queue_url, message, "1", "1")

    # Test
    purge_response = queue_service.purge_queue(queue_url)

    # Assert
    assert purge_response["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_create_queue_with_attributes():
    # Setup
    queue_service = QueueService()
    attributes = {
        "DelaySeconds": "5",
        "MaximumMessageSize": "262144",
        "MessageRetentionPeriod": "86400",
    }

    # Test
    queue_url = queue_service.create_queue(
        "TestQueueWithAttributes", attributes=attributes
    )

    # Assert
    assert queue_url is not None


@mock_aws
def test_create_fifo_queue():
    # Setup
    queue_service = QueueService()

    # Test
    queue_url = queue_service.create_queue("TestFIFOQueue", is_fifo=True)

    # Assert
    assert queue_url.endswith(".fifo")


@mock_aws
def test_send_message_batch():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    messages = [{"key": "value1"}, {"key": "value2"}]

    # Test
    response = queue_service.send_message_batch(queue_url, messages)

    # Assert
    assert "Successful" in response
    assert len(response["Successful"]) == 2


@mock_aws
def test_receive_messages():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    queue_service.send_message(queue_url, message, "1", "1")

    # Test
    messages = queue_service.receive_messages(queue_url)

    # Assert
    assert len(messages) > 0
    assert messages[0]["Body"] == '{"key": "value"}'


@mock_aws
def test_change_message_visibility():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()
    message = {"key": "value"}
    queue_service.send_message(queue_url, message, "1", "1")

    # Receive the message to get the correct receipt handle
    receive_response = queue_service.receive_message(queue_url)
    receipt_handle = receive_response["Messages"][0]["ReceiptHandle"]

    # Test
    queue_service.change_message_visibility(queue_url, receipt_handle, 60)

    # Assert
    # No exception should be raised


@mock_aws
def test_get_queue_attributes():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="TestQueue")
    queue_url = queue.url
    queue_service = QueueService()

    # Test
    attributes = queue_service.get_queue_attributes(queue_url)

    # Assert
    assert "QueueArn" in attributes


@mock_aws
def test_list_queues():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    sqs.create_queue(QueueName="TestQueue")
    queue_service = QueueService()

    # Test
    queue_urls = queue_service.list_queues()

    # Assert
    assert len(queue_urls) > 0


@mock_aws
def test_get_queue_url():
    # Setup
    sqs = boto3.resource("sqs", region_name="us-east-1")
    sqs.create_queue(QueueName="TestQueue")
    queue_service = QueueService()

    # Test
    queue_url = queue_service.get_queue_url("TestQueue")

    # Assert
    assert queue_url is not None
