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
}

const SpeedChart: React.FC<SpeedChartProps> = ({
  speedData,
  currentTime,
  videoDuration,
  speedOffset
}) => {
  // Преобразуем данные с учетом смещения
  const adjustedData = speedData.map((point, index) => ({
    timestamp: index + speedOffset, // Добавляем смещение к времени
    speed: point.speed
  }));

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
        pointRadius: 0, // Убираем точки для более гладкого графика
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
        // Возвращаем скользящее окно ±10 секунд от текущего времени
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