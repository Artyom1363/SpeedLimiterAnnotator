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
            assert video_response.status_code == 201
            video_id = video_response.json()["video_id"]

        # Upload speed data
        with open(get_test_speed_data_path(), 'rb') as speed_file:
            speed_response = await client.post(
                f"/api/data/upload_csv/{video_id}",
                files={"csv_file": ("speed_data.csv", speed_file, "text/csv")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )
            assert speed_response.status_code == 200

        # Upload button data
        with open(get_test_button_data_path(), 'rb') as button_file:
            button_response = await client.post(
                f"/api/data/upload_button_data/{video_id}",
                files={"button_data_file": ("button_data.txt", button_file, "text/plain")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )
            assert button_response.status_code == 200

        # 2. Start annotation
        start_response = await client.post(
            f"/api/annotations/{video_id}/start",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert start_response.status_code == 200
        start_data = start_response.json()
        assert start_data["status"] == "started"

        # 3. Add annotations
        annotations = [
            {
                "timestamp": 1717352241,
                "speed": 25.5,
                "button_state": False
            }
        ]
        commit_response = await client.post(
            f"/api/annotations/{video_id}/commit",
            json=annotations,
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert commit_response.status_code == 200
        commit_data = commit_response.json()
        assert commit_data["status"] == "committed"
        assert len(commit_data["annotations"]) == len(annotations)

        # 4. Complete annotation
        unlock_response = await client.post(
            f"/api/annotations/{video_id}/unlock",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert unlock_response.status_code == 200

    async def test_annotation_locking(self, client: AsyncClient, test_user, test_user2):
        """Test annotation locking mechanism"""
        # Create test video
        with open(get_test_video_path(), 'rb') as video_file:
            video_response = await client.post(
                "/api/data/upload_video",
                files={"video_file": ("test_video.mp4", video_file, "video/mp4")},
                headers={"Authorization": f"Bearer {test_user.get_token()}"}
            )
            assert video_response.status_code == 201
            video_id = video_response.json()["video_id"]

        # First user starts annotation
        start_response = await client.post(
            f"/api/annotations/{video_id}/start",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert start_response.status_code == 200

        # Second user tries to start annotation (should fail)
        second_start_response = await client.post(
            f"/api/annotations/{video_id}/start",
            headers={"Authorization": f"Bearer {test_user2.get_token()}"}
        )
        assert second_start_response.status_code == 409
        assert "locked by another user" in second_start_response.json()["detail"]

        # Second user tries to commit annotations (should fail)
        annotations = [
            {
                "timestamp": 1717352241.0,
                "speed": 25.5,
                "button_state": False
            }
        ]
        commit_response = await client.post(
            f"/api/annotations/{video_id}/commit",
            json=annotations,
            headers={"Authorization": f"Bearer {test_user2.get_token()}"}
        )
        assert commit_response.status_code == 403

        # First user unlocks the video
        unlock_response = await client.post(
            f"/api/annotations/{video_id}/unlock",
            headers={"Authorization": f"Bearer {test_user.get_token()}"}
        )
        assert unlock_response.status_code == 200

        # Second user can now start annotation
        final_start_response = await client.post(
            f"/api/annotations/{video_id}/start",
            headers={"Authorization": f"Bearer {test_user2.get_token()}"}
        )
        assert final_start_response.status_code == 200