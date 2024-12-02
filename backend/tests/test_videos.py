# Path: backend/tests/test_videos.py
import pytest
from httpx import AsyncClient
import pandas as pd
from sqlalchemy import text
from datetime import datetime
from .test_data import get_test_video_path, get_test_speed_data_path, get_test_button_data_path

pytestmark = pytest.mark.asyncio

class TestVideos:

    async def test_upload_video_and_validate_response(
        self,
        client: AsyncClient,
        s3,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        test_content = b"test video content"
        files = {
            "video_file": ("test_video.mp4", test_content, "video/mp4")
        }
        
        response = await client.post(
            "/api/data/upload_video",
            files=files,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "video_id" in data["data"]
        assert "message" in data
        assert data["message"] == "Video uploaded successfully"

        # Verify database entry
        video_id = data["video_id"]
        result = await test_session.execute(
            text("""
            SELECT id, filename, s3_key, user_id, status
            FROM videos
            WHERE id = :video_id
            """),
            {"video_id": video_id}
        )
        video = result.first()
        
        assert video is not None
        assert video.filename == "test_video.mp4"
        assert video.user_id == test_user.id

    async def test_upload_speed_data(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        """Test CSV speed data upload"""
        # First upload a video
        files = {
            "video_file": ("test_video.mp4", b"test content", "video/mp4")
        }
        video_response = await client.post(
            "/api/data/upload_video",
            files=files,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Then upload speed data
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            files = {"csv_file": ("speed_data.csv", speed_file, "text/csv")}
            response = await client.post(
                f"/api/data/upload_csv/{video_id}",  # было f"/api/data/upload_csv" с video_id в params
                files=files,
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        assert response.status_code == 200
        assert response.json()["message"] == "CSV data uploaded successfully"

        # Verify speed data in database
        async with test_session.begin():
            result = await test_session.execute(
                """
                SELECT timestamp, speed, latitude, longitude
                FROM speed_data
                WHERE video_id = :video_id
                ORDER BY timestamp
                """,
                {"video_id": video_id}
            )
            speed_records = result.fetchall()

        assert len(speed_records) > 0
        first_record = speed_records[0]
        assert first_record.timestamp == 1  # From our test data
        assert first_record.speed == 0.0
        assert abs(first_record.latitude - 55.68595415917755) < 0.0001
        assert abs(first_record.longitude - 37.71803369749125) < 0.0001

    async def test_upload_button_data(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        """Test button data upload"""
        # First upload a video
        files = {
            "video_file": ("test_video.mp4", b"test content", "video/mp4")
        }
        video_response = await client.post(
            "/api/data/upload_video",
            files=files,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Then upload button data
        with open(get_test_button_data_path(), 'rb') as button_file:
            files = {"button_data_file": ("button_data.txt", button_file, "text/plain")}
            response = await client.post(
                f"/api/data/upload_button_data/{video_id}",  # было с video_id в params
                files=files, 
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        assert response.status_code == 200
        assert response.json()["message"] == "Button data uploaded successfully"

        # Verify button data in database
        async with test_session.begin():
            result = await test_session.execute(
                """
                SELECT timestamp, state
                FROM button_data
                WHERE video_id = :video_id
                ORDER BY timestamp
                """,
                {"video_id": video_id}
            )
            button_records = result.fetchall()

        assert len(button_records) > 0
        assert button_records[0].timestamp == 1717352241
        assert button_records[0].state is False

    async def test_get_next_unannotated_video(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        """Test getting next video for annotation"""
        # Create a video with all required data
        files = {
            "video_file": ("test_video.mp4", b"test content", "video/mp4")
        }
        video_response = await client.post(
            "/api/data/upload_video",
            files=files,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Upload required data
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            response = await client.post(
                f"/api/data/upload_csv/{video_id}",  # было f"/api/data/upload_csv" с video_id в params
                files=files,
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        with open(get_test_button_data_path(), 'rb') as button_file:
            await client.post(
                f"/api/data/upload_button_data/{video_id}",  # было с video_id в params
                files=files, 
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        # Get next unannotated video
        response = await client.get(
            "/api/data/next_unannotated",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )

        assert response.status_code == 200
        data = response.json()
        print(f'data for debug: {data}')
        assert "video_id" in data['data']
        assert data['data']["video_id"] == video_id
        assert data["status"] == "ready_for_annotation"
        assert "speed_data_count" in data
        assert "button_data_count" in data
        assert data["speed_data_count"] > 0
        assert data["button_data_count"] > 0

    async def test_get_video_data(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        """Test getting video data with speed and button data"""
        # Create a video with all data
        files = {
            "video_file": ("test_video.mp4", b"test content", "video/mp4")
        }
        video_response = await client.post(
            "/api/data/upload_video",
            files=files,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Upload data
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            response = await client.post(
                f"/api/data/upload_csv/{video_id}",  # было f"/api/data/upload_csv" с video_id в params
                files=files,
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        with open(get_test_button_data_path(), 'rb') as button_file:
            await client.post(
                f"/api/data/upload_button_data/{video_id}",  # было с video_id в params
                files=files, 
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        # Get video data
        response = await client.get(
            f"/api/data/{video_id}/data",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )

        assert response.status_code == 200
        data = response.json()
        
        assert "speed_data" in data["data"]
        assert len(data["speed_data"]) > 0
        assert all(key in data["speed_data"][0] for key in [
            "timestamp", "speed", "latitude", "longitude"
        ])

        assert "button_data" in data
        assert len(data["button_data"]) > 0
        assert all(key in data["button_data"][0] for key in [
            "timestamp", "state"
        ])

    async def test_error_cases(
        self,
        client: AsyncClient,
        test_user: "User"
    ):
        """Test various error cases"""
        # Try to upload invalid file type
        files = {
            "video_file": ("test.txt", b"not a video", "text/plain")
        }
        response = await client.post(
            "/api/data/upload_video",
            files=files,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

        # Try to upload speed data without video
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            response = await client.post(
                f"/api/data/upload_csv/{500}", 
                files=files,
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )
        assert response.status_code == 404
        assert response.json()["detail"] == "Not Found"

        # Try to access video without authentication
        response = await client.get("/api/data/next_unannotated")
        assert response.status_code == 401