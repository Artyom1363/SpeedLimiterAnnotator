import React, { useState, useEffect } from 'react';
import { Box, Container, Typography } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import SpeedChart from './SpeedChart';
import { useParams } from 'react-router-dom';
import axiosInstance from '../config/axios';

interface VideoData {
  video_id: string;
  speed_data: Array<{
    timestamp: number;
    speed: number;
  }>;
}

const VideoAnnotation: React.FC = () => {
  const { videoId } = useParams<{ videoId: string }>();
  const [currentTime, setCurrentTime] = useState(0);
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentSpeed, setCurrentSpeed] = useState<number | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const response = await axiosInstance.get(`/api/data/${videoId}/data`);
        
        if (response.data.status === 'success') {
          setVideoData(response.data.data);
        } else {
          setError('Failed to load video data');
        }
      } catch (error) {
        console.error('Error fetching video data:', error);
        setError('Error loading video data');
      } finally {
        setIsLoading(false);
      }
    };

    if (videoId) {
      fetchData();
    }
  }, [videoId]);

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time);
    if (videoData?.speed_data) {
      const currentSpeedData = videoData.speed_data.find(
        data => Math.abs(data.timestamp - time) < 0.1
      );
      setCurrentSpeed(currentSpeedData?.speed || null);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error || !videoData) return <div>Error: {error || 'Failed to load data'}</div>;

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <VideoPlayer
          videoId={videoData.video_id}
          onTimeUpdate={handleTimeUpdate}
        />
        {currentSpeed !== null && (
          <Box sx={{ 
            textAlign: 'center', 
            my: 2, 
            p: 2, 
            bgcolor: 'background.paper',
            borderRadius: 1,
            boxShadow: 1
          }}>
            <Typography variant="h3">
              {currentSpeed.toFixed(1)} км/ч
            </Typography>
          </Box>
        )}
        <SpeedChart
          speedData={videoData.speed_data}
          currentTime={currentTime}
        />
      </Box>
    </Container>
  );
};

export default VideoAnnotation;
export {};