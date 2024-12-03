import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UploadState } from '../../types';

const initialState: UploadState = {
  isUploading: false,
  progress: 0,
  error: null,
  videoId: null,
};

const uploadSlice = createSlice({
  name: 'upload',
  initialState,
  reducers: {
    uploadStart: (state) => {
      state.isUploading = true;
      state.progress = 0;
      state.error = null;
    },
    uploadProgress: (state, action: PayloadAction<number>) => {
      state.progress = action.payload;
    },
    uploadSuccess: (state, action: PayloadAction<string>) => {
      state.isUploading = false;
      state.progress = 100;
      state.videoId = action.payload;
    },
    uploadFailure: (state, action: PayloadAction<string>) => {
      state.isUploading = false;
      state.error = action.payload;
    },
    resetUpload: (state) => {
      state.isUploading = false;
      state.progress = 0;
      state.error = null;
      state.videoId = null;
    },
  },
});

export const {
  uploadStart,
  uploadProgress,
  uploadSuccess,
  uploadFailure,
  resetUpload,
} = uploadSlice.actions;
export default uploadSlice.reducer;
