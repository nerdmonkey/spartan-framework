import boto3
import jsonpickle
import os

class AppService:
    def __init__(self):
        self.table_name = os.environ.get('GSM_TABLE', 'GlobalStateTable')
        self.region_name = os.environ.get('AWS_REGION', 'us-east-1')

        self.dynamodb_resource = boto3.resource('dynamodb', region_name=self.region_name)
        self.table = self.dynamodb_resource.Table(self.table_name)


    def set_state(self, key, value):
        try:
            value_json = jsonpickle.encode(value)
            response = self.table.update_item(
                Key={'Key': key},
                UpdateExpression='SET Attr_Data = :val',
                ExpressionAttributeValues={':val': value_json},
                ReturnValues='UPDATED_NEW'
            )
            return response['Attributes']['Attr_Data']
        except Exception as e:
            print(f"Error setting state: {e}")
            return None

    def get_state(self, key):
        try:
            response = self.table.get_item(Key={'Key': key})
            item = response.get('Item', {})
            if 'Attr_Data' in item:
                return jsonpickle.decode(item['Attr_Data'])
            else:
                return None
        except Exception as e:
            print(f"Error getting state: {e}")
            return None

    def remove_state(self, key):
        try:
            response = self.table.delete_item(Key={'Key': key})
            if 'Attributes' in response:
                return response['Attributes']['Attr_Data']
            else:
                return None
        except Exception as e:
            print(f"Error removing state: {e}")
            return None
