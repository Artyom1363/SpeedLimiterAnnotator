import React, { useState, useEffect } from 'react';
import { Box, Container } from '@mui/material';
import VideoPlayer from './VideoPlayer';
import SpeedChart from './SpeedChart';
import ButtonEvents from './ButtonEvents';
import { useParams } from 'react-router-dom';
import axiosInstance from '../config/axios';

interface VideoData {
  video_id: string;
  speed_data: Array<{
    timestamp: number;
    speed: number;
  }>;
  button_data: Array<{
    timestamp: number;
    state: boolean;
  }>;
}

const VideoAnnotation: React.FC = () => {
  const { videoId } = useParams<{ videoId: string }>();
  const [currentTime, setCurrentTime] = useState(0);
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        console.log('Fetching data for videoId:', videoId);
        
        const response = await axiosInstance.get(`/api/data/${videoId}/data`);
        console.log('API Response:', response.data);
        
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
  };

  const handleVideoError = (error: any) => {
    console.error('Video loading error:', error);
    setError('Ошибка загрузки видео');
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error || !videoData) {
    return <div>Error: {error || 'Failed to load data'}</div>;
  }

  console.log('VideoData:', videoData); // Добавляем для отладки

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <VideoPlayer
          videoId={videoData.video_id}
          onTimeUpdate={handleTimeUpdate}
          onError={handleVideoError}
        />
        <SpeedChart
          speedData={videoData.speed_data}
          currentTime={currentTime}
        />
        <ButtonEvents
          buttonData={videoData.button_data}
          currentTime={currentTime}
        />
      </Box>
    </Container>
  );
};

export default VideoAnnotation;
export {};