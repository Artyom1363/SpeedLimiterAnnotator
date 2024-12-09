import React from 'react';
import { Box, Typography } from '@mui/material';

interface SpeedDisplayProps {
  speed: number | null;
  isIrrelevant?: boolean;
}

const SpeedDisplay: React.FC<SpeedDisplayProps> = ({ speed, isIrrelevant }) => {
  return (
    <Box 
      sx={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        width: '200px',
        textAlign: 'center',
        p: 3,
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 3,
        zIndex: 1000
      }}
    >
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Текущая скорость
      </Typography>
      <Typography variant="h3" component="div" color={isIrrelevant ? 'error.main' : 'inherit'}>
        {isIrrelevant ? 'Нерелевантно' : (speed !== null ? `${speed.toFixed(1)} км/ч` : '-')}
      </Typography>
    </Box>
  );
};

export default SpeedDisplay; 