import React, { useState, useEffect, useRef } from 'react';
import { Box, Container } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import Timeline from './Timeline';
import SpeedDisplay from './SpeedDisplay';
import { useParams } from 'react-router-dom';
import axiosInstance from '../config/axios';
import SpeedChart from './SpeedChart';

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
  const videoRef = useRef<VideoPlayerRef>(null);

  const getCurrentSpeed = (time: number, speedData: TimelineData[]): number | null => {
    if (!speedData || !speedData.length) {
      return null;
    }

    const index = Math.floor(time);
    if (index >= speedData.length) {
      return speedData[speedData.length - 1].speed;
    }
    if (index < 0) {
      return speedData[0].speed;
    }
    
    const fraction = time - index;
    const currentPoint = speedData[index];
    const nextPoint = speedData[Math.min(index + 1, speedData.length - 1)];
    
    return currentPoint.speed + (nextPoint.speed - currentPoint.speed) * fraction;
  };

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
    if (videoRef.current && Math.abs(videoRef.current.currentTime - time) > 0.5) {
      videoRef.current.currentTime = time;
    }
  };

  const handleVideoReady = (duration: number) => {
    setVideoDuration(duration);
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
          onReady={handleVideoReady}
          ref={videoRef}
        />
        <Timeline
          currentTime={currentTime}
          onTimeChange={handleTimeUpdate}
          videoDuration={videoDuration}
        />
        <SpeedChart 
          speedData={videoData.speed_data}
          currentTime={currentTime}
          videoDuration={videoDuration}
        />
      </Box>
    </Container>
  );
};

export default VideoAnnotation;
export {};