export type SegmentType = 'speed_adjustment' | 'irrelevant';

export interface Segment {
  id: string;
  type: SegmentType;
  startTime: number;
  endTime: number;
  originalSpeed?: number;
  adjustedSpeed?: number;
} 