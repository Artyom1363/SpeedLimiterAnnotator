import React, { useState, useEffect, useRef } from 'react';
import { Box, Container, Button } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import Timeline from './Timeline';
import SpeedDisplay from './SpeedDisplay';
import SpeedOffsetControls from './SpeedOffsetControls';
import { useParams } from 'react-router-dom';
import axiosInstance from '../config/axios';
import SpeedChart from './SpeedChart';
import SegmentManager from './SegmentManager';
import { Segment } from '../types/segment';
import SegmentEditor from './SegmentEditor';

interface VideoData {
  video_id: string;
  speed_data: Array<{
    timestamp: number;
    speed: number;
  }>;
}

interface TimelineData {
  timestamp: number;
  speed: number;
}

interface VideoPlayerRef {
  currentTime: number;
}

interface SpeedDataPoint {
  timestamp: string | number;
  speed: string | number;
}

const VideoAnnotation: React.FC = () => {
  const { videoId } = useParams<{ videoId: string }>();
  const [currentTime, setCurrentTime] = useState(0);
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [videoDuration, setVideoDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [speedOffset, setSpeedOffset] = useState(0);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const videoRef = useRef<VideoPlayerRef>(null);
  const [segments, setSegments] = useState<Segment[]>(() => {
    const savedSegments = localStorage.getItem(`segments_${videoId}`);
    return savedSegments ? JSON.parse(savedSegments) : [];
  });
  const [activeSegment, setActiveSegment] = useState<Segment | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axiosInstance.get(`/api/data/${videoId}/data`);
        console.log('Received data:', response.data.data);
        
        if (!response.data.data.speed_data || !Array.isArray(response.data.data.speed_data)) {
          throw new Error('Invalid speed data format');
        }

        const validSpeedData = response.data.data.speed_data
          .map((point: SpeedDataPoint) => ({
            timestamp: Number(point.timestamp),
            speed: Number(point.speed)
          }))
          .filter((point: { timestamp: number; speed: number }) => 
            !isNaN(point.timestamp) && !isNaN(point.speed)
          );

        console.log('Processed speed data:', validSpeedData);

        setVideoData({
          video_id: response.data.data.video_id,
          speed_data: validSpeedData
        });
        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load video data');
        setIsLoading(false);
      }
    };
    fetchData();
  }, [videoId]);

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time);
    if (videoRef.current) {
      const currentVideoTime = videoRef.current.currentTime;
      if (Math.abs(currentVideoTime - time) > 0.5) {
        videoRef.current.currentTime = time;
      }
    }
  };

  const handleVideoReady = (duration: number) => {
    setVideoDuration(duration);
  };

  const handleOffsetChange = (newOffset: number) => {
    setSpeedOffset(newOffset);
    setHasUnsavedChanges(true);
  };

  const saveChanges = async () => {
    if (!hasUnsavedChanges) return;

    try {
      await axiosInstance.post(`/api/annotations/${videoId}/shift_timestamp`, {
        timestamp_offset: Number(speedOffset.toFixed(1))
      });
      setHasUnsavedChanges(false);
    } catch (err) {
      console.error('Error saving changes:', err);
    }
  };

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedChanges]);

  const getCurrentSpeed = (time: number, speedData: TimelineData[]): number | null => {
    if (!speedData || !speedData.length) {
      return null;
    }

    const adjustedTime = time - speedOffset;
    const index = Math.floor(adjustedTime);
    
    if (index >= speedData.length) {
      return speedData[speedData.length - 1].speed;
    }
    if (index < 0) {
      return speedData[0].speed;
    }
    
    const fraction = adjustedTime - index;
    const currentPoint = speedData[index];
    const nextPoint = speedData[Math.min(index + 1, speedData.length - 1)];
    
    return currentPoint.speed + (nextPoint.speed - currentPoint.speed) * fraction;
  };

  const handleSegmentCreate = (segment: Segment) => {
    setSegments(prev => [...prev, segment]);
    setHasUnsavedChanges(true);
  };

  const handleSegmentDelete = (segmentId: string) => {
    setSegments(prev => prev.filter(segment => segment.id !== segmentId));
    if (activeSegment?.id === segmentId) {
      setActiveSegment(null);
    }
    setHasUnsavedChanges(true);
  };

  const handleSegmentSpeedChange = (segmentId: string, newSpeed: number) => {
    setSegments(prev => prev.map(segment => 
      segment.id === segmentId 
        ? { ...segment, adjustedSpeed: newSpeed }
        : segment
    ));
    setHasUnsavedChanges(true);
  };

  useEffect(() => {
    if (videoId && segments.length > 0) {
      localStorage.setItem(`segments_${videoId}`, JSON.stringify(segments));
    }
  }, [segments, videoId]);

  const getCurrentSpeedForSegment = (time: number, speedData: TimelineData[]): number | null => {
    const activeSegment = segments.find(
      segment => time >= segment.startTime && time <= segment.endTime
    );

    if (activeSegment?.type === 'speed_adjustment' && activeSegment.adjustedSpeed !== undefined) {
      return activeSegment.adjustedSpeed;
    }

    return getCurrentSpeed(time, speedData);
  };

  const handleSegmentClick = (segment: Segment) => {
    if (segment.type === 'speed_adjustment') {
      setActiveSegment(segment);
    }
  };

  const handleSegmentUpdate = (segmentId: string, startTime: number, endTime: number) => {
    setSegments(prev => prev.map(segment =>
      segment.id === segmentId
        ? { ...segment, startTime, endTime }
        : segment
    ));
    setHasUnsavedChanges(true);
  };

  if (isLoading) return <div>Loading...</div>;
  if (error || !videoData) return <div>Error: {error || 'Failed to load data'}</div>;

  const currentSpeed = getCurrentSpeedForSegment(currentTime, videoData.speed_data);

  console.log('Speed data length:', videoData.speed_data.length);

  return (
    <Container maxWidth="lg">
      <SpeedDisplay 
        speed={currentSpeed} 
        isIrrelevant={segments.some(
          segment => 
            segment.type === 'irrelevant' && 
            currentTime >= segment.startTime && 
            currentTime <= segment.endTime
        )} 
      />
      <Box sx={{ py: 4 }}>
        <VideoPlayer
          videoId={videoData.video_id}
          onTimeUpdate={handleTimeUpdate}
          onReady={handleVideoReady}
          ref={videoRef}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SpeedOffsetControls
            onOffsetChange={handleOffsetChange}
            currentOffset={speedOffset}
          />
          {hasUnsavedChanges && (
            <Button 
              variant="contained" 
              color="primary" 
              onClick={saveChanges}
            >
              Сохранить изменения
            </Button>
          )}
        </Box>
        <SegmentManager
          currentTime={currentTime}
          videoDuration={videoDuration}
          onSegmentCreate={handleSegmentCreate}
        />
        {activeSegment && activeSegment.type === 'speed_adjustment' && (
          <SegmentEditor
            key={activeSegment.id}
            segment={activeSegment}
            currentSpeed={getCurrentSpeed(activeSegment.startTime, videoData.speed_data) || 0}
            onSpeedChange={handleSegmentSpeedChange}
          />
        )}
        <Timeline
          currentTime={currentTime}
          onTimeChange={handleTimeUpdate}
          videoDuration={videoDuration}
          segments={segments}
          onSegmentDelete={handleSegmentDelete}
          getCurrentSpeed={(time) => getCurrentSpeed(time, videoData.speed_data)}
          onSegmentClick={handleSegmentClick}
          activeSegment={activeSegment}
          onSegmentUpdate={handleSegmentUpdate}
        />
        <SpeedChart
          speedData={videoData.speed_data}
          currentTime={currentTime}
          videoDuration={videoDuration}
          speedOffset={speedOffset}
          segments={segments}
        />
      </Box>
    </Container>
  );
};

export default VideoAnnotation;
export {};