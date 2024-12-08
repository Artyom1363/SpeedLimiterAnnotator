import React from 'react';
import { Box, Slider } from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  TimeScale
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  TimeScale
);

interface TimelineProps {
  speedData: Array<{
    timestamp: number;
    speed: number;
  }>;
  currentTime: number;
  onTimeChange: (time: number) => void;
}

const Timeline: React.FC<TimelineProps> = ({
  speedData,
  currentTime,
  onTimeChange
}) => {
  const maxTime = Math.max(...speedData.map(point => point.timestamp));
  
  const handleSliderChange = (_event: Event, newValue: number | number[]) => {
    onTimeChange(newValue as number);
  };

  const chartData = {
    labels: speedData.map(point => point.timestamp),
    datasets: [
      {
        label: 'Скорость',
        data: speedData.map(point => ({
          x: point.timestamp,
          y: point.speed
        })),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        pointRadius: 0
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 250
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      x: {
        type: 'linear' as const,
        display: true,
        title: {
          display: false
        },
        min: Math.max(0, currentTime - 10),
        max: currentTime + 10,
      },
      y: {
        type: 'linear' as const,
        display: true,
        title: {
          display: false
        }
      }
    }
  };

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      <Box sx={{ height: '100px' }}>
        <Line data={chartData} options={chartOptions} />
      </Box>
      <Box sx={{ px: 2, mt: 2 }}>
        <Slider
          value={currentTime}
          onChange={handleSliderChange}
          min={0}
          max={maxTime}
          step={0.1}
          valueLabelDisplay="auto"
          valueLabelFormat={(value) => `${value.toFixed(1)}s`}
        />
      </Box>
    </Box>
  );
};

export default Timeline; 