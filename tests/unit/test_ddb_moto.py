import os

try:
    from moto.dynamodb2 import mock_dynamodb2 as mock_dynamodb
    import boto3
except Exception:
    import pytest

    pytest.skip("moto not available in this environment", allow_module_level=True)


@mock_dynamodb
def test_moto_creates_table_and_describe():
    # Create a table using moto and verify describe_table works
    table_name = "moto_test_table"

    client = boto3.client("dynamodb", region_name="us-east-1")
    client.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        AttributeDefinitions=[{"AttributeName": "PK", "AttributeType": "S"}, {"AttributeName": "SK", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    resp = client.describe_table(TableName=table_name)
    assert resp["Table"]["TableName"] == table_name
