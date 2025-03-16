import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError
from app.services.queue import QueueService

# Fixtures
@pytest.fixture
def mock_sqs():
    with patch('boto3.client') as mock:
        sqs_client = Mock()
        mock.return_value = sqs_client
        yield sqs_client

@pytest.fixture
def queue_service(mock_sqs):
    return QueueService(region_name='us-east-1', max_messages=10)

@pytest.fixture
def sample_queue_url():
    return "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"

@pytest.fixture
def sample_messages():
    return [
        {"id": 1, "data": "test1"},
        {"id": 2, "data": "test2"}
    ]

# Test Functions
def test_queue_service_initialization():
    """Test QueueService initialization with different parameters"""
    # Test default values
    service = QueueService()
    assert service.max_messages == 10

    # Test custom values
    service = QueueService(region_name='us-west-2', max_messages=5)
    assert service.max_messages == 5

    # Test max_messages bounds
    service = QueueService(max_messages=15)
    assert service.max_messages == 10  # Should be capped at 10

    service = QueueService(max_messages=0)
    assert service.max_messages == 1  # Should be minimum 1

def test_create_standard_queue(queue_service, mock_sqs):
    """Test creation of standard queue"""
    mock_sqs.create_queue.return_value = {"QueueUrl": "standard-queue-url"}

    url = queue_service.create_queue("test-queue")

    assert url == "standard-queue-url"
    mock_sqs.create_queue.assert_called_with(
        QueueName="test-queue",
        Attributes={}
    )

def test_create_fifo_queue(queue_service, mock_sqs):
    """Test creation of FIFO queue"""
    mock_sqs.create_queue.return_value = {"QueueUrl": "fifo-queue-url"}

    url = queue_service.create_queue("test-queue", is_fifo=True)

    assert url == "fifo-queue-url"
    mock_sqs.create_queue.assert_called_with(
        QueueName="test-queue.fifo",
        Attributes={
            "FifoQueue": "true",
            "ContentBasedDeduplication": "true"
        }
    )

def test_create_queue_with_attributes(queue_service, mock_sqs):
    """Test queue creation with custom attributes"""
    custom_attributes = {"DelaySeconds": "60"}
    mock_sqs.create_queue.return_value = {"QueueUrl": "custom-queue-url"}

    url = queue_service.create_queue("test-queue", attributes=custom_attributes)

    assert url == "custom-queue-url"
    mock_sqs.create_queue.assert_called_with(
        QueueName="test-queue",
        Attributes=custom_attributes
    )

def test_create_queue_error_handling(queue_service, mock_sqs):
    """Test error handling in queue creation"""
    mock_sqs.create_queue.side_effect = ClientError(
        {"Error": {"Code": "QueueAlreadyExists", "Message": "Queue already exists"}},
        "CreateQueue"
    )

    with pytest.raises(Exception) as exc_info:
        queue_service.create_queue("test-queue")
    assert "Failed to create queue" in str(exc_info.value)

def test_send_message_batch_standard_queue(queue_service, mock_sqs, sample_queue_url, sample_messages):
    """Test sending batch messages to standard queue"""
    mock_sqs.send_message_batch.return_value = {
        "Successful": [{"Id": "0"}, {"Id": "1"}],
        "Failed": []
    }

    response = queue_service.send_message_batch(sample_queue_url, sample_messages)

    assert "Successful" in response
    assert len(response["Successful"]) == 2
    assert "Failed" in response
    assert len(response["Failed"]) == 0

def test_send_message_batch_fifo_queue(queue_service, mock_sqs, sample_queue_url, sample_messages):
    """Test sending batch messages to FIFO queue"""
    fifo_url = f"{sample_queue_url}.fifo"
    mock_sqs.send_message_batch.return_value = {
        "Successful": [{"Id": "0"}, {"Id": "1"}],
        "Failed": []
    }

    response = queue_service.send_message_batch(fifo_url, sample_messages, "group1")

    calls = mock_sqs.send_message_batch.call_args_list[-1]
    entries = calls[1]["Entries"]
    assert all("MessageGroupId" in entry for entry in entries)
    assert all("MessageDeduplicationId" in entry for entry in entries)

