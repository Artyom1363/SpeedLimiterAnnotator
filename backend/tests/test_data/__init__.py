# Path: backend/tests/test_data/__init__.py
from pathlib import Path

# Get the directory containing test data
TEST_DATA_DIR = Path(__file__).parent

# Helper functions to get paths to test files
def get_test_video_path():
    return TEST_DATA_DIR / "test_video.mp4"

def get_test_speed_data_path():
    return TEST_DATA_DIR / "speed_data.csv"

def get_test_button_data_path():
    return TEST_DATA_DIR / "button_data.txt"