### Full API Description for the Electric Scooter Speed Control System with Manual Video Annotation

---

### **1. Authorization and Authentication (Auth API)**

Endpoints for user authorization and authentication to ensure secure access to the system.

#### 1.1 **User Registration**  
- **POST /api/auth/register**  
  - **Description**: Register a new user.  
  - **Parameters**:  
    - `username` (string): Username.  
    - `email` (string): User's email address.  
    - `password` (string): Password.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "User registered successfully"
    }
    ```
  
#### 1.2 **User Login**  
- **POST /api/auth/login**  
  - **Description**: Authenticate user and obtain access token.  
  - **Parameters**:  
    - `email` (string): User's email address.  
    - `password` (string): User's password.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "access_token": "your_jwt_token",
      "refresh_token": "your_refresh_token"
    }
    ```
  
#### 1.3 **Refresh Token**  
- **POST /api/auth/refresh_token**  
  - **Description**: Refresh the access token using a refresh token.  
  - **Parameters**:  
    - `refresh_token` (string): Refresh token.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "access_token": "new_jwt_token"
    }
    ```

---

### **2. Data Upload and Management (Data Upload API)**

Endpoints for uploading and managing video files, as well as handling CSV data for speed and geolocation.

#### 2.1 **Upload Video**  
- **POST /api/data/upload_video**  
  - **Description**: Upload a video file to the system (e.g., to Yandex Cloud S3).  
  - **Parameters**:  
    - `video_file` (file): Video file.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "video_id": "string",
      "message": "Video uploaded successfully"
    }
    ```

#### 2.2 **Upload Speed and Geolocation CSV Data**  
- **POST /api/data/upload_csv**  
  - **Description**: Upload a CSV file containing speed and geolocation data for a video.  
  - **Parameters**:  
    - `video_id` (string): The video ID to associate with the CSV file.  
    - `csv_file` (file): The CSV file containing speed and geolocation data.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "CSV data uploaded successfully"
    }
    ```

#### 2.3 **Upload Button Data**  
- **POST /api/data/upload_button_data**  
  - **Description**: Upload button press data (TXT file, where each line is 0 or 1 indicating the button state).  
  - **Parameters**:  
    - `video_id` (string): The video ID to associate with the button data.  
    - `button_data_file` (file): The button press data file.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "Button data uploaded successfully"
    }
    ```

---

### **3. Annotation and Synchronization Management (Annotation API)**

Endpoints for managing video annotations, including the ability to edit and commit annotations.

#### 3.1 **Get the First Available Unannotated Video**  
- **GET /api/videos/next_unannotated**  
  - **Description**: Retrieve the first unannotated and unblocked video.  
  - **Response**:  
    ```json
    {
      "video_id": "string",
      "title": "Video title",
      "upload_date": "timestamp",
      "status": "unannotated",
      "locked_by": null,
      "lock_time": null
    }
    ```

#### 3.2 **Lock Video for Annotation**  
- **POST /api/annotations/{video_id}/lock**  
  - **Description**: Lock a video for annotation.  
  - **Parameters**:  
    - `video_id` (string): The video ID to lock.  
  - **Response**:  
    ```json
    {
      "status": "locked",
      "video_id": "string",
      "locked_by": "user_id",
      "lock_time": "timestamp"
    }
    ```

#### 3.3 **Start Annotation (Manual Labeling)**  
- **POST /api/annotations/{video_id}/start**  
  - **Description**: Start annotating the video.  
  - **Parameters**:  
    - `video_id` (string): The video ID to start annotating.  
  - **Response**:  
    ```json
    {
      "status": "started",
      "video_id": "string",
      "user_id": "user_id"
    }
    ```

#### 3.4 **Commit Annotations**  
- **POST /api/annotations/{video_id}/commit**  
  - **Description**: Commit the annotations for a video.  
  - **Parameters**:  
    - `video_id` (string): The video ID to commit annotations for.  
    - `annotations` (array): A list of annotation data (e.g., timestamp, speed, button state).  
  - **Response**:  
    ```json
    {
      "status": "committed",
      "video_id": "string",
      "annotations": [
        { "timestamp": "int", "speed": "float", "button_state": "int" }
      ]
    }
    ```

#### 3.5 **Unlock Video After Annotation**  
- **POST /api/annotations/{video_id}/unlock**  
  - **Description**: Unlock a video after annotation is complete.  
  - **Parameters**:  
    - `video_id` (string): The video ID to unlock.  
  - **Response**:  
    ```json
    {
      "status": "unlocked",
      "video_id": "string"
    }
    ```

---

### **4. Inference Model (Inference API)**

Endpoints for working with the pre-trained machine learning model to perform inference (predictions) on videos.

#### 4.1 **Run Inference on a Video**  
- **POST /api/inference/run**  
  - **Description**: Run inference on a video using the pre-trained model.  
  - **Parameters**:  
    - `video_id` (string): The video ID to run inference on.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "video_id": "string",
      "predictions": [
        { "timestamp": "int", "predicted_speed": "float", "confidence": "float" }
      ]
    }
    ```

---

### **5. Geolocation and Map Display (Geolocation API)**

Endpoints for working with geolocation data and displaying it on a map.

#### 5.1 **Get Geolocation Data for a Video**  
- **GET /api/geolocation/{video_id}**  
  - **Description**: Retrieve geolocation data for a video to display on a map.  
  - **Parameters**:  
    - `video_id` (string): The video ID to get geolocation data for.  
  - **Response**:  
    ```json
    {
      "video_id": "string",
      "locations": [
        { "timestamp": "int", "latitude": "float", "longitude": "float" }
      ]
    }
    ```

---

### **6. User Management API (User Management API)**

Endpoints for managing user data and roles.

#### 6.1 **Get User Information**  
- **GET /api/users/{user_id}**  
  - **Description**: Get information about a user.  
  - **Parameters**:  
    - `user_id` (string): The user ID.  
  - **Response**:  
    ```json
    {
      "user_id": "string",
      "username": "string",
      "email": "string",
      "role": "string"
    }
    ```

#### 6.2 **Update User Information**  
- **PUT /api/users/{user_id}**  
  - **Description**: Update user information.  
  - **Parameters**:  
    - `username` (string): Username.  
    - `email` (string): Email address.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "User info updated"
    }
    ```

---

### **7. Video Locking and Annotation Management (Video Annotation API)**

Endpoints for working with video locking, unlocking, and annotations.

#### 7.1 **Get the First Available Unannotated Video**  
- **GET /api/videos/next_unannotated**  
  - **Description**: Retrieve the first unannotated and unblocked video.  
  - **Response**:  
    ```json
    {
      "video_id": "string",
      "title": "Video title",
      "upload_date": "timestamp",
      "status": "unannotated",
      "locked_by": null,
      "

lock_time": null
    }
    ```

#### 7.2 **Lock Video for Annotation**  
- **POST /api/annotations/{video_id}/lock**  
  - **Description**: Lock a video for annotation, preventing other users from annotating it simultaneously.  
  - **Parameters**:  
    - `video_id` (string): The video ID to lock.  
  - **Response**:  
    ```json
    {
      "status": "locked",
      "video_id": "string",
      "locked_by": "user_id",
      "lock_time": "timestamp"
    }
    ```

#### 7.3 **Unlock Video After Annotation**  
- **POST /api/annotations/{video_id}/unlock**  
  - **Description**: Unlock the video after annotation is complete.  
  - **Parameters**:  
    - `video_id` (string): The video ID to unlock.  
  - **Response**:  
    ```json
    {
      "status": "unlocked",
      "video_id": "string"
    }
    ```

---