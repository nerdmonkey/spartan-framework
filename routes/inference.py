from fastapi import APIRouter

from app.helpers.logger import get_logger
import torch


logger = get_logger("spartan-framework")

route = APIRouter(
    prefix="/api",
    tags=["Inference"],
    responses={404: {"description": "Not found"}},
)

def create_hello_world_tensor() -> torch.Tensor:
    """Creates a simple PyTorch tensor demonstration"""
    # Create a tensor with "Hello World" values
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    y = torch.tensor([[2.0, 1.0], [0.0, 1.0]])

    # Perform a basic operation
    result = torch.matmul(x, y)
    return result


@route.get("/inference", response_model=dict)
async def inference():
    """
    Endpoint for performing inference.

    When accessed, it returns a simple JSON response indicating that the inference service is operational.

    Returns:
        dict: A dictionary with a key 'message' and value 'OK', signifying the service is running.
    """

    logger.info("Inference endpoint called")

    try:
        # Check if PyTorch is using CUDA
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        # Run PyTorch hello world
        result = create_hello_world_tensor()
        logger.info("PyTorch operation successful")
        logger.info(f"Tensor result shape: {result.shape}")
        logger.info(f"Tensor values: {result.tolist()}")

        return {
            "statusCode": 200,
            "body": {
                "message": "Hello World from PyTorch",
                "tensor_result": result.tolist(),
                "device": device,
                "pytorch_version": torch.__version__,
            },
        }

    except Exception as e:
        logger.error(f"Error in PyTorch operation: {str(e)}")
        return {
            "statusCode": 500,
            "body": {"error": "PyTorch operation failed", "message": str(e)}
        }
