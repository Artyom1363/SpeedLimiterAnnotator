import React, { useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  TimeScale,
  ChartOptions
} from 'chart.js';
import { Box } from '@mui/material';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  TimeScale
);

interface SpeedChartProps {
  speedData: Array<{
    timestamp: number;
    speed: number;
  }>;
  currentTime: number;
}

const SpeedChart: React.FC<SpeedChartProps> = ({ speedData, currentTime }) => {
  const chartRef = useRef<any>(null);

  const data = {
    type: 'line' as const,
    datasets: [{
      label: 'Скорость',
      data: speedData.map(d => ({
        x: d.timestamp,
        y: d.speed
      })),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1,
      pointRadius: 0
    }]
  };

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    scales: {
      x: {
        type: 'linear',
        position: 'bottom',
        title: {
          display: true,
          text: 'Время (секунды)'
        },
        min: Math.min(...speedData.map(d => d.timestamp)),
        max: Math.max(...speedData.map(d => d.timestamp))
      },
      y: {
        type: 'linear',
        position: 'left',
        title: {
          display: true,
          text: 'Скорость (км/ч)'
        }
      }
    },
    plugins: {
      tooltip: {
        enabled: true,
        mode: 'nearest',
        intersect: false
      }
    }
  };

  return (
    <Box sx={{ 
      width: '100%', 
      height: '200px',
      mt: 2,
      position: 'relative'
    }}>
      <Line ref={chartRef} data={data} options={options} />
    </Box>
  );
};

export default SpeedChart;