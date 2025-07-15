import pytest
import json
from unittest.mock import patch, MagicMock, PropertyMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# --- Fixtures for Mocking --- #

@pytest.fixture
def mock_get_transcript():
    with patch('src.main.get_transcript') as mock:
        yield mock

@pytest.fixture
def mock_genai_client():
    with patch('src.main.client') as mock_client:
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "summary": "This is a test summary.",
            "english_learning": {
                "vocabulary": [{"word": "transcript", "example": "I read the transcript of the meeting."}],
                "grammar": [{"rule": "Past Tense", "example": "The video was very informative."}]
            }
        })
        mock_client.models.generate_content.return_value = mock_response
        yield mock_client.models.generate_content

# --- Test Cases --- #

def test_summarize_success(mock_get_transcript, mock_genai_client):
    """Test the /summarize endpoint with a successful scenario."""
    mock_get_transcript.return_value = "This is a test transcript."
    response = client.post("/summarize", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "This is a test summary."
    assert "vocabulary" in data["english_learning"] 
    args, kwargs = mock_genai_client.call_args
    assert 'config' in kwargs
    assert kwargs['config'].response_mime_type == 'application/json'

def test_summarize_invalid_youtube_url():
    """Test that an invalid URL format returns a 400 error."""
    response = client.post("/summarize", json={"url": "this-is-not-a-url"})
    assert response.status_code == 400
    assert "Invalid YouTube URL" in response.json()["detail"]

def test_summarize_transcript_not_found(mock_get_transcript):
    """Test the case where a transcript cannot be fetched."""
    from fastapi import HTTPException
    mock_get_transcript.side_effect = HTTPException(status_code=404, detail="Transcript not found")
    response = client.post("/summarize", json={"url": "https://www.youtube.com/watch?v=nonexistent"})
    assert response.status_code == 404
    assert "Transcript not found" in response.json()["detail"]

def test_summarize_model_invalid_response(mock_get_transcript, mock_genai_client):
    """Test the case where the model returns an empty or invalid (non-JSON) response."""
    mock_get_transcript.return_value = "A valid transcript."
    
    mock_response = MagicMock()
    # The .text is accessed on the *return value* of generate_content
    type(mock_response).text = PropertyMock(side_effect=ValueError)
    mock_genai_client.return_value = mock_response

    response = client.post("/summarize", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert response.status_code == 500
    assert "invalid or empty response from the model" in response.json()["detail"]

def test_root_path():
    """Test the root path to ensure the static files are being served."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']