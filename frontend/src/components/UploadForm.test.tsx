// src/components/UploadForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { toast } from 'react-toastify';
import UploadForm from './UploadForm';
import axiosInstance from '../config/axios';
import { RootState } from '../store';

// Mock dependencies
jest.mock('react-toastify');
jest.mock('../config/axios');
const mockAxios = axiosInstance as jest.Mocked<typeof axiosInstance>;

const createMockStore = () => {
  return configureStore({
    reducer: {
      upload: (state = {
        isUploading: false,
        progress: 0,
        error: null,
        videoId: null,
      }) => state,
    },
  });
};

describe('UploadForm', () => {
  let store: ReturnType<typeof createMockStore>;

  beforeEach(() => {
    store = createMockStore();
    jest.clearAllMocks();
  });

  it('renders upload buttons for video, CSV, and button data', () => {
    render(
      <Provider store={store}>
        <UploadForm />
      </Provider>
    );

    expect(screen.getByText('Select Video')).toBeInTheDocument();
    expect(screen.getByText('Select CSV Data')).toBeInTheDocument();
    expect(screen.getByText('Select Button Data')).toBeInTheDocument();
  });

  it('validates CSV format', async () => {
    render(
      <Provider store={store}>
        <UploadForm />
      </Provider>
    );

    const file = new File(
      ['Elapsed time (sec),Wrong Column,Latitude,Longitude,Altitude (km),Accuracy (km)'],
      'test.csv',
      { type: 'text/csv' }
    );

    const input = screen.getByLabelText('Select CSV Data');
    await fireEvent.change(input, { target: { files: [file] } });

    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('CSV must include these columns'));
  });

  it('uploads files successfully', async () => {
    mockAxios.post.mockImplementation((url) => {
      if (url.includes('upload_video')) {
        return Promise.resolve({ data: { status: 'success', video_id: '123' } });
      }
      return Promise.resolve({ data: { status: 'success' } });
    });

    render(
      <Provider store={store}>
        <UploadForm />
      </Provider>
    );

    const videoFile = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    const csvFile = new File(
      ['Elapsed time (sec),Speed (km/h),Latitude,Longitude,Altitude (km),Accuracy (km)'],
      'test.csv',
      { type: 'text/csv' }
    );
    const buttonFile = new File(['0,1,0,1'], 'test.txt', { type: 'text/plain' });

    fireEvent.change(screen.getByLabelText('Select Video'), { target: { files: [videoFile] } });
    await fireEvent.change(screen.getByLabelText('Select CSV Data'), { target: { files: [csvFile] } });
    fireEvent.change(screen.getByLabelText('Select Button Data'), { target: { files: [buttonFile] } });

    fireEvent.click(screen.getByText('Upload All Files'));

    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalledTimes(3);
      expect(toast.success).toHaveBeenCalledWith('All files uploaded successfully!');
    });
  });

  it('handles upload errors', async () => {
    mockAxios.post.mockRejectedValue(new Error('Upload failed'));

    render(
      <Provider store={store}>
        <UploadForm />
      </Provider>
    );

    const videoFile = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    fireEvent.change(screen.getByLabelText('Select Video'), { target: { files: [videoFile] } });

    fireEvent.click(screen.getByText('Upload All Files'));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('Upload failed'));
    });
  });

  it('disables upload button when no video is selected', () => {
    render(
      <Provider store={store}>
        <UploadForm />
      </Provider>
    );

    const uploadButton = screen.getByText('Upload All Files');
    expect(uploadButton).toBeDisabled();
  });

  it('shows progress during upload', async () => {
    mockAxios.post.mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: { status: 'success', video_id: '123' } });
        }, 100);
      });
    });

    render(
      <Provider store={store}>
        <UploadForm />
      </Provider>
    );

    const videoFile = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    fireEvent.change(screen.getByLabelText('Select Video'), { target: { files: [videoFile] } });
    fireEvent.click(screen.getByText('Upload All Files'));

    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });
});