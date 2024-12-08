import React, { forwardRef, useState, useImperativeHandle } from 'react';
import ReactPlayer from 'react-player';
import { Box, CircularProgress } from '@mui/material';

interface VideoPlayerProps {
  videoId: string;
  onTimeUpdate?: (currentTime: number) => void;
  onReady?: (duration: number) => void;
  onError?: (error: any) => void;
}

interface VideoPlayerRef {
  currentTime: number;
}

const VideoPlayer = forwardRef<VideoPlayerRef, VideoPlayerProps>(({ 
  videoId, 
  onTimeUpdate, 
  onReady, 
  onError 
}, ref) => {
  const videoUrl = `${process.env.REACT_APP_API_URL || 'http://46.8.29.89'}/api/data/video/${videoId}`;
  const [isLoading, setIsLoading] = useState(true);
  const [player, setPlayer] = useState<ReactPlayer | null>(null);

  useImperativeHandle(ref, () => ({
    get currentTime() {
      return player?.getCurrentTime() || 0;
    },
    set currentTime(time: number) {
      const currentTime = player?.getCurrentTime() || 0;
      if (Math.abs(currentTime - time) > 0.5) {
        player?.seekTo(time, 'seconds');
      }
    }
  }));

  const handleProgress = (state: { playedSeconds: number }) => {
    if (onTimeUpdate) {
      onTimeUpdate(state.playedSeconds);
    }
  };

  const handleDuration = (duration: number) => {
    if (onReady) {
      onReady(duration);
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
        ref={(playerRef) => setPlayer(playerRef)}
        url={videoUrl}
        controls
        width="100%"
        height="100%"
        progressInterval={100}
        onProgress={handleProgress}
        onDuration={handleDuration}
        onReady={() => setIsLoading(false)}
        onError={onError}
      />
    </Box>
  );
});

VideoPlayer.displayName = 'VideoPlayer';

export default VideoPlayer; 