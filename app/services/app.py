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
        self.table_name = os.environ.get("GSM_TABLE", "GlobalStateTable")
        self.region_name = os.environ.get("AWS_REGION", "us-east-1")
        self.dynamodb_resource = boto3.resource("dynamodb", region_name=self.region_name)
        self.table = self.dynamodb_resource.Table(self.table_name)

    def set_state(self, key, value):
        """
        Sets or updates a state in the DynamoDB table.

        Args:
            key (str): The key for the state to set or update.
            value (Any): The value of the state to be stored, which can be any
                         Python object that jsonpickle can serialize.

        Returns:
            str: The updated state after serialization or None in case of error.
        """
        try:
            value_json = jsonpickle.encode(value)
            response = self.table.update_item(
                Key={"Key": key},
                UpdateExpression="SET Attr_Data = :val",
                ExpressionAttributeValues={":val": value_json},
                ReturnValues="UPDATED_NEW",
            )
            return response["Attributes"]["Attr_Data"]
        except Exception as e:
            print(f"Error setting state: {e}")
            return None

    def get_state(self, key):
        """
        Retrieves a state from the DynamoDB table.

        Args:
            key (str): The key for the state to retrieve.

        Returns:
            Any: The deserialized Python object stored as the state or None if not found or in case of error.
        """
        try:
            response = self.table.get_item(Key={"Key": key})
            item = response.get("Item", {})
            if "Attr_Data" in item:
                return jsonpickle.decode(item["Attr_Data"])
            else:
                return None
        except Exception as e:
            print(f"Error getting state: {e}")
            return None

    def remove_state(self, key):
        """
        Removes a state from the DynamoDB table.

        Args:
            key (str): The key for the state to remove.

        Returns:
            str: The serialized state that was removed or None if not found or in case of error.
        """
        try:
            response = self.table.delete_item(Key={"Key": key})
            if "Attributes" in response:
                return response["Attributes"]["Attr_Data"]
            else:
                return None
        except Exception as e:
            print(f"Error removing state: {e}")
            return None
