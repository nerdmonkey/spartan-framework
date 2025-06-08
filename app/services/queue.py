import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


class QueueService:
    """
    An enhanced service class to interact with AWS Simple Queue Service (SQS).
    """

    def __init__(
        self, region_name: str = "us-east-1", max_messages: int = 10
    ) -> None:
        """
        Initialize the QueueService with configurable parameters.

        Args:
            region_name (str): AWS region name
            max_messages (int): Maximum number of messages to receive at once (1-10)
        """
        self.sqs_client = boto3.client("sqs", region_name=region_name)
        self.max_messages = min(
            max(1, max_messages), 10
        )  # Ensure value is between 1-10

    def create_queue(
        self, queue_name: str, is_fifo: bool = False, attributes: Dict = None
    ) -> str:
        """
        Creates a new SQS queue.

        Args:
            queue_name (str): Name of the queue to create
            is_fifo (bool): Whether to create a FIFO queue
            attributes (Dict): Additional queue attributes

        Returns:
            str: URL of the created queue
        """
        queue_attributes = attributes or {}

        if is_fifo:
            if not queue_name.endswith(".fifo"):
                queue_name = f"{queue_name}.fifo"
            queue_attributes["FifoQueue"] = "true"
            queue_attributes["ContentBasedDeduplication"] = "true"

        try:
            response = self.sqs_client.create_queue(
                QueueName=queue_name, Attributes=queue_attributes
            )
            return response["QueueUrl"]
        except ClientError as e:
            raise Exception(f"Failed to create queue: {str(e)}")

    def send_message_batch(
        self, queue_url: str, messages: List[Dict], group_id: str = None
    ) -> Dict[str, Any]:
        """
        Sends multiple messages to an SQS queue in a single request.

        Args:
            queue_url (str): The URL of the SQS queue
            messages (List[Dict]): List of messages to send
            group_id (str, optional): Message group ID for FIFO queues

        Returns:
            Dict[str, Any]: Response containing successful and failed messages
        """
        entries = []
        for i, msg in enumerate(messages):
            entry = {"Id": str(i), "MessageBody": json.dumps(msg)}

            if queue_url.endswith(".fifo"):
                entry["MessageGroupId"] = group_id or "default"
                entry[
                    "MessageDeduplicationId"
                ] = f"{datetime.utcnow().timestamp()}-{i}"

            entries.append(entry)

        return self.sqs_client.send_message_batch(
            QueueUrl=queue_url, Entries=entries
        )

    def receive_messages(
        self, queue_url: str, wait_time: int = 20, visibility_timeout: int = 30
    ) -> List[Dict]:
        """
        Receives multiple messages from an SQS queue with long polling.

        Args:
            queue_url (str): The URL of the SQS queue
            wait_time (int): Long polling wait time in seconds (0-20)
            visibility_timeout (int): Message visibility timeout in seconds

        Returns:
            List[Dict]: List of received messages
        """
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=self.max_messages,
                WaitTimeSeconds=min(max(0, wait_time), 20),
                VisibilityTimeout=visibility_timeout,
                AttributeNames=["All"],
                MessageAttributeNames=["All"],
            )
            return response.get("Messages", [])
        except ClientError as e:
            raise Exception(f"Failed to receive messages: {str(e)}")

    def delete_message_batch(
        self, queue_url: str, messages: List[Dict]
    ) -> Dict[str, Any]:
        """
        Deletes multiple messages from an SQS queue in a single request.

        Args:
            queue_url (str): The URL of the SQS queue
            messages (List[Dict]): List of messages to delete

        Returns:
            Dict[str, Any]: Response containing successful and failed deletions
        """
        entries = [
            {"Id": str(i), "ReceiptHandle": msg["ReceiptHandle"]}
            for i, msg in enumerate(messages)
        ]

        return self.sqs_client.delete_message_batch(
            QueueUrl=queue_url, Entries=entries
        )

    def change_message_visibility(
        self, queue_url: str, receipt_handle: str, visibility_timeout: int
    ) -> None:
        """
        Changes the visibility timeout of a message.

        Args:
            queue_url (str): The URL of the SQS queue
            receipt_handle (str): Receipt handle of the message
            visibility_timeout (int): New visibility timeout in seconds
        """
        self.sqs_client.change_message_visibility(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=visibility_timeout,
        )

    def purge_queue(self, queue_url: str) -> None:
        """
        Deletes all messages from the queue.

        Args:
            queue_url (str): The URL of the SQS queue
        """
        try:
            self.sqs_client.purge_queue(QueueUrl=queue_url)
        except ClientError as e:
            raise Exception(f"Failed to purge queue: {str(e)}")

    def get_queue_attributes(
        self, queue_url: str, attribute_names: List[str] = ["All"]
    ) -> Dict[str, str]:
        """
        Gets queue attributes.

        Args:
            queue_url (str): The URL of the SQS queue
            attribute_names (List[str]): List of attribute names to retrieve

        Returns:
            Dict[str, str]: Queue attributes
        """
        try:
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=queue_url, AttributeNames=attribute_names
            )
            return response.get("Attributes", {})
        except ClientError as e:
            raise Exception(f"Failed to get queue attributes: {str(e)}")

    def send_message(
        self, queue_url: str, message: Dict, group_id: str, dedup_id: str
    ) -> Dict[str, Any]:
        """
        Sends a single message to an SQS queue.

        Args:
            queue_url (str): The URL of the SQS queue
            message (Dict): Message to send
            group_id (str): Message group ID for FIFO queues
            dedup_id (str): Deduplication ID for FIFO queues

        Returns:
            Dict[str, Any]: Response containing MessageId if successful
        """
        try:
            message_body = json.dumps(message)
            params = {"QueueUrl": queue_url, "MessageBody": message_body}

            if queue_url.endswith(".fifo"):
                params["MessageGroupId"] = group_id
                params["MessageDeduplicationId"] = dedup_id

            return self.sqs_client.send_message(**params)
        except ClientError as e:
            raise Exception(f"Failed to send message: {str(e)}")

    def receive_message(self, queue_url: str) -> Dict[str, Any]:
        """
        Receives a single message from an SQS queue.

        Args:
            queue_url (str): The URL of the SQS queue

        Returns:
            Dict[str, Any]: Response containing received messages
        """
        try:
            return self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                AttributeNames=["All"],
                MessageAttributeNames=["All"],
            )
        except ClientError as e:
            raise Exception(f"Failed to receive message: {str(e)}")

    def delete_message(
        self, queue_url: str, receipt_handle: str
    ) -> Dict[str, Any]:
        """
        Deletes a message from an SQS queue using its receipt handle.

        Args:
            queue_url (str): The URL of the SQS queue
            receipt_handle (str): The receipt handle of the message to delete

        Returns:
            Dict[str, Any]: Response containing deletion status
        """
        try:
            return self.sqs_client.delete_message(
                QueueUrl=queue_url, ReceiptHandle=receipt_handle
            )
        except ClientError as e:
            raise Exception(f"Failed to delete message: {str(e)}")

    def list_queues(self, prefix: Optional[str] = None) -> List[str]:
        """
        Lists all queues in the account.

        Args:
            prefix (str, optional): Queue name prefix to filter the list

        Returns:
            List[str]: List of queue URLs
        """
        try:
            if prefix:
                response = self.sqs_client.list_queues(QueueNamePrefix=prefix)
            else:
                response = self.sqs_client.list_queues()
            return response.get("QueueUrls", [])
        except ClientError as e:
            raise Exception(f"Failed to list queues: {str(e)}")

    def get_queue_url(self, queue_name: str) -> str:
        """
        Gets the URL of a queue by its name.

        Args:
            queue_name (str): Name of the queue

        Returns:
            str: URL of the queue
        """
        try:
            response = self.sqs_client.get_queue_url(QueueName=queue_name)
            return response["QueueUrl"]
        except ClientError as e:
            raise Exception(f"Failed to get queue URL: {str(e)}")
