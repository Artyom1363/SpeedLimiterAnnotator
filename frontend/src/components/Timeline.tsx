import React from 'react';
import { Box, Slider } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { IconButton } from '@mui/material';
import { Segment } from '../types/segment';

interface TimelineProps {
  currentTime: number;
  onTimeChange: (time: number) => void;
  videoDuration: number;
  segments: Segment[];
  onSegmentDelete: (segmentId: string) => void;
}

const Timeline: React.FC<TimelineProps> = ({
  currentTime,
  onTimeChange,
  videoDuration,
  segments,
  onSegmentDelete
}) => {
  const handleSliderChange = (_event: Event, newValue: number | number[]) => {
    onTimeChange(newValue as number);
  };

  return (
    <Box sx={{ width: '100%', mt: 2, position: 'relative' }}>
      <Slider
        value={currentTime}
        onChange={handleSliderChange}
        min={0}
        max={videoDuration}
        step={0.1}
        sx={{ mt: 2 }}
      />
      {segments.map(segment => (
        <Box
          key={segment.id}
          sx={{
            position: 'absolute',
            left: `${(segment.startTime / videoDuration) * 100}%`,
            width: `${((segment.endTime - segment.startTime) / videoDuration) * 100}%`,
            height: '100%',
            bgcolor: segment.type === 'speed_adjustment' ? 'yellow' : 'red',
            opacity: 0.5,
            top: '15px',
            '&:hover': {
              opacity: 0.7,
              '& .segment-controls': {
                display: 'flex'
              }
            }
          }}
        >
          <Box
            className="segment-controls"
            sx={{
              position: 'absolute',
              right: 0,
              top: '-20px',
              display: 'none'
            }}
          >
            <IconButton
              size="small"
              onClick={() => onSegmentDelete(segment.id)}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        </Box>
      ))}
    </Box>
  );
};

export default Timeline; 