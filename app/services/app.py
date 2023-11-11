import logging
import os

import boto3
import jsonpickle


class AppService:
    """
    A service class to interact with an AWS DynamoDB table.

    This class provides methods to set, get, and remove a state in a DynamoDB table.
    It uses the boto3 library to communicate with AWS services and jsonpickle for
    serializing and deserializing Python objects to/from JSON.
    """

    def __init__(self):
        """
        Initializes the AppService class.

        Sets up the DynamoDB resource and table based on environment variables or
        default values. The table name and AWS region are configurable through
        environment variables.
        """
        self.logger = logging.getLogger(__name__)
        self._setup_dynamodb()

    def _setup_dynamodb(self):
        """Set up the DynamoDB resource and table."""
        table_name = os.environ.get("GSM_TABLE", "GlobalStateTable")
        region_name = os.environ.get("AWS_REGION", "us-east-1")
        self.dynamodb_resource = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb_resource.Table(table_name)

    def _serialize(self, value):
        """Serialize a Python object to JSON."""
        return jsonpickle.encode(value)

    def _deserialize(self, value):
        """Deserialize a JSON string to a Python object."""
        return jsonpickle.decode(value)

    def set_state(self, key, value):
        """Sets or updates a state in the DynamoDB table."""
        try:
            value_json = self._serialize(value)
            response = self.table.update_item(
                Key={"Key": key},
                UpdateExpression="SET Attr_Data = :val",
                ExpressionAttributeValues={":val": value_json},
                ReturnValues="UPDATED_NEW",
            )
            return response["Attributes"]["Attr_Data"]
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Error setting state: {e}")
            return None

    def get_state(self, key):
        """Retrieves a state from the DynamoDB table."""
        try:
            response = self.table.get_item(Key={"Key": key})
            item = response.get("Item", {})
            return self._deserialize(item["Attr_Data"]) if "Attr_Data" in item else None
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Error getting state: {e}")
            return None

    def remove_state(self, key):
        """Removes a state from the DynamoDB table."""
        try:
            response = self.table.delete_item(Key={"Key": key})
            return (
                response["Attributes"]["Attr_Data"]
                if "Attributes" in response
                else None
            )
        except boto3.exceptions.Boto3Error as e:
            self.logger.error(f"Error removing state: {e}")
            return None
