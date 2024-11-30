# Path: backend/tests/test_data/__init__.py
from pathlib import Path

# Получаем путь к директории с тестовыми данными
TEST_DATA_DIR = Path(__file__).parent

def get_test_video_path() -> Path:
    """Returns path to test video file."""
    return TEST_DATA_DIR / "test.mp4"

def get_test_speed_data_path() -> Path:
    """Returns path to test speed data CSV file."""
    return TEST_DATA_DIR / "speed_data.csv"

def get_test_button_data_path() -> Path:
    """Returns path to test button data file."""
    return TEST_DATA_DIR / "button_data.txt"