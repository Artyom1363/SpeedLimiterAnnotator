### Sprint 1: Developing Backend Architecture (Backend API)
**Goal**: Create the initial backend structure to handle basic requests and data storage.
**Technologies**: Python, FastAPI, PostgreSQL, Docker
**MVP**: REST API with basic endpoints for data upload (video, CSV, TXT), metadata storage in PostgreSQL, Docker containerization.
- Create a basic skeleton using FastAPI.
- Set up PostgreSQL database for storing metadata and upload parameters.
- Set up Docker containers for the backend and the database.
- Implement CRUD operations for videos and related data (file metadata).

### Sprint 2: Developing Initial Data Upload Interface (Frontend)
**Goal**: Create a user interface for uploading videos and data files.
**Technologies**: React.js, Redux
**MVP**: A form to upload video, CSV, and TXT files. The upload status should be displayed on-screen.
- Set up a React application and create a basic interface.
- Implement forms for video and file uploads using Redux for state management.
- Send the data to the backend via API (upload request).

### Sprint 3: DevOps and Environment Setup
**Goal**: Set up the infrastructure to integrate all components.
**Technologies**: Docker, Nginx, Yandex Cloud S3
**MVP**: Containerized application including backend, frontend, and proxying via Nginx.
- Set up Docker Compose for all components (backend, frontend, database).
- Set up Nginx as a reverse proxy.
- Set up integration with Yandex Cloud S3 for video storage.

### Sprint 4: Implementing Video Playback Interface and Synchronization (Frontend)
**Goal**: Create an interface for video playback and display speed and button event timelines.
**Technologies**: React.js, Video.js, Chart.js/D3.js
**MVP**: A video player that synchronizes video playback with speed and button event graphs.
- Integrate the Video.js library for video playback.
- Integrate graphs using Chart.js or D3.js to display speed and button event data.
- Create a basic interface to display all data synchronized with the video.

### Sprint 5: Logic for Uploading and Storing Files in Yandex Cloud S3 (Backend)
**Goal**: Set up file uploads and store video files in Yandex Cloud S3.
**Technologies**: Python, boto3, Yandex Cloud S3
**MVP**: Video upload function to S3 and extracting its metadata.
- Integrate boto3 to interact with Yandex Cloud S3.
- Set up methods to upload videos and other files to S3.
- Store file links and metadata in PostgreSQL.

### Sprint 6: Developing Data Synchronization Interface (Frontend)
**Goal**: Create an interface for synchronizing speed timeline data with video.
**Technologies**: React.js, Redux, D3.js
**MVP**: A slider to adjust the speed timeline relative to the video, enabling synchronized playback.
- Add a slider tool for manual synchronization of speed and button data with video.
- Display synchronization visually in the interface.

### Sprint 7: Creating Functionality for Editing and Saving Changes (Backend)
**Goal**: Develop an API to process user-made edits.
**Technologies**: Python, FastAPI, PostgreSQL
**MVP**: Endpoints for getting and saving annotation changes, with data versioning support.
- Create an API to save annotation changes, including time intervals and data adjustments.
- Support data versioning to track changes.

### Sprint 8: Interface for Editing Speed and Saving Annotations (Frontend)
**Goal**: Create an interface for editing speed, selecting intervals, and saving changes.
**Technologies**: React.js, Redux
**MVP**: Ability to edit speed for selected intervals, save locally, and send to backend.
- Develop an interface for selecting intervals on the timeline.
- Implement speed changes for the selected interval.
- Save changes locally and send them to the backend via a "Save" button.

### Sprint 9: Model Inference Integration and Testing (Inference)
**Goal**: Integrate the existing model inference code.
**Technologies**: Python, Celery, Redis
**MVP**: Run inference on uploaded videos and integrate with annotation results.
- Set up Celery and Redis for asynchronous inference tasks.
- Integrate model code and run inference on selected videos.
- Store inference results and send information on problematic sections to the frontend.

### Sprint 10: Displaying Problematic Areas in Interface (Frontend)
**Goal**: Display problematic areas detected by the model and allow for additional annotations.
**Technologies**: React.js, Chart.js/D3.js
**MVP**: Highlight problematic areas on the timeline for easier annotation.
- Display moments on the timeline where the model detects possible errors.
- Provide quick navigation to problematic sections.

### Sprint 11: Saving Changes with Author Tracking (Backend)
**Goal**: Add support for saving information about the author of changes.
**Technologies**: Python, FastAPI, PostgreSQL
**MVP**: Ability to save the author of each change for annotation tracking.
- Expand the database schema to store information about the authors of changes.
- Modify API endpoints to save information about users and their actions.

### Sprint 12: Adding Geolocation on the Map (Frontend)
**Goal**: Create an interface to display geolocation parameters on a map.
**Technologies**: React.js, Leaflet.js
**MVP**: Visualize geolocation data synchronized with the video.
- Integrate Leaflet.js for working with maps.
- Display movement route on the map, synchronized with video playback.
- Integrate the map into the annotation interface.

### Sprint 13: Final Integration and System Testing
**Goal**: Test all system components and ensure their full integration.
**Technologies**: Python, React.js, Docker, Selenium (for e2e testing)
**MVP**: A fully functional system ready for use.
- Conduct integration testing to verify interactions between frontend and backend.
- Test system performance and identify potential bottlenecks.
- Perform end-to-end testing with Selenium to validate user scenarios.
- Fix identified issues and bugs.

