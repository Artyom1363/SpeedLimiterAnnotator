### **1. Authorization and Authentication (Auth API)**

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

#### 2.4 **Add Timestamps for Button Data**  
- **POST /api/data/add_button_timestamp**  
  - **Description**: Add timestamp information to the button data file.  
  - **Parameters**:  
    - `video_id` (string): The video ID to associate with the timestamped button data.  
    - `button_data_with_timestamps` (array): Array of button press data with associated timestamps. Each entry contains `timestamp` (int) and `button_state` (int).  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "Button data with timestamps added successfully"
    }
    ```

#### 2.5 **Add Timestamps for Video Data**  
- **POST /api/data/add_video_timestamp**  
  - **Description**: Add or adjust timestamps for video data to synchronize with other data (such as button data or geolocation).  
  - **Parameters**:  
    - `video_id` (string): The video ID to add timestamps for.  
    - `video_data_with_timestamps` (array): Array of video data with timestamps. Each entry contains `timestamp` (int) and `video_segment` (string).  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "Video timestamps added/adjusted successfully"
    }
    ```

---

### **3. Annotation and Synchronization Management (Annotation API)**

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

#### 3.2 **Start Annotation (Lock and Start Annotating)**  
- **POST /api/annotations/{video_id}/start**  
  - **Description**: Start annotating a video. The video will be locked to prevent other users from annotating it at the same time.  
  - **Parameters**:  
    - `video_id` (string): The video ID to start annotating.  
  - **Response (Success)**:  
    ```json
    {
      "status": "started",
      "video_id": "string",
      "user_id": "user_id",
      "locked_by": "user_id",
      "lock_time": "timestamp"
    }
    ```
  - **Response (Error - Video Locked)**:  
    ```json
    {
      "status": "error",
      "message": "Video is already locked by another user"
    }
    ```

#### 3.3 **Commit Annotations**  
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

#### 3.4 **Unlock Video After Annotation**  
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

#### 3.5 **Shift Video Timestamp**  
- **POST /api/annotations/{video_id}/shift_timestamp**  
  - **Description**: Shift the video timestamps by a given offset to synchronize it with other data (e.g., button data or speed data).  
  - **Parameters**:  
    - `video_id` (string): The video ID whose timestamp needs to be shifted.  
    - `timestamp_offset` (float): The amount of time (in seconds) to shift the video timestamps.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "Video timestamps shifted successfully"
    }
    ```

#### 3.6 **Shift Button Data Timestamp**  
- **POST /api/annotations/{video_id}/shift_button_timestamp**  
  - **Description**: Shift the button data timestamps by a given offset.  
  - **Parameters**:  
    - `video_id` (string): The video ID whose button data timestamps need to be shifted.  
    - `timestamp_offset` (float): The amount of time (in seconds) to shift the button data timestamps.  
  - **Response**:  
    ```json
    {
      "status": "success",
      "message": "Button data timestamps shifted successfully"
    }
    ```

---

### **4. Inference Model (Inference API)**

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
      "

email": "string",
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