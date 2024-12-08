import React, { useState, useEffect, useRef } from 'react';
import { Box, Container } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import Timeline from './Timeline';
import SpeedDisplay from './SpeedDisplay';
import { useParams } from 'react-router-dom';
import axiosInstance from '../config/axios';

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

const VideoAnnotation: React.FC = () => {
  const { videoId } = useParams<{ videoId: string }>();
  const [currentTime, setCurrentTime] = useState(0);
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<VideoPlayerRef>(null);

  const getCurrentSpeed = (time: number, speedData: TimelineData[]): number | null => {
    if (!speedData.length) return null;

    const index = speedData.findIndex(point => point.timestamp > time);
    
    if (index === -1) return speedData[speedData.length - 1].speed;
    if (index === 0) return speedData[0].speed;
    
    const prevPoint = speedData[index - 1];
    const nextPoint = speedData[index];
    
    const timeDiff = nextPoint.timestamp - prevPoint.timestamp;
    const speedDiff = nextPoint.speed - prevPoint.speed;
    const timeOffset = time - prevPoint.timestamp;
    
    return prevPoint.speed + (speedDiff * timeOffset) / timeDiff;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axiosInstance.get(`/api/data/${videoId}/data`);
        setVideoData({
          video_id: response.data.data.video_id,
          speed_data: response.data.data.speed_data
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
    if (videoRef.current && Math.abs(videoRef.current.currentTime - time) > 0.5) {
      videoRef.current.currentTime = time;
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error || !videoData) return <div>Error: {error || 'Failed to load data'}</div>;

  const currentSpeed = getCurrentSpeed(currentTime, videoData.speed_data);

  return (
    <Container maxWidth="lg">
      <SpeedDisplay speed={currentSpeed} />
      <Box sx={{ py: 4 }}>
        <VideoPlayer
          videoId={videoData.video_id}
          onTimeUpdate={handleTimeUpdate}
          ref={videoRef}
        />
        <Timeline
          speedData={videoData.speed_data}
          currentTime={currentTime}
          onTimeChange={handleTimeUpdate}
        />
      </Box>
    </Container>
  );
};

export default VideoAnnotation;
export {};