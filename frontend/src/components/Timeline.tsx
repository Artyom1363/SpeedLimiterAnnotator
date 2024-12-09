import React, { useState, useRef } from 'react';
import { Box, Slider } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { IconButton } from '@mui/material';
import { Segment } from '../types/segment';
import SegmentInfo from './SegmentInfo';

interface TimelineProps {
  currentTime: number;
  onTimeChange: (time: number) => void;
  videoDuration: number;
  segments: Segment[];
  onSegmentDelete: (segmentId: string) => void;
  getCurrentSpeed: (time: number) => number | null;
  onSegmentClick: (segment: Segment) => void;
  activeSegment: Segment | null;
  onSegmentUpdate: (segmentId: string, startTime: number, endTime: number) => void;
}

const Timeline: React.FC<TimelineProps> = ({
  currentTime,
  onTimeChange,
  videoDuration,
  segments,
  onSegmentDelete,
  getCurrentSpeed,
  onSegmentClick,
  activeSegment,
  onSegmentUpdate
}) => {
  const timelineRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState<string | null>(null);
  const dragStartRef = useRef<{ x: number; segmentStart: number; segmentEnd: number } | null>(null);
  const [hoveredSegment, setHoveredSegment] = useState<string | null>(null);

  const handleTimelineClick = (e: React.MouseEvent) => {
    if (!timelineRef.current) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const clickPosition = (e.clientX - rect.left) / rect.width;
    const newTime = clickPosition * videoDuration;
    onTimeChange(Math.max(0, Math.min(newTime, videoDuration)));
  };

  const handleSegmentResize = (e: React.MouseEvent, segmentId: string, edge: 'start' | 'end') => {
    e.stopPropagation();
    const segment = segments.find(s => s.id === segmentId);
    if (!segment || !timelineRef.current) return;

    const timelineRect = timelineRef.current.getBoundingClientRect();
    dragStartRef.current = {
      x: e.clientX,
      segmentStart: segment.startTime,
      segmentEnd: segment.endTime
    };
    setIsDragging(`${segmentId}-${edge}`);

    const handleMouseMove = (e: MouseEvent) => {
      if (!dragStartRef.current || !timelineRef.current) return;

      const timelineWidth = timelineRect.width;
      const pixelsPerSecond = timelineWidth / videoDuration;
      const deltaTime = (e.clientX - dragStartRef.current.x) / pixelsPerSecond;

      let newStart = segment.startTime;
      let newEnd = segment.endTime;

      if (edge === 'start') {
        newStart = Math.max(0, Math.min(dragStartRef.current.segmentStart + deltaTime, segment.endTime - 0.1));
      } else {
        newEnd = Math.min(videoDuration, Math.max(segment.startTime + 0.1, dragStartRef.current.segmentEnd + deltaTime));
      }

      onSegmentUpdate(segmentId, newStart, newEnd);
    };

    const handleMouseUp = () => {
      setIsDragging(null);
      dragStartRef.current = null;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleSegmentMove = (e: React.MouseEvent, segmentId: string) => {
    e.stopPropagation();
    const segment = segments.find(s => s.id === segmentId);
    if (!segment || !timelineRef.current) return;

    const timelineRect = timelineRef.current.getBoundingClientRect();
    const segmentDuration = segment.endTime - segment.startTime;
    dragStartRef.current = {
      x: e.clientX,
      segmentStart: segment.startTime,
      segmentEnd: segment.endTime
    };
    setIsDragging(segmentId);

    const handleMouseMove = (e: MouseEvent) => {
      if (!dragStartRef.current || !timelineRef.current) return;

      const timelineWidth = timelineRect.width;
      const pixelsPerSecond = timelineWidth / videoDuration;
      const deltaTime = (e.clientX - dragStartRef.current.x) / pixelsPerSecond;

      const newStart = Math.max(0, Math.min(dragStartRef.current.segmentStart + deltaTime, videoDuration - segmentDuration));
      const newEnd = newStart + segmentDuration;

      onSegmentUpdate(segmentId, newStart, newEnd);
    };

    const handleMouseUp = () => {
      setIsDragging(null);
      dragStartRef.current = null;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <Box 
      ref={timelineRef} 
      sx={{ width: '100%', mt: 2, position: 'relative', height: '60px' }}
      onClick={handleTimelineClick}
    >
      <Slider
        value={currentTime}
        onChange={(_, value) => onTimeChange(value as number)}
        min={0}
        max={videoDuration}
        step={0.1}
        sx={{ mt: 2 }}
      />
      {segments.map(segment => (
        <Box
          key={segment.id}
          onClick={(e) => {
            e.stopPropagation();
            onSegmentClick(segment);
          }}
          onMouseEnter={() => setHoveredSegment(segment.id)}
          onMouseLeave={() => setHoveredSegment(null)}
          sx={{
            position: 'absolute',
            left: `${(segment.startTime / videoDuration) * 100}%`,
            width: `${((segment.endTime - segment.startTime) / videoDuration) * 100}%`,
            height: '20px',
            bgcolor: segment.type === 'speed_adjustment' ? 'yellow' : 'red',
            opacity: isDragging === segment.id ? 0.8 : 0.5,
            top: '15px',
            cursor: isDragging ? 'grabbing' : 'grab',
            border: activeSegment?.id === segment.id ? '2px solid #666' : 'none',
            '&:hover': {
              opacity: 0.7
            }
          }}
          onMouseDown={(e) => handleSegmentMove(e, segment.id)}
        >
          {hoveredSegment === segment.id && (
            <>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onSegmentDelete(segment.id);
                }}
                sx={{
                  position: 'absolute',
                  right: '-20px',
                  bottom: '-25px',
                  bgcolor: 'background.paper',
                  boxShadow: 1,
                  '&:hover': {
                    bgcolor: 'background.paper',
                  }
                }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
              <Box sx={{ position: 'absolute', width: '100%', top: '-90px' }}>
                <SegmentInfo
                  segment={segment}
                  currentSpeed={getCurrentSpeed(segment.startTime)}
                />
              </Box>
            </>
          )}
          <Box
            sx={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: '10px',
              height: '100%',
              cursor: 'col-resize',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.3)' }
            }}
            onMouseDown={(e) => handleSegmentResize(e, segment.id, 'start')}
          />
          <Box
            sx={{
              position: 'absolute',
              right: 0,
              top: 0,
              width: '10px',
              height: '100%',
              cursor: 'col-resize',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.3)' }
            }}
            onMouseDown={(e) => handleSegmentResize(e, segment.id, 'end')}
          />
        </Box>
      ))}
    </Box>
  );
};

export default Timeline; 