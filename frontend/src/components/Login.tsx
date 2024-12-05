// src/components/Login.tsx
import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Link } from '@mui/material';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { loginStart, loginSuccess, loginFailure } from '../store/slices/authSlice';
import axios from 'axios';
import { toast } from 'react-toastify';

const Login: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    dispatch(loginStart());

    const formData = new FormData(event.currentTarget);
    
    try {
      console.log('Attempting login...'); // Debug log
      const response = await axios.post('/api/auth/login', {
        email: formData.get('email'),
        password: formData.get('password')
      });

      console.log('Login response:', response.data); // Debug log

      if (response.data.status === 'success') {
        // Store the token
        const token = response.data.access_token;
        
        // Update axios default headers for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // Update Redux state
        dispatch(loginSuccess({
          user: {
            id: 'temp-id', // We might need to make another request to get user details
            email: formData.get('email') as string,
            username: formData.get('email') as string
          },
          token: token
        }));

        toast.success('Successfully logged in!');
        navigate('/upload');
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error); // Debug log
      if (axios.isAxiosError(error) && error.response) {
        dispatch(loginFailure(error.response.data.message || 'Login failed'));
        toast.error(`Login failed: ${error.response.data.message || error.message}`);
      } else {
        dispatch(loginFailure('Login failed'));
        toast.error('Login failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        marginTop: 8,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Paper elevation={3} sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography component="h1" variant="h5" align="center">
          Sign In
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </Button>
          <Box sx={{ textAlign: 'center' }}>
            <Link href="/signup" variant="body2">
              {"Don't have an account? Sign Up"}
            </Link>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default Login;