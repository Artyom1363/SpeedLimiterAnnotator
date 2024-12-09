import React, { useState } from 'react';
import { Box, Typography, TextField, IconButton, Paper } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { Segment } from '../types/segment';

interface SegmentEditorProps {
  segment: Segment;
  currentSpeed: number;
  onSpeedChange: (segmentId: string, newSpeed: number) => void;
}

const SegmentEditor: React.FC<SegmentEditorProps> = ({
  segment,
  currentSpeed,
  onSpeedChange
}) => {
  const [adjustedSpeed, setAdjustedSpeed] = useState(
    segment.adjustedSpeed || currentSpeed
  );

  const handleSpeedChange = (delta: number) => {
    const newSpeed = Math.max(0, adjustedSpeed + delta);
    setAdjustedSpeed(newSpeed);
    onSpeedChange(segment.id, newSpeed);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newSpeed = parseFloat(event.target.value);
    if (!isNaN(newSpeed) && newSpeed >= 0) {
      setAdjustedSpeed(newSpeed);
      onSpeedChange(segment.id, newSpeed);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
      <Typography variant="subtitle1" gutterBottom>
        Корректировка скорости
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography>
          Исходная скорость: {currentSpeed.toFixed(1)} км/ч
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={() => handleSpeedChange(-0.5)} size="small">
            <RemoveIcon />
          </IconButton>
          <TextField
            type="number"
            value={adjustedSpeed}
            onChange={handleInputChange}
            inputProps={{
              step: 0.5,
              min: 0,
              style: { width: '80px' }
            }}
            size="small"
          />
          <IconButton onClick={() => handleSpeedChange(0.5)} size="small">
            <AddIcon />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default SegmentEditor; 