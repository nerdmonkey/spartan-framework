import json

import boto3


class Secret:
    def __init__(self, secret_id: str = None):
        self._data = {}
        if secret_id:
            self.load(secret_id)

    def load(self, secret_id: str):
        try:
            client = boto3.client("secretsmanager")
            response = client.get_secret_value(SecretId=secret_id)
            self._data = json.loads(response["SecretString"])
        except Exception:
            self._data = {}

    def __call__(self, key: str, default=None):
        return self._data.get(key, default)

    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(f"Secret has no attribute '{key}'")
