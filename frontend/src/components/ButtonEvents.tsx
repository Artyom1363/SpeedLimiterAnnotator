import React from 'react';
import { Box } from '@mui/material';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ButtonEventsProps {
  buttonData: Array<{
    timestamp: number;
    state: boolean;
  }>;
  currentTime: number;
}

const ButtonEvents: React.FC<ButtonEventsProps> = ({ buttonData, currentTime }) => {
  const data = {
    labels: buttonData.map(d => d.timestamp.toFixed(1)),
    datasets: [
      {
        label: 'Button State',
        data: buttonData.map(d => d.state ? 1 : 0),
        backgroundColor: 'rgb(255, 99, 132)',
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
        text: 'Button Events'
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
        min: 0,
        max: 1,
        ticks: {
          stepSize: 1
        }
      }
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '800px', mx: 'auto', mt: 2 }}>
      <Bar data={data} options={options} />
    </Box>
  );
};

export default ButtonEvents;
export {};