def test_receive_messages_success(queue_service, mock_sqs, sample_queue_url):
    """Test successful message reception"""
    mock_messages = [
        {"MessageId": "1", "Body": json.dumps({"data": "test1"})},
        {"MessageId": "2", "Body": json.dumps({"data": "test2"})}
    ]
    mock_sqs.receive_message.return_value = {"Messages": mock_messages}

    messages = queue_service.receive_messages(sample_queue_url)

    assert len(messages) == 2
    assert messages == mock_messages

def test_receive_messages_empty_queue(queue_service, mock_sqs, sample_queue_url):
    """Test receiving messages from empty queue"""
    mock_sqs.receive_message.return_value = {}

    messages = queue_service.receive_messages(sample_queue_url)

    assert len(messages) == 0

def test_receive_messages_error(queue_service, mock_sqs, sample_queue_url):
    """Test error handling in message reception"""
    mock_sqs.receive_message.side_effect = ClientError(
        {"Error": {"Code": "QueueDoesNotExist", "Message": "Queue does not exist"}},
        "ReceiveMessage"
    )

    with pytest.raises(Exception) as exc_info:
        queue_service.receive_messages(sample_queue_url)
    assert "Failed to receive messages" in str(exc_info.value)

def test_delete_message_batch_success(queue_service, mock_sqs, sample_queue_url):
    """Test successful batch message deletion"""
    messages = [
        {"MessageId": "1", "ReceiptHandle": "receipt1"},
        {"MessageId": "2", "ReceiptHandle": "receipt2"}
    ]
    mock_sqs.delete_message_batch.return_value = {
        "Successful": [{"Id": "0"}, {"Id": "1"}],
        "Failed": []
    }

    response = queue_service.delete_message_batch(sample_queue_url, messages)

    assert "Successful" in response
    assert len(response["Successful"]) == 2
    assert "Failed" in response
    assert len(response["Failed"]) == 0

def test_purge_queue_success(queue_service, mock_sqs, sample_queue_url):
    """Test successful queue purge"""
    queue_service.purge_queue(sample_queue_url)
    mock_sqs.purge_queue.assert_called_once_with(QueueUrl=sample_queue_url)

def test_purge_queue_error(queue_service, mock_sqs, sample_queue_url):
    """Test error handling in queue purge"""
    mock_sqs.purge_queue.side_effect = ClientError(
        {"Error": {"Code": "Error", "Message": "Purge failed"}},
        "PurgeQueue"
    )

    with pytest.raises(Exception) as exc_info:
        queue_service.purge_queue(sample_queue_url)
    assert "Failed to purge queue" in str(exc_info.value)

def test_get_queue_attributes_success(queue_service, mock_sqs, sample_queue_url):
    """Test successful retrieval of queue attributes"""
    mock_attributes = {
        "ApproximateNumberOfMessages": "100",
        "CreatedTimestamp": "1234567890"
    }
    mock_sqs.get_queue_attributes.return_value = {"Attributes": mock_attributes}

    attributes = queue_service.get_queue_attributes(sample_queue_url)

    assert attributes == mock_attributes
    mock_sqs.get_queue_attributes.assert_called_with(
        QueueUrl=sample_queue_url,
        AttributeNames=["All"]
    )

def test_list_queues_without_prefix(queue_service, mock_sqs):
    """Test listing queues without prefix"""
    mock_urls = ["queue1", "queue2"]
    mock_sqs.list_queues.return_value = {"QueueUrls": mock_urls}

    urls = queue_service.list_queues()

    assert urls == mock_urls
    mock_sqs.list_queues.assert_called_with()

def test_list_queues_with_prefix(queue_service, mock_sqs):
    """Test listing queues with prefix"""
    mock_urls = ["test-queue1", "test-queue2"]
    mock_sqs.list_queues.return_value = {"QueueUrls": mock_urls}

    urls = queue_service.list_queues("test-")

    assert urls == mock_urls
    mock_sqs.list_queues.assert_called_with(QueueNamePrefix="test-")

def test_get_queue_url_success(queue_service, mock_sqs):
    """Test successful queue URL retrieval"""
    mock_sqs.get_queue_url.return_value = {"QueueUrl": "test-queue-url"}

    url = queue_service.get_queue_url("test-queue")

    assert url == "test-queue-url"
    mock_sqs.get_queue_url.assert_called_with(QueueName="test-queue")
