import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.dataset_loader import load_dataset_stream

@patch("ingestion.dataset_loader.load_dataset")
def test_load_dataset_stream(mock_load_dataset):
    mock_load_dataset.return_value = "mocked_stream"
    stream = load_dataset_stream(split="train")
    assert stream == "mocked_stream"
    # Verify that load_dataset was called with name="default"
    mock_load_dataset.assert_called_once_with("ai4bharat/MSMARCO-XI", name="default", split="train", streaming=True)
    
    # Assert that it was NOT called with language config names
    for bad_name in ["hi", "mr", "en"]:
        for call in mock_load_dataset.call_args_list:
            assert call.kwargs.get("name") != bad_name
