import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import App from './App';
import authReducer from './store/slices/authSlice';
import uploadReducer from './store/slices/uploadSlice';
import { MemoryRouter } from 'react-router-dom';

// Mock react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
  ToastContainer: () => null,
}));

// Mock the theme provider and other MUI components
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  CssBaseline: () => null,
  Paper: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Box: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Typography: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  TextField: () => <input />,
  Button: ({ children }: { children: React.ReactNode }) => <button>{children}</button>,
  Link: ({ children }: { children: React.ReactNode }) => <a href="#">{children}</a>,
}));

const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authReducer,
      upload: uploadReducer,
    },
    preloadedState: initialState,
  });
};

const renderApp = (initialState = {}, initialRoute = '/') => {
  const store = createTestStore(initialState);
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <App />
      </MemoryRouter>
    </Provider>
  );
};

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders without crashing and redirects to login when not authenticated', () => {
    renderApp({
      auth: {
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      }
    });
    
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('renders upload form when authenticated', () => {
    renderApp({
      auth: {
        user: { id: '1', username: 'test', email: 'test@test.com' },
        token: 'test-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }
    });
    
    expect(screen.getByText('Upload All Files')).toBeInTheDocument();
  });
});