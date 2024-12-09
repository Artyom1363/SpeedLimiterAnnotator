import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
} from 'chart.js';
import { Box } from '@mui/material';
import { Segment } from '../types/segment';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip
);

interface SpeedChartProps {
  speedData: Array<{
    timestamp: number;
    speed: number;
  }>;
  currentTime: number;
  videoDuration: number;
  speedOffset: number;
  segments: Segment[];
}

const SpeedChart: React.FC<SpeedChartProps> = ({
  speedData,
  currentTime,
  videoDuration,
  speedOffset,
  segments
}) => {
  // Преобразуем данные с учетом смещения и корректировок скорости
  const adjustedData = speedData.map((point, index) => {
    const timestamp = index + speedOffset;
    let speed = point.speed;

    // Проверяем, находится ли точка в каком-либо сегменте корректировки скорости
    const speedAdjustmentSegment = segments.find(
      segment => 
        segment.type === 'speed_adjustment' &&
        timestamp >= segment.startTime &&
        timestamp <= segment.endTime &&
        segment.adjustedSpeed !== undefined
    );

    if (speedAdjustmentSegment) {
      speed = speedAdjustmentSegment.adjustedSpeed!;
    }

    return {
      timestamp,
      speed
    };
  });

  const data = {
    datasets: [
      {
        label: 'Скорость',
        data: adjustedData.map(point => ({
          x: point.timestamp,
          y: point.speed
        })),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        pointRadius: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Скорость (км/ч)'
        }
      },
      x: {
        type: 'linear' as const,
        title: {
          display: true,
          text: 'Время (с)'
        },
        min: Math.max(0, currentTime - 10),
        max: Math.min(videoDuration, currentTime + 10)
      }
    },
    plugins: {
      tooltip: {
        enabled: true,
        mode: 'index' as const,
        intersect: false
      }
    }
  };

  return (
    <Box sx={{ width: '100%', height: '200px', mt: 2 }}>
      <Line data={data} options={options} />
    </Box>
  );
};

export default SpeedChart;