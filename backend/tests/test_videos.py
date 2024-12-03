# Path: backend/tests/test_videos.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import List
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
        assert "video_id" in data
        assert data["status"] == "success"
        assert data["message"] == "Video uploaded successfully"

        # Verify database entry
        async with test_session.begin():
            result = await test_session.execute(
                text("""
                SELECT id, filename, s3_key, user_id, status
                FROM videos
                WHERE id = :video_id
                """),
                {"video_id": data["video_id"]}
            )
            video = result.first()
            
            assert video is not None
            assert video.filename == "test_video.mp4"
            assert video.user_id == test_user.id
            assert video.status == "unannotated"

    async def test_upload_csv_data(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        # First upload a video
        video_response = await client.post(
            "/api/data/upload_video",
            files={"video_file": ("test_video.mp4", b"test content", "video/mp4")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Then upload CSV data
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            response = await client.post(
                f"/api/data/upload_csv/{video_id}",
                files={"csv_file": ("speed_data.csv", speed_file, "text/csv")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "CSV data uploaded successfully"

        # Verify data in database
        async with test_session.begin():
            result = await test_session.execute(
                text("""
                SELECT timestamp, speed, latitude, longitude
                FROM speed_data
                WHERE video_id = :video_id
                ORDER BY timestamp
                """),
                {"video_id": video_id}
            )
            speed_records = result.fetchall()
            assert len(speed_records) > 0

    async def test_upload_button_data(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        # Upload video first
        video_response = await client.post(
            "/api/data/upload_video",
            files={"video_file": ("test_video.mp4", b"test content", "video/mp4")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Upload button data
        with open(get_test_button_data_path(), 'rb') as button_file:
            response = await client.post(
                f"/api/data/upload_button_data/{video_id}",
                files={"button_data_file": ("button_data.txt", button_file, "text/plain")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Button data uploaded successfully"

        # Verify in database
        async with test_session.begin():
            result = await test_session.execute(
                text("""
                SELECT timestamp, state
                FROM button_data
                WHERE video_id = :video_id
                ORDER BY timestamp
                """),
                {"video_id": video_id}
            )
            button_records = result.fetchall()
            assert len(button_records) > 0

    async def test_get_next_unannotated_video(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        # Create a test video
        video_response = await client.post(
            "/api/data/upload_video",
            files={"video_file": ("test_video.mp4", b"test content", "video/mp4")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        created_video_id = video_response.json()["video_id"]

        # Get next unannotated video
        response = await client.get(
            "/api/data/next_unannotated",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == created_video_id
        assert data["status"] == "unannotated"
        assert "title" in data
        assert "upload_date" in data
        assert data["locked_by"] is None
        assert data["lock_time"] is None

    async def test_get_video_data(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        # Create video with all required data
        video_response = await client.post(
            "/api/data/upload_video",
            files={"video_file": ("test_video.mp4", b"test content", "video/mp4")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Upload CSV data
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            await client.post(
                f"/api/data/upload_csv/{video_id}",
                files={"csv_file": ("speed_data.csv", speed_file, "text/csv")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        # Upload button data
        with open(get_test_button_data_path(), 'rb') as button_file:
            await client.post(
                f"/api/data/upload_button_data/{video_id}",
                files={"button_data_file": ("button_data.txt", button_file, "text/plain")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        # Get video data
        response = await client.get(
            f"/api/data/{video_id}/data",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "speed_data" in data["data"]
        assert "button_data" in data["data"]
        assert len(data["data"]["speed_data"]) > 0
        assert len(data["data"]["button_data"]) > 0

    async def test_add_video_timestamp(
        self,
        client: AsyncClient,
        test_user: "User",
        test_session: "AsyncSession"
    ):
        # Create test video
        video_response = await client.post(
            "/api/data/upload_video",
            files={"video_file": ("test_video.mp4", b"test content", "video/mp4")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        # Add timestamps
        timestamps_data = [
            {"timestamp": 1.0, "video_segment": "segment1"},
            {"timestamp": 2.0, "video_segment": "segment2"}
        ]
        response = await client.post(
            f"/api/data/add_video_timestamp/{video_id}",
            json=timestamps_data,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Video timestamps added/adjusted successfully"

    async def test_error_cases(
        self,
        client: AsyncClient,
        test_user: "User"
    ):
        # Test invalid file type
        response = await client.post(
            "/api/data/upload_video",
            files={"video_file": ("test.txt", b"not a video", "text/plain")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

        # Test uploading CSV for non-existent video
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            response = await client.post(
                f"/api/data/upload_csv/nonexistent-id",
                files={"csv_file": ("speed_data.csv", speed_file, "text/csv")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )
        assert response.status_code == 404
        assert response.json()["detail"] == "Video not found"

        # Test uploading invalid CSV format
        video_response = await client.post(
            "/api/data/upload_video",
            files={"video_file": ("test_video.mp4", b"test content", "video/mp4")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        video_id = video_response.json()["video_id"]

        response = await client.post(
            f"/api/data/upload_csv/{video_id}",
            files={"csv_file": ("invalid.csv", b"invalid,csv,format", "text/csv")},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert response.status_code == 400
        assert "Invalid CSV format" in response.json()["detail"]

        # Test unauthorized access
        response = await client.get("/api/data/next_unannotated")
        assert response.status_code == 401

    async def test_empty_database(
        self,
        client: AsyncClient,
        test_user: "User"
    ):
        response = await client.get(
            "/api/data/next_unannotated",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "No unannotated videos available"