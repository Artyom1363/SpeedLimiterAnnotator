import React, { useState } from 'react';
import { Box, TextField, IconButton, Typography } from '@mui/material';
import ArrowLeftIcon from '@mui/icons-material/ArrowLeft';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';

interface SpeedOffsetControlsProps {
  onOffsetChange: (offset: number) => void;
  currentOffset: number;
}

const SpeedOffsetControls: React.FC<SpeedOffsetControlsProps> = ({
  onOffsetChange,
  currentOffset
}) => {
  const [inputValue, setInputValue] = useState(currentOffset.toString());

  const handleOffsetChange = (newOffset: number) => {
    setInputValue(newOffset.toString());
    onOffsetChange(newOffset);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
    const newOffset = parseFloat(event.target.value);
    if (!isNaN(newOffset)) {
      onOffsetChange(newOffset);
    }
  };

  const adjustOffset = (delta: number) => {
    const newOffset = currentOffset + delta;
    handleOffsetChange(newOffset);
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, my: 2 }}>
      <Typography variant="body1">Смещение данных скорости (сек):</Typography>
      <IconButton onClick={() => adjustOffset(-0.1)} size="small">
        <ArrowLeftIcon />
      </IconButton>
      <TextField
        type="number"
        value={inputValue}
        onChange={handleInputChange}
        inputProps={{
          step: 0.1,
          style: { width: '80px' }
        }}
        size="small"
      />
      <IconButton onClick={() => adjustOffset(0.1)} size="small">
        <ArrowRightIcon />
      </IconButton>
    </Box>
  );
};

export default SpeedOffsetControls; 