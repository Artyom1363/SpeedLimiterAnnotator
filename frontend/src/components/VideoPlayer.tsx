import React, { useState } from 'react';
import ReactPlayer from 'react-player';
import { Box, CircularProgress } from '@mui/material';

interface VideoPlayerProps {
  videoId: string;
  onTimeUpdate?: (currentTime: number) => void;
  onError?: (error: any) => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoId, onTimeUpdate, onError }) => {
  const videoUrl = `${process.env.REACT_APP_API_URL || 'http://46.8.29.89'}/api/data/video/${videoId}`;
  const [isLoading, setIsLoading] = useState(true);

  const handleProgress = (state: { playedSeconds: number }) => {
    if (onTimeUpdate) {
      onTimeUpdate(state.playedSeconds);
    }
  };

  return (
    <Box position="relative" width="100%" minHeight="400px">
      {isLoading && (
        <Box
          position="absolute"
          display="flex"
          alignItems="center"
          justifyContent="center"
          width="100%"
          height="100%"
          bgcolor="rgba(0, 0, 0, 0.3)"
          zIndex={2}
        >
          <CircularProgress />
        </Box>
      )}
      <ReactPlayer
        url={videoUrl}
        controls
        width="100%"
        height="100%"
        onProgress={handleProgress}
        onReady={() => setIsLoading(false)}
        onError={onError}
      />
    </Box>
  );
};

export default VideoPlayer; 