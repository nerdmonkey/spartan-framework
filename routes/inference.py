from fastapi import APIRouter
from langchain_openai import AzureChatOpenAI

from app.helpers.environment import env
from app.helpers.logger import get_logger
from app.requests.query import QueryRequest
from app.responses.query import QueryResponse

logger = get_logger("spartan-framework")


route = APIRouter(
    prefix="/api",
    tags=["Inference"],
    responses={404: {"description": "Not found"}},
)


@route.post("/inference", response_model=QueryResponse)
async def inference(request: QueryRequest):
    """
    Endpoint for performing inference.

    When accessed, it returns a simple JSON response indicating that the inference service is operational.

    Returns:
        dict: A dictionary with a key 'message' and value 'OK', signifying the service is running.
    """

    try:
        logger.info("Performing inference")

        model = AzureChatOpenAI(
            openai_api_key=env("AZURE_OPENAI_API_KEY"),
            azure_endpoint=env("AZURE_OPENAI_ENDPOINT"),
            deployment_name=env("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_version=env("AZURE_OPENAI_API_VERSION"),
            temperature=0,
        )

        response = model.invoke(request.query)

        return {
            "statusCode": 200,
            "response": {
                "content": response.content,
                "metadata": response.response_metadata,
            },
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "response": {"error": "Error occured", "message": str(e)},
        }
