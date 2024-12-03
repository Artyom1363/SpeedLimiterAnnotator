# Path: backend/tests/test_annotations.py
import pytest
from httpx import AsyncClient
from datetime import datetime
from .test_data import get_test_video_path, get_test_speed_data_path, get_test_button_data_path

class TestAnnotations:
    async def test_annotation_workflow(self, client: AsyncClient, test_user):
        """Test complete annotation workflow"""
        # 1. Upload test video and data
        with open(get_test_video_path(), 'rb') as video_file:
            video_response = await client.post(
                "/api/data/upload_video",
                files={"video_file": ("test_video.mp4", video_file, "video/mp4")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )
            video_id = video_response.json()["video_id"]

        # Upload associated data
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            await client.post(
                f"/api/data/upload_csv",
                files={"csv_file": ("speed_data.csv", speed_file, "text/csv")},
                params={"video_id": video_id},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        with open(get_test_button_data_path(), 'rb') as button_file:
            await client.post(
                f"/api/data/upload_button_data",
                files={"button_data_file": ("button_data.txt", button_file, "text/plain")},
                params={"video_id": video_id},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )

        # 2. Start annotation
        start_response = await client.post(
            f"/api/annotations/{video_id}/start",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert start_response.status_code == 200
        assert start_response.json()["status"] == "started"

        # 3. Add annotations
        annotations = [
            {
                "timestamp": 1717352241,
                "speed": 25.5,
                "button_state": 0,
                "error_detected": False
            },
            {
                "timestamp": 1717352242,
                "speed": 30.0,
                "button_state": 0,
                "error_detected": True
            }
        ]

        commit_response = await client.post(
            f"/api/annotations/{video_id}/commit",
            json={"annotations": annotations},
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert commit_response.status_code == 200
        commit_data = commit_response.json()
        assert commit_data["status"] == "committed"
        assert len(commit_data["annotations"]) == len(annotations)

        # 4. Verify annotations
        verify_response = await client.get(
            f"/api/annotations/{video_id}",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert len(verify_data["annotations"]) == len(annotations)
        
        # 5. Complete annotation
        complete_response = await client.post(
            f"/api/annotations/{video_id}/complete",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"

    async def test_annotation_locking(self, client: AsyncClient, test_user):
        """Test annotation locking mechanism"""
        # Create test video with data
        with open(get_test_video_path(), 'rb') as video_file:
            video_response = await client.post(
                "/api/data/upload_video",
                files={"video_file": ("test_video.mp4", video_file, "video/mp4")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )
            video_id = video_response.json()["video_id"]

        # Start annotation
        start_response = await client.post(
            f"/api/annotations/{video_id}/start",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert start_response.status_code == 200

        # Try to start annotation again (should fail)
        second_start_response = await client.post(
            f"/api/annotations/{video_id}/start",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert second_start_response.status_code == 409  # Conflict
        
        # Release lock
        unlock_response = await client.post(
            f"/api/annotations/{video_id}/unlock",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert unlock_response.status_code == 200