import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import UploadForm from './UploadForm';
import uploadReducer from '../store/slices/uploadSlice';

// Mock dependencies
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock axios module
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: jest.fn(),
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() },
    },
  })),
  isAxiosError: jest.fn()
}));

// Создаем обертку для рендеринга с провайдером
const renderWithProvider = (ui: React.ReactElement) => {
  const store = configureStore({
    reducer: {
      upload: uploadReducer,
    },
  });
  
  return {
    ...render(
      <Provider store={store}>
        {ui}
      </Provider>
    ),
    store,
  };
};

describe('UploadForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders upload buttons', () => {
    renderWithProvider(<UploadForm />);
    expect(screen.getByText('Select Video')).toBeInTheDocument();
    expect(screen.getByText('Select CSV Data')).toBeInTheDocument();
    expect(screen.getByText('Select Button Data')).toBeInTheDocument();
  });

  test('handles video file selection', async () => {
    renderWithProvider(<UploadForm />);
    const file = new File(['test video content'], 'test.mp4', { type: 'video/mp4' });
    const input = screen.getByLabelText(/Select Video/i);

    fireEvent.change(input, { target: { files: [file] } });
    
    expect((input as HTMLInputElement).files?.[0]).toBeTruthy();
    expect((input as HTMLInputElement).files?.[0].name).toBe('test.mp4');
  });

  test('handles CSV file selection', async () => {
    renderWithProvider(<UploadForm />);
    const csvContent = 'Elapsed time (sec),Speed (km/h),Latitude,Longitude,Altitude (km),Accuracy (km)\n1,60,0,0,0,0';
    const file = new File([csvContent], 'test.csv', { type: 'text/csv' });
    const input = screen.getByLabelText(/Select CSV Data/i);

    fireEvent.change(input, { target: { files: [file] } });
    
    expect((input as HTMLInputElement).files?.[0]).toBeTruthy();
    expect((input as HTMLInputElement).files?.[0].name).toBe('test.csv');
  });

  test('handles button data file selection', async () => {
    renderWithProvider(<UploadForm />);
    const file = new File(['0,1,0,1'], 'button.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/Select Button Data/i);

    fireEvent.change(input, { target: { files: [file] } });
    
    expect((input as HTMLInputElement).files?.[0]).toBeTruthy();
    expect((input as HTMLInputElement).files?.[0].name).toBe('button.txt');
  });

  test('upload button is disabled when no video is selected', () => {
    renderWithProvider(<UploadForm />);
    const uploadButton = screen.getByText('Upload All Files');
    expect(uploadButton).toBeDisabled();
  });

  test('upload button is enabled when video is selected', async () => {
    renderWithProvider(<UploadForm />);
    const file = new File(['test video content'], 'test.mp4', { type: 'video/mp4' });
    const input = screen.getByLabelText(/Select Video/i);

    fireEvent.change(input, { target: { files: [file] } });
    
    const uploadButton = screen.getByText('Upload All Files');
    expect(uploadButton).not.toBeDisabled();
  });
});