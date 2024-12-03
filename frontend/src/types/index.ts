export interface User {
  id: string;
  username: string;
  email: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  videoId: string | null;
}

export type RootState = {
  auth: AuthState;
  upload: UploadState;
};
