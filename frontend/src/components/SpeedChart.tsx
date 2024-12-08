import React, { useRef, useEffect } from 'react';
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

  useEffect(() => {
    const chart = chartRef.current;
    if (chart) {
      const chartInstance = chart.chartInstance;
      if (chartInstance) {
        const xScale = chartInstance.scales.x;
        const visibleRange = xScale.max - xScale.min;
        
        if (currentTime < xScale.min || currentTime > xScale.max) {
          const newMin = Math.max(0, currentTime - visibleRange / 2);
          const newMax = newMin + visibleRange;
          
          chartInstance.options.scales.x.min = newMin;
          chartInstance.options.scales.x.max = newMax;
          chartInstance.update('none');
        }
      }
    }
  }, [currentTime]);

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
        min: Math.max(0, currentTime - 10),
        max: currentTime + 10,
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

  if (chartRef.current) {
    const chart = chartRef.current;
    const ctx = chart.ctx;
    const xScale = chart.scales.x;
    const yScale = chart.scales.y;
    
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(xScale.getPixelForValue(currentTime), yScale.top);
    ctx.lineTo(xScale.getPixelForValue(currentTime), yScale.bottom);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
  }

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