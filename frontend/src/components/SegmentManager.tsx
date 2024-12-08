import React, { useState } from 'react';
import { Box, Button } from '@mui/material';
import { Segment, SegmentType } from '../types/segment';
import SegmentTypeSelector from './SegmentTypeSelector';
import { v4 as uuidv4 } from 'uuid';

interface SegmentManagerProps {
  currentTime: number;
  videoDuration: number;
  onSegmentCreate: (segment: Segment) => void;
}

const SegmentManager: React.FC<SegmentManagerProps> = ({
  currentTime,
  videoDuration,
  onSegmentCreate
}) => {
  const [selectedType, setSelectedType] = useState<SegmentType | null>(null);

  const handleCreateSegment = () => {
    if (!selectedType) return;

    const endTime = Math.min(currentTime + 5, videoDuration);
    const newSegment: Segment = {
      id: uuidv4(),
      type: selectedType,
      startTime: currentTime,
      endTime: endTime,
    };

    onSegmentCreate(newSegment);
  };

  return (
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
      <SegmentTypeSelector
        selectedType={selectedType}
        onTypeSelect={setSelectedType}
      />
      <Button
        variant="contained"
        onClick={handleCreateSegment}
        disabled={!selectedType}
      >
        Создать сегмент
      </Button>
    </Box>
  );
};

export default SegmentManager; 