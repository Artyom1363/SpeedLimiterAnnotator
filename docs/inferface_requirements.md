# Video Annotation System for Electric Scooter Speed Control

## System Overview

This document outlines the requirements for a video annotation interface designed for validating and correcting electric scooter speed data. The system enables synchronization of ride recordings with corresponding speed data and allows marking segments where speed corrections are needed or data is irrelevant.

### Purpose
- Review electric scooter ride recordings
- Synchronize video footage with speed data
- Mark segments with incorrect data
- Adjust speed values for selected segments
- Prepare datasets for machine learning model training

### Primary Use Cases
1. Retrieving unannotated video and speed data from the system
2. Synchronizing speed data recording start with motion onset in video
3. Marking segments with incorrect data
4. Adjusting speed values for selected segments
5. Saving annotated data

## Interface Requirements

### 1. Core Components

#### 1.1 Main Screen
- Video player
- Unified timeline below the video
- Current speed display window
- Segment marking type selector

#### 1.2 Control Elements
- Play/pause buttons
- Common cursor for video and speed data
- Speed data offset controls:
  - Left/right shift buttons
  - Offset value input field (in seconds)

### 2. Segment Management

#### 2.1 Segment Markers
- Irrelevant data marker (red color)
  - For marking segments to be excluded
- Speed adjustment marker (yellow color)
  - For segments requiring speed correction

#### 2.2 Segment Creation Process
1. During video playback:
   - User pauses the video
   - Selects marker type
   - Clicks create segment button
   - Left boundary sets at current cursor position
   - Right boundary automatically sets at +5 seconds

2. Segment Editing:
   - Both boundaries can be dragged with mouse
   - Cursor changes to resize when hovering over boundaries
   - Precise boundary adjustment via arrows or value input

#### 2.3 Segment Operations
- For irrelevant segments:
  - Visual dimming of the area
  - Option to delete segment
  
- For speed adjustment segments:
  - New speed value input field
  - Speed increment/decrement buttons (0.5 km/h steps)
  - Display of original and new speed values

### 3. Timeline Visualization
- Marked segments displayed directly on timeline
- Color coding for segment types
- On segment hover:
  - Information tooltip
  - Segment control buttons

### 4. Synchronization
- Synchronized movement during playback:
  - Video position
  - Timeline cursor
  - Current speed value
- Cursor movement updates:
  - Video position
  - Displayed speed
  - Modified speed display when cursor is in marked segment

### 5. Speed Display
- Large digital display of current speed
- When cursor enters marked segment:
  - Shows modified speed for speed adjustment segments
  - Shows "Irrelevant Data" label for irrelevant segments

## Technical Integration

### API Integration
- System retrieves data via `/api/annotations/next_unannotated` endpoint
- Automatic data loading on interface initialization
- Real-time synchronization of video and speed data
- Support for saving annotations back to the server

### Performance Requirements
- Smooth video playback
- Responsive timeline interaction
- Real-time speed value updates
- Efficient segment manipulation

## Data Handling
- Speed values in km/h
- Time measurements in seconds
- Segment boundaries with precision to 0.1 seconds
- Support for videos up to 15 minutes in length