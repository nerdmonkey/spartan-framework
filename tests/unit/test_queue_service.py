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
def test_create_queue_standard_and_fifo():
    queue_service = QueueService()
    # Standard queue
    url = queue_service.create_queue("MyStandardQueue")
    assert url.endswith("MyStandardQueue")
    # FIFO queue
    fifo_url = queue_service.create_queue("MyFifoQueue", is_fifo=True)
    assert fifo_url.endswith("MyFifoQueue.fifo")


@mock_aws
def test_create_queue_error(monkeypatch):
    queue_service = QueueService()

    def raise_client_error(*a, **kw):
        from botocore.exceptions import ClientError

        raise ClientError(
            {"Error": {"Code": "Boom", "Message": "fail"}}, "create_queue"
        )

    monkeypatch.setattr(
        queue_service.sqs_client, "create_queue", raise_client_error
    )
    with pytest.raises(Exception):
        queue_service.create_queue("fail-queue")


@mock_aws
def test_send_message_batch_and_receive_messages():
    queue_service = QueueService()
    url = queue_service.create_queue("BatchQueue")
    msgs = [{"foo": i} for i in range(3)]
    resp = queue_service.send_message_batch(url, msgs)
    assert "Successful" in resp
    received = queue_service.receive_messages(url)
    assert isinstance(received, list)


@mock_aws
def test_send_message_batch_fifo():
    queue_service = QueueService()
    url = queue_service.create_queue("BatchFifoQueue", is_fifo=True)
    msgs = [{"foo": i} for i in range(2)]
    resp = queue_service.send_message_batch(url, msgs, group_id="g1")
    assert "Successful" in resp


@mock_aws
def test_receive_messages_error(monkeypatch):
    queue_service = QueueService()
    url = queue_service.create_queue("ErrQueue")

    def raise_client_error(*a, **kw):
        from botocore.exceptions import ClientError

        raise ClientError(
            {"Error": {"Code": "Boom", "Message": "fail"}}, "receive_message"
        )

    monkeypatch.setattr(
        queue_service.sqs_client, "receive_message", raise_client_error
    )
    with pytest.raises(Exception):
        queue_service.receive_messages(url)


@mock_aws
def test_delete_message_batch():
    queue_service = QueueService()
    url = queue_service.create_queue("DelBatchQueue")
    queue_service.send_message(url, {"foo": 1}, "g", "d")
    msgs = queue_service.receive_messages(url)
    if msgs:
        resp = queue_service.delete_message_batch(url, msgs)
        assert "Successful" in resp


@mock_aws
def test_change_message_visibility(monkeypatch):
    queue_service = QueueService()
    url = queue_service.create_queue("VisQueue")
    queue_service.send_message(url, {"foo": 1}, "g", "d")
    msgs = queue_service.receive_messages(url)
    if msgs:
        rh = msgs[0]["ReceiptHandle"]
        monkeypatch.setattr(
            queue_service.sqs_client,
            "change_message_visibility",
            lambda **kw: True,
        )
        assert queue_service.change_message_visibility(url, rh, 10) is None


@mock_aws
def test_purge_queue_and_error(monkeypatch):
    queue_service = QueueService()
    url = queue_service.create_queue("PurgeQueue")
    queue_service.send_message(url, {"foo": 1}, "g", "d")
    queue_service.purge_queue(url)  # Should not raise

    def raise_client_error(*a, **kw):
        from botocore.exceptions import ClientError

        raise ClientError(
            {"Error": {"Code": "Boom", "Message": "fail"}}, "purge_queue"
        )

    monkeypatch.setattr(
        queue_service.sqs_client, "purge_queue", raise_client_error
    )
    with pytest.raises(Exception):
        queue_service.purge_queue(url)


@mock_aws
def test_get_queue_attributes_and_error(monkeypatch):
    queue_service = QueueService()
    url = queue_service.create_queue("AttrQueue")
    attrs = queue_service.get_queue_attributes(url)
    assert isinstance(attrs, dict)

    def raise_client_error(*a, **kw):
        from botocore.exceptions import ClientError

        raise ClientError(
            {"Error": {"Code": "Boom", "Message": "fail"}},
            "get_queue_attributes",
        )

    monkeypatch.setattr(
        queue_service.sqs_client, "get_queue_attributes", raise_client_error
    )
    with pytest.raises(Exception):
        queue_service.get_queue_attributes(url)


@mock_aws
def test_list_queues_and_get_queue_url_and_error(monkeypatch):
    queue_service = QueueService()
    queue_service.create_queue("ListQueue1")
    queue_service.create_queue("ListQueue2")
    urls = queue_service.list_queues()
    assert any("ListQueue1" in u for u in urls)
    assert any("ListQueue2" in u for u in urls)
    qurl = queue_service.get_queue_url("ListQueue1")
    assert qurl.endswith("ListQueue1")

    def raise_client_error(*a, **kw):
        from botocore.exceptions import ClientError

        raise ClientError(
            {"Error": {"Code": "Boom", "Message": "fail"}}, "get_queue_url"
        )

    monkeypatch.setattr(
        queue_service.sqs_client, "get_queue_url", raise_client_error
    )
    with pytest.raises(Exception):
        queue_service.get_queue_url("ListQueue1")
