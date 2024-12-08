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
  const [segments, setSegments] = useState<Segment[]>([]);

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
    if (videoRef.current && Math.abs(videoRef.current.currentTime - time) > 1.0) {
      const currentVideoTime = videoRef.current.currentTime;
      const targetTime = Math.max(0, Math.min(time, videoDuration));
      const step = (targetTime - currentVideoTime) / 10;
      
      let frame = 0;
      const animate = () => {
        if (frame < 10 && videoRef.current) {
          videoRef.current.currentTime = currentVideoTime + step * frame;
          frame++;
          requestAnimationFrame(animate);
        }
      };
      animate();
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
    setHasUnsavedChanges(true);
  };

  if (isLoading) return <div>Loading...</div>;
  if (error || !videoData) return <div>Error: {error || 'Failed to load data'}</div>;

  const currentSpeed = getCurrentSpeed(currentTime, videoData.speed_data);

  console.log('Speed data length:', videoData.speed_data.length);

  return (
    <Container maxWidth="lg">
      <SpeedDisplay speed={currentSpeed} />
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
        <Timeline
          currentTime={currentTime}
          onTimeChange={handleTimeUpdate}
          videoDuration={videoDuration}
          segments={segments}
          onSegmentDelete={handleSegmentDelete}
        />
        <SpeedChart 
          speedData={videoData.speed_data}
          currentTime={currentTime}
          videoDuration={videoDuration}
          speedOffset={speedOffset}
        />
        <SegmentManager
          currentTime={currentTime}
          videoDuration={videoDuration}
          onSegmentCreate={handleSegmentCreate}
        />
      </Box>
    </Container>
  );
};

export default VideoAnnotation;
export {};