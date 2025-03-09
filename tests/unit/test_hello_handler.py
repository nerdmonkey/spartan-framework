import pytest
from unittest.mock import patch, MagicMock, call
from handlers.hello import main, create_hello_world_tensor


@patch("handlers.hello.logger")
@patch("handlers.hello.torch")
def test_main(mock_torch, mock_logger):
    mock_torch.cuda.is_available.return_value = False
    mock_torch.__version__ = "1.8.0"

    mock_event = {}
    mock_context = MagicMock()

    result = main(mock_event, mock_context)

    print("Actual logger calls:", mock_logger.info.call_args_list)
    print("All logger mock calls:", mock_logger.mock_calls)

    first_call = mock_logger.info.call_args_list[0]
    assert first_call[0][0] == "Event"
    assert "event" in first_call[1]["extra"]
    assert "context" in first_call[1]["extra"]

    assert result["statusCode"] == 200
    assert result["body"]["message"] == "Hello World from PyTorch"
    assert result["body"]["device"] == "cpu"
    assert result["body"]["pytorch_version"] == "1.8.0"


def test_create_hello_world_tensor():
    result = create_hello_world_tensor()
    expected_result = [[2.0, 3.0], [6.0, 7.0]]
    assert result.tolist() == expected_result
