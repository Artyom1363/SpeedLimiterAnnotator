import React from 'react';
import { Typography, Paper } from '@mui/material';
import { Segment } from '../types/segment';

interface SegmentInfoProps {
  segment: Segment;
  currentSpeed: number | null;
}

const SegmentInfo: React.FC<SegmentInfoProps> = ({ segment, currentSpeed }) => {
  return (
    <Paper 
      sx={{ 
        position: 'absolute',
        top: '-60px',
        left: '50%',
        transform: 'translateX(-50%)',
        p: 1,
        minWidth: '200px',
        zIndex: 1000
      }}
    >
      <Typography variant="body2">
        {segment.type === 'speed_adjustment' ? (
          <>
            Корректировка скорости:
            <br />
            Исходная: {currentSpeed?.toFixed(1) || '-'} км/ч
            <br />
            Новая: {segment.adjustedSpeed?.toFixed(1) || '-'} км/ч
          </>
        ) : (
          'Нерелевантные данные'
        )}
      </Typography>
    </Paper>
  );
};

export default SegmentInfo; 