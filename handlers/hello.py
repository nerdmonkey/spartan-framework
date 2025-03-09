from typing import Any, Dict

import torch

from app.helpers.context import MockLambdaContext
from app.helpers.logger import get_logger

context = MockLambdaContext()

logger = get_logger("spartan-framework")


def create_hello_world_tensor() -> torch.Tensor:
    """Creates a simple PyTorch tensor demonstration"""
    # Create a tensor with "Hello World" values
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    y = torch.tensor([[2.0, 1.0], [0.0, 1.0]])

    # Perform a basic operation
    result = torch.matmul(x, y)
    return result


def main(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("Event", extra={"event": event, "context": context.__dict__})

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
            "body": {"error": "PyTorch operation failed", "message": str(e)},
        }


if __name__ == "__main__":
    result = main((), context)
    logger.info("response", extra={"result": result})
