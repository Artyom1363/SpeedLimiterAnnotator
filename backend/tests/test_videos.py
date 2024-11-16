# tests/test_videos.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Video Annotation Backend API"}

def test_upload_video():
    response = client.post(
        "/videos/",
        json={"filename": "test_video.mp4", "file_metadata": "test metadata"}
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "test_video.mp4"
    assert response.json()["file_metadata"] == "test metadata"

