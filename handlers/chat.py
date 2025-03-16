import json

from langchain_openai import AzureChatOpenAI

from app.helpers.context import MockLambdaContext
from app.helpers.environment import env
from app.helpers.logger import get_logger
from app.middlewares.logging import standard_logger

logger = get_logger("spartan-framework")
context = MockLambdaContext()


@standard_logger
def main(event, context):
    try:
        logger.info(
            "Event", extra={"event": event, "context": context.__dict__}
        )

        model = AzureChatOpenAI(
            openai_api_key=env("AZURE_OPENAI_API_KEY"),
            azure_endpoint=env("AZURE_OPENAI_ENDPOINT"),
            deployment_name=env("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_version=env("AZURE_OPENAI_API_VERSION"),
            temperature=0,
        )

        body = json.loads(event.get("prompt", "{}"))
        input_text = body.get("text", "Hello World")

        response = model.invoke(input_text)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"message": str(response)}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }


if __name__ == "__main__":
    event = {"prompt": json.dumps({"text": "What is science?"})}

    print(event)

    response = main(event, context)

    print(json.dumps(response, indent=2))
