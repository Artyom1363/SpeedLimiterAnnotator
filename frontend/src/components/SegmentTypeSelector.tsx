import React from 'react';
import { ToggleButton, ToggleButtonGroup } from '@mui/material';
import { SegmentType } from '../types/segment';

interface SegmentTypeSelectorProps {
  selectedType: SegmentType | null;
  onTypeSelect: (type: SegmentType) => void;
}

const SegmentTypeSelector: React.FC<SegmentTypeSelectorProps> = ({
  selectedType,
  onTypeSelect
}) => {
  return (
    <ToggleButtonGroup
      value={selectedType}
      exclusive
      onChange={(_, value) => value && onTypeSelect(value)}
      aria-label="segment type"
    >
      <ToggleButton value="speed_adjustment" aria-label="speed adjustment">
        Корректировка скорости
      </ToggleButton>
      <ToggleButton value="irrelevant" aria-label="irrelevant data">
        Нерелевантные данные
      </ToggleButton>
    </ToggleButtonGroup>
  );
};

export default SegmentTypeSelector; 