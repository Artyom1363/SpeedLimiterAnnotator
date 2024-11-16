# Video Annotation Backend API Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Data Models](#data-models)
5. [API Endpoints](#api-endpoints)
    - [1. Root Endpoint](#1-root-endpoint)
    - [2. Videos Endpoints](#2-videos-endpoints)
        - [a. Upload Video Metadata](#a-upload-video-metadata)
        - [b. List Videos](#b-list-videos)
        - [c. Get Video by ID](#c-get-video-by-id)
        - [d. Delete Video by ID](#d-delete-video-by-id)
        - [e. Upload Video File](#e-upload-video-file)
6. [Error Handling](#error-handling)
7. [Examples](#examples)
    - [1. Upload Video Metadata](#1-upload-video-metadata)
    - [2. List Videos](#2-list-videos)
    - [3. Get Video by ID](#3-get-video-by-id)
    - [4. Delete Video by ID](#4-delete-video-by-id)
    - [5. Upload Video File](#5-upload-video-file)
8. [Interactive Documentation](#interactive-documentation)
9. [Contact & Support](#contact--support)

---

## Introduction

Welcome to the **Video Annotation Backend API** documentation. This API is designed to support a video annotation system tailored for speed control on electric scooters. It enables functionalities such as uploading videos, managing video metadata, and handling file uploads. The backend is built using **FastAPI**, **Python**, and **PostgreSQL**, and is containerized with **Docker**.

---

## Base URL

All API endpoints are prefixed with the base URL:

```
http://46.8.29.217:8000
```


---

## Authentication

**Note:** Currently, the API does **not** implement authentication mechanisms. For production environments, it's highly recommended to secure your endpoints using authentication methods like **JWT (JSON Web Tokens)** or **OAuth2**.

---

## Data Models

### Video Model

The `Video` model represents a video file and its associated metadata.

| Field          | Type      | Description                                 |
|----------------|-----------|---------------------------------------------|
| `id`           | `integer` | Unique identifier for the video (auto-incremented). |
| `filename`     | `string`  | Name of the video file (must be unique).    |
| `upload_time`  | `datetime`| Timestamp when the video was uploaded.      |
| `file_metadata`| `string`  | Additional metadata related to the video (optional). |

---

## API Endpoints

### 1. Root Endpoint

- **URL:** `/`
- **Method:** `GET`
- **Description:** Welcome message to confirm the API is running.

#### Response

- **Status Code:** `200 OK`
- **Body:**
  
  ```json
  {
    "message": "Welcome to the Video Annotation Backend API"
  }
  ```

---

### 2. Videos Endpoints

#### a. Upload Video Metadata

- **URL:** `/videos/`
- **Method:** `POST`
- **Description:** Upload metadata for a new video.

- **Request Body:**
  
  - **Content-Type:** `application/json`
  
  | Field          | Type      | Required | Description                              |
  |----------------|-----------|----------|------------------------------------------|
  | `filename`     | `string`  | Yes      | Name of the video file (must be unique). |
  | `file_metadata`| `string`  | No       | Additional metadata for the video.       |

- **Example Request:**

  ```json
  {
    "filename": "scooter_run_01.mp4",
    "file_metadata": "Initial test run at 5 mph."
  }
  ```

- **Response:**
  
  - **Status Code:** `200 OK`
  - **Body:**
    
    ```json
    {
      "id": 1,
      "filename": "scooter_run_01.mp4",
      "upload_time": "2024-04-27T12:34:56.789Z",
      "file_metadata": "Initial test run at 5 mph."
    }
    ```

#### b. List Videos

- **URL:** `/videos/`
- **Method:** `GET`
- **Description:** Retrieve a list of all uploaded videos.

- **Query Parameters:**

  | Parameter | Type    | Description                                     |
  |-----------|---------|-------------------------------------------------|
  | `skip`    | `integer` | Number of records to skip for pagination (default: `0`). |
  | `limit`   | `integer` | Maximum number of records to return (default: `100`).  |

- **Example Request:**

  ```
  GET /videos/?skip=0&limit=10
  ```

- **Response:**
  
  - **Status Code:** `200 OK`
  - **Body:**
    
    ```json
    [
      {
        "id": 1,
        "filename": "scooter_run_01.mp4",
        "upload_time": "2024-04-27T12:34:56.789Z",
        "file_metadata": "Initial test run at 5 mph."
      },
      {
        "id": 2,
        "filename": "scooter_run_02.mp4",
        "upload_time": "2024-04-28T09:20:15.123Z",
        "file_metadata": "Second test run at 7 mph."
      }
      // ... more videos
    ]
    ```

#### c. Get Video by ID

- **URL:** `/videos/{video_id}`
- **Method:** `GET`
- **Description:** Retrieve details of a specific video by its ID.

- **Path Parameters:**

  | Parameter   | Type      | Description                   |
  |-------------|-----------|-------------------------------|
  | `video_id`  | `integer` | Unique identifier of the video. |

- **Example Request:**

  ```
  GET /videos/1
  ```

- **Response:**
  
  - **Status Code:** `200 OK`
  - **Body:**
    
    ```json
    {
      "id": 1,
      "filename": "scooter_run_01.mp4",
      "upload_time": "2024-04-27T12:34:56.789Z",
      "file_metadata": "Initial test run at 5 mph."
    }
    ```

- **Error Response:**
  
  - **Status Code:** `404 Not Found`
  - **Body:**
    
    ```json
    {
      "detail": "Video not found"
    }
    ```

#### d. Delete Video by ID

- **URL:** `/videos/{video_id}`
- **Method:** `DELETE`
- **Description:** Delete a specific video by its ID.

- **Path Parameters:**

  | Parameter   | Type      | Description                   |
  |-------------|-----------|-------------------------------|
  | `video_id`  | `integer` | Unique identifier of the video. |

- **Example Request:**

  ```
  DELETE /videos/1
  ```

- **Response:**
  
  - **Status Code:** `200 OK`
  - **Body:**
    
    ```json
    {
      "id": 1,
      "filename": "scooter_run_01.mp4",
      "upload_time": "2024-04-27T12:34:56.789Z",
      "file_metadata": "Initial test run at 5 mph."
    }
    ```

- **Error Response:**
  
  - **Status Code:** `404 Not Found`
  - **Body:**
    
    ```json
    {
      "detail": "Video not found"
    }
    ```

#### e. Upload Video File

- **URL:** `/videos/upload-file/`
- **Method:** `POST`
- **Description:** Upload a video file along with its metadata.

- **Request Body:**
  
  - **Content-Type:** `multipart/form-data`
  
  | Field          | Type       | Required | Description                              |
  |----------------|------------|----------|------------------------------------------|
  | `filename`     | `string`   | Yes      | Name of the video file (must be unique). |
  | `file_metadata`| `string`   | No       | Additional metadata for the video.       |
  | `file`         | `file`     | Yes      | The video file to upload.                |

- **Example Request:**

  Using `curl`:

  ```bash
  curl -X POST "http://<your-server-ip>:8000/videos/upload-file/" \
       -H "accept: application/json" \
       -H "Content-Type: multipart/form-data" \
       -F "filename=scooter_run_03.mp4" \
       -F "file_metadata=Third test run at 10 mph." \
       -F "file=@/path/to/scooter_run_03.mp4"
  ```

- **Response:**
  
  - **Status Code:** `200 OK`
  - **Body:**
    
    ```json
    {
      "id": 3,
      "filename": "scooter_run_03.mp4",
      "upload_time": "2024-04-29T14:22:30.456Z",
      "file_metadata": "Third test run at 10 mph."
    }
    ```

- **Error Responses:**
  
  - **Missing `python-multipart` Dependency:**
    
    If `python-multipart` is not installed, you'll encounter the following error:
    
    ```
    RuntimeError: Form data requires "python-multipart" to be installed.
    You can install "python-multipart" with:
    
    pip install python-multipart
    ```
    
    **Solution:** Ensure `python-multipart` is included in your `requirements.txt` and rebuild your Docker containers.

  - **Validation Errors:**
    
    If required fields are missing or invalid.
    
    ```json
    {
      "detail": [
        {
          "loc": ["body", "filename"],
          "msg": "field required",
          "type": "value_error.missing"
        },
        {
          "loc": ["body", "file"],
          "msg": "field required",
          "type": "value_error.missing"
        }
      ]
    }
    ```

---

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of an API request.

| Status Code | Meaning                     | Description                                     |
|-------------|-----------------------------|-------------------------------------------------|
| `200 OK`    | Success                     | The request was successfully processed.         |
| `404 Not Found` | Resource not found        | The requested resource does not exist.          |
| `400 Bad Request` | Invalid request          | The request was malformed or contained invalid data. |
| `500 Internal Server Error` | Server error | An unexpected error occurred on the server.      |

**Error Response Format:**

```json
{
  "detail": "Error message describing what went wrong."
}
```

---

## Examples

### 1. Upload Video Metadata

**Request:**

```
POST /videos/
Content-Type: application/json

{
  "filename": "scooter_run_04.mp4",
  "file_metadata": "Fourth test run at 12 mph."
}
```

**Response:**

```json
{
  "id": 4,
  "filename": "scooter_run_04.mp4",
  "upload_time": "2024-04-30T10:15:20.789Z",
  "file_metadata": "Fourth test run at 12 mph."
}
```

---

### 2. List Videos

**Request:**

```
GET /videos/?skip=0&limit=5
```

**Response:**

```json
[
  {
    "id": 1,
    "filename": "scooter_run_01.mp4",
    "upload_time": "2024-04-27T12:34:56.789Z",
    "file_metadata": "Initial test run at 5 mph."
  },
  {
    "id": 2,
    "filename": "scooter_run_02.mp4",
    "upload_time": "2024-04-28T09:20:15.123Z",
    "file_metadata": "Second test run at 7 mph."
  },
  {
    "id": 3,
    "filename": "scooter_run_03.mp4",
    "upload_time": "2024-04-29T14:22:30.456Z",
    "file_metadata": "Third test run at 10 mph."
  },
  {
    "id": 4,
    "filename": "scooter_run_04.mp4",
    "upload_time": "2024-04-30T10:15:20.789Z",
    "file_metadata": "Fourth test run at 12 mph."
  }
]
```

---

### 3. Get Video by ID

**Request:**

```
GET /videos/2
```

**Response:**

```json
{
  "id": 2,
  "filename": "scooter_run_02.mp4",
  "upload_time": "2024-04-28T09:20:15.123Z",
  "file_metadata": "Second test run at 7 mph."
}
```

---

### 4. Delete Video by ID

**Request:**

```
DELETE /videos/3
```

**Response:**

```json
{
  "id": 3,
  "filename": "scooter_run_03.mp4",
  "upload_time": "2024-04-29T14:22:30.456Z",
  "file_metadata": "Third test run at 10 mph."
}
```

---

### 5. Upload Video File

**Request:**

```bash
curl -X POST "http://<your-server-ip>:8000/videos/upload-file/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "filename=scooter_run_05.mp4" \
     -F "file_metadata=Fifth test run at 15 mph." \
     -F "file=@/path/to/scooter_run_05.mp4"
```

**Response:**

```json
{
  "id": 5,
  "filename": "scooter_run_05.mp4",
  "upload_time": "2024-05-01T08:30:45.678Z",
  "file_metadata": "Fifth test run at 15 mph."
}
```

---

## Interactive Documentation

FastAPI automatically generates interactive API documentation using **Swagger UI** and **ReDoc**. You can access these interfaces to explore and test your API endpoints.

- **Swagger UI:** [http://<your-server-ip>:8000/docs](http://<your-server-ip>:8000/docs)
- **ReDoc:** [http://<your-server-ip>:8000/redoc](http://<your-server-ip>:8000/redoc)

**Usage:**

1. Open your web browser.
2. Navigate to the desired URL (e.g., Swagger UI).
3. Interact with the API by expanding the endpoints and executing requests directly from the interface.
