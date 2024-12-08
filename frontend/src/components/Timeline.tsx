import React from 'react';
import { Box, Slider } from '@mui/material';

interface TimelineProps {
  currentTime: number;
  onTimeChange: (time: number) => void;
  videoDuration: number;
}

const Timeline: React.FC<TimelineProps> = ({
  currentTime,
  onTimeChange,
  videoDuration
}) => {
  const handleSliderChange = (_event: Event, newValue: number | number[]) => {
    onTimeChange(newValue as number);
  };

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      <Slider
        value={currentTime}
        onChange={handleSliderChange}
        min={0}
        max={videoDuration}
        step={0.1}
        sx={{ mt: 2 }}
      />
    </Box>
  );
};

export default Timeline; 