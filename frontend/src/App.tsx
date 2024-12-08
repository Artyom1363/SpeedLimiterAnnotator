import React from 'react';
import SignUp from './components/SignUp';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles/video-player.css';
import theme from './theme';
import UploadForm from './components/UploadForm';
import Layout from './components/Layout';
import PrivateRoute from './components/PrivateRoute';
import Login from './components/Login';
import VideoAnnotation from './components/VideoAnnotation';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/upload"
            element={
              <PrivateRoute>
                <UploadForm />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/upload" replace />} />
          <Route path="/annotate/:videoId" element={<VideoAnnotation />} />
        </Routes>
      </Layout>
      <ToastContainer position="top-right" autoClose={5000} />
    </ThemeProvider>
  );
}

export default App;