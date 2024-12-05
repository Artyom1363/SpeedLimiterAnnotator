// src/components/UploadForm.tsx
import React, { useState } from 'react';
import { Box, Button, LinearProgress, Typography, Paper } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useDispatch } from 'react-redux';
import { uploadStart, uploadSuccess, uploadFailure } from '../store/slices/uploadSlice';
import axiosInstance from '../config/axios';
import { toast } from 'react-toastify';
import axios from 'axios';

interface FileUploadState {
  file: File | null;
  progress: number;
}

const csvColumnFormat = [
  'Elapsed time (sec)',
  'Speed (km/h)',
  'Latitude',
  'Longitude',
  'Altitude (km)',
  'Accuracy (km)'
];

const UploadForm: React.FC = () => {
  const dispatch = useDispatch();
  const [videoFile, setVideoFile] = useState<FileUploadState>({ file: null, progress: 0 });
  const [csvFile, setCsvFile] = useState<FileUploadState>({ file: null, progress: 0 });
  const [buttonFile, setButtonFile] = useState<FileUploadState>({ file: null, progress: 0 });
  const [isUploading, setIsUploading] = useState(false);

  const validateCsvFile = async (file: File): Promise<boolean> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const firstLine = text.split('\n')[0];
        const headers = firstLine.split(',').map(h => h.trim());
        
        const hasAllColumns = csvColumnFormat.every(col => 
          headers.includes(col)
        );

        if (!hasAllColumns) {
          toast.error(`CSV must include these columns: ${csvColumnFormat.join(', ')}`);
          resolve(false);
        }
        resolve(true);
      };
      reader.readAsText(file);
    });
  };

  const handleFileSelect = async (
    event: React.ChangeEvent<HTMLInputElement>,
    setFile: React.Dispatch<React.SetStateAction<FileUploadState>>,
    fileType?: 'csv' | 'button' | 'video'
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      if (fileType === 'csv') {
        const isValid = await validateCsvFile(file);
        if (!isValid) {
          event.target.value = '';
          return;
        }
      }
      setFile({ file, progress: 0 });
    }
  };

  const uploadVideo = async (): Promise<string> => {
    if (!videoFile.file) throw new Error('No video file selected');

    const formData = new FormData();
    formData.append('video_file', videoFile.file);

    try {
      console.log('Starting video upload...');
      const response = await axiosInstance.post('/api/data/upload_video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          setVideoFile(prev => ({ ...prev, progress }));
        }
      });

      console.log('Video upload response:', response.data);

      if (!response.data.video_id) {
        throw new Error('No video ID received from server');
      }

      return response.data.video_id;
    } catch (error) {
      console.error('Video upload failed:', error);
      throw error;
    }
  };

  const uploadCsv = async (videoId: string) => {
    if (!csvFile.file) return;

    const formData = new FormData();
    formData.append('csv_file', csvFile.file);

    try {
      console.log('Starting CSV upload for video_id:', videoId);
      const response = await axiosInstance.post(`/api/data/upload_csv/${videoId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          setCsvFile(prev => ({ ...prev, progress }));
        }
      });

      console.log('CSV upload response:', response.data);
      
      if (response.data.status !== 'success') {
        throw new Error(response.data.message || 'CSV upload failed');
      }
    } catch (error) {
      console.error('CSV upload failed:', error);
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  };

  const uploadButtonData = async (videoId: string) => {
    if (!buttonFile.file) return;

    const formData = new FormData();
    formData.append('button_data_file', buttonFile.file);

    try {
      console.log('Starting button data upload for video_id:', videoId);
      const response = await axiosInstance.post(`/api/data/upload_button_data/${videoId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          setButtonFile(prev => ({ ...prev, progress }));
        }
      });

      console.log('Button data upload response:', response.data);
      
      if (response.data.status !== 'success') {
        throw new Error(response.data.message || 'Button data upload failed');
      }
    } catch (error) {
      console.error('Button data upload failed:', error);
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  };

  const handleUpload = async () => {
    if (!videoFile.file) {
      toast.error('Please select a video file');
      return;
    }

    setIsUploading(true);
    dispatch(uploadStart());

    try {
      const videoId = await uploadVideo();
      toast.success('Video uploaded successfully!');

      if (csvFile.file) {
        await uploadCsv(videoId);
        toast.success('CSV data uploaded successfully!');
      }

      if (buttonFile.file) {
        await uploadButtonData(videoId);
        toast.success('Button data uploaded successfully!');
      }

      dispatch(uploadSuccess(videoId));
      toast.success('All files uploaded successfully!');
    } catch (error) {
      console.error('Upload process error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      dispatch(uploadFailure(errorMessage));
      toast.error(`Upload failed: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Box sx={{ textAlign: 'center' }}>
        {/* Video Upload */}
        <Box sx={{ mb: 3 }}>
          <input
            accept="video/*"
            style={{ display: 'none' }}
            id="video-upload"
            type="file"
            onChange={(e) => handleFileSelect(e, setVideoFile, 'video')}
            disabled={isUploading}
          />
          <label htmlFor="video-upload">
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUploadIcon />}
              disabled={isUploading}
            >
              Select Video
            </Button>
          </label>
          {videoFile.file && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected video: {videoFile.file.name}
            </Typography>
          )}
          {videoFile.progress > 0 && (
            <Box sx={{ mt: 1 }}>
              <LinearProgress variant="determinate" value={videoFile.progress} />
              <Typography variant="body2">Video upload progress: {videoFile.progress}%</Typography>
            </Box>
          )}
        </Box>

        {/* CSV Upload */}
        <Box sx={{ mb: 3 }}>
          <input
            accept=".csv"
            style={{ display: 'none' }}
            id="csv-upload"
            type="file"
            onChange={(e) => handleFileSelect(e, setCsvFile, 'csv')}
            disabled={isUploading}
          />
          <label htmlFor="csv-upload">
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUploadIcon />}
              disabled={isUploading}
            >
              Select CSV Data
            </Button>
          </label>
          {csvFile.file && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected CSV: {csvFile.file.name}
            </Typography>
          )}
          {csvFile.progress > 0 && (
            <Box sx={{ mt: 1 }}>
              <LinearProgress variant="determinate" value={csvFile.progress} />
              <Typography variant="body2">CSV upload progress: {csvFile.progress}%</Typography>
            </Box>
          )}
          <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1 }}>
            Required CSV columns: {csvColumnFormat.join(', ')}
          </Typography>
        </Box>

        {/* Button Data Upload */}
        <Box sx={{ mb: 3 }}>
          <input
            accept=".txt"
            style={{ display: 'none' }}
            id="button-upload"
            type="file"
            onChange={(e) => handleFileSelect(e, setButtonFile, 'button')}
            disabled={isUploading}
          />
          <label htmlFor="button-upload">
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUploadIcon />}
              disabled={isUploading}
            >
              Select Button Data
            </Button>
          </label>
          {buttonFile.file && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected button data: {buttonFile.file.name}
            </Typography>
          )}
          {buttonFile.progress > 0 && (
            <Box sx={{ mt: 1 }}>
              <LinearProgress variant="determinate" value={buttonFile.progress} />
              <Typography variant="body2">Button data upload progress: {buttonFile.progress}%</Typography>
            </Box>
          )}
        </Box>

        {/* Upload Button */}
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!videoFile.file || isUploading}
          sx={{ mt: 2 }}
        >
          {isUploading ? 'Uploading...' : 'Upload All Files'}
        </Button>
      </Box>
    </Paper>
  );
};

export default UploadForm;