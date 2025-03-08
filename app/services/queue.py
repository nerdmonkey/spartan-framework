import json
from typing import Any, Dict, List, Optional
from datetime import datetime

import boto3
from botocore.exceptions import ClientError


class QueueService:
    """
    An enhanced service class to interact with AWS Simple Queue Service (SQS).
    """

    def __init__(self, region_name: str = "us-east-1", max_messages: int = 10) -> None:
        """
        Initialize the QueueService with configurable parameters.

        Args:
            region_name (str): AWS region name
            max_messages (int): Maximum number of messages to receive at once (1-10)
        """
        self.sqs_client = boto3.client("sqs", region_name=region_name)
        self.max_messages = min(max(1, max_messages), 10)  # Ensure value is between 1-10

    def create_queue(self, queue_name: str, is_fifo: bool = False, attributes: Dict = None) -> str:
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
            if not queue_name.endswith('.fifo'):
                queue_name = f"{queue_name}.fifo"
            queue_attributes['FifoQueue'] = 'true'
            queue_attributes['ContentBasedDeduplication'] = 'true'

        try:
            response = self.sqs_client.create_queue(
                QueueName=queue_name,
                Attributes=queue_attributes
            )
            return response['QueueUrl']
        except ClientError as e:
            raise Exception(f"Failed to create queue: {str(e)}")

    def send_message_batch(
        self,
        queue_url: str,
        messages: List[Dict],
        group_id: str = None
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
            entry = {
                'Id': str(i),
                'MessageBody': json.dumps(msg)
            }

            if queue_url.endswith('.fifo'):
                entry['MessageGroupId'] = group_id or 'default'
                entry['MessageDeduplicationId'] = f"{datetime.utcnow().timestamp()}-{i}"

            entries.append(entry)

        return self.sqs_client.send_message_batch(
            QueueUrl=queue_url,
            Entries=entries
        )

    def receive_messages(
        self,
        queue_url: str,
        wait_time: int = 20,
        visibility_timeout: int = 30
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
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            return response.get('Messages', [])
        except ClientError as e:
            raise Exception(f"Failed to receive messages: {str(e)}")

    def delete_message_batch(
        self,
        queue_url: str,
        messages: List[Dict]
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
            {
                'Id': str(i),
                'ReceiptHandle': msg['ReceiptHandle']
            }
            for i, msg in enumerate(messages)
        ]

        return self.sqs_client.delete_message_batch(
            QueueUrl=queue_url,
            Entries=entries
        )

    def change_message_visibility(
        self,
        queue_url: str,
        receipt_handle: str,
        visibility_timeout: int
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
            VisibilityTimeout=visibility_timeout
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
        self,
        queue_url: str,
        attribute_names: List[str] = ['All']
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
                QueueUrl=queue_url,
                AttributeNames=attribute_names
            )
            return response.get('Attributes', {})
        except ClientError as e:
            raise Exception(f"Failed to get queue attributes: {str(e)}")

    def send_message(
        self,
        queue_url: str,
        message: Dict[str, Any],
        group_id: Optional[str] = None,
        deduplication_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends a single message to an SQS queue.

        Args:
            queue_url (str): The URL of the SQS queue
            message (Dict[str, Any]): The message to send
            group_id (str, optional): Message group ID for FIFO queues
            deduplication_id (str, optional): Message deduplication ID for FIFO queues

        Returns:
            Dict[str, Any]: Response from SQS
        """
        params = {
            'QueueUrl': queue_url,
            'MessageBody': json.dumps(message)
        }

        if queue_url.endswith('.fifo'):
            params['MessageGroupId'] = group_id or 'default'
            params['MessageDeduplicationId'] = deduplication_id or str(datetime.utcnow().timestamp())

        return self.sqs_client.send_message(**params)

    def receive_message(
        self,
        queue_url: str,
        wait_time: int = 20,
        visibility_timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Receives a single message from an SQS queue.

        Args:
            queue_url (str): The URL of the SQS queue
            wait_time (int): Long polling wait time in seconds (0-20)
            visibility_timeout (int): Message visibility timeout in seconds

        Returns:
            Dict[str, Any]: Response from SQS
        """
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=min(max(0, wait_time), 20),
                VisibilityTimeout=visibility_timeout,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            return response
        except ClientError as e:
            raise Exception(f"Failed to receive message: {str(e)}")

    def delete_message(
        self,
        queue_url: str,
        receipt_handle: str
    ) -> Dict[str, Any]:
        """
        Deletes a single message from an SQS queue.

        Args:
            queue_url (str): The URL of the SQS queue
            receipt_handle (str): Receipt handle of the message to delete

        Returns:
            Dict[str, Any]: Response from SQS
        """
        try:
            response = self.sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return response
        except ClientError as e:
            raise Exception(f"Failed to delete message: {str(e)}")
