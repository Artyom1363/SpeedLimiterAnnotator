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
  Legend
} from 'chart.js';
import { Box } from '@mui/material';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface SpeedChartProps {
  speedData: Array<{
    timestamp: number;
    speed: number;
  }>;
  currentTime: number;
}

const SpeedChart: React.FC<SpeedChartProps> = ({ speedData, currentTime }) => {
  const data = {
    labels: speedData.map(d => d.timestamp.toFixed(1)),
    datasets: [
      {
        label: 'Speed (km/h)',
        data: speedData.map(d => d.speed),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Speed Over Time'
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Time (seconds)'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Speed (km/h)'
        }
      }
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '800px', mx: 'auto', mt: 2 }}>
      <Line data={data} options={options} />
    </Box>
  );
};

export default SpeedChart; 