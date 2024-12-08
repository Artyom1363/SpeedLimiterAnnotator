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
  videoDuration: number;
}

const SpeedChart: React.FC<SpeedChartProps> = ({ speedData, currentTime, videoDuration }) => {
  const chartRef = useRef<any>(null);
  
  const chartData = speedData.map((d, index) => ({
    x: index,
    y: d.speed
  }));
  
  const data = {
    datasets: [{
      label: 'Скорость',
      data: chartData,
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
        min: Math.max(0, currentTime - 10),
        max: Math.min(speedData.length - 1, currentTime + 10),
      },
      y: {
        type: 'linear',
        position: 'left',
        title: {
          display: true,
          text: 'Скорость (км/ч)'
        },
        min: 0,
        max: 25,
        ticks: {
          stepSize: 5
        }
      }
    }
  };

  return (
    <Box sx={{ width: '100%', height: '200px', mt: 2 }}>
      <Line ref={chartRef} data={data} options={options} />
    </Box>
  );
};

export default SpeedChart;