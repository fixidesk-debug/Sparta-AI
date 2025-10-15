import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Tab,
  Tabs,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/endpoints';

const Login: React.FC = () => {
  // Helper: sanitize and extract a short error message from unknown values
  const sanitizeForDisplay = (value: unknown, maxLen = 300): string => {
    try {
      if (value == null) return '';
      const s = String(value);
      const cleaned = s.replace(/\s+/g, ' ').replace(/[^\x20-\x7E]/g, '');
      return cleaned.length > maxLen ? cleaned.slice(0, maxLen) + '...' : cleaned;
    } catch {
      return 'An error occurred';
    }
  };

  const extractErrorMessage = (err: unknown): string => {
    if (!err) return 'An unknown error occurred';
    if (err instanceof Error) return sanitizeForDisplay(err.message);
    try {
      // common axios-style shape: err.response?.data?.detail
      const maybe = (err as any)?.response?.data?.detail ?? (err as any)?.message ?? err;
      return sanitizeForDisplay(maybe);
    } catch {
      return 'An unknown error occurred';
    }
  };

  const [tabValue, setTabValue] = useState(0);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await authApi.login(email, password);
      localStorage.setItem('token', response.data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(extractErrorMessage(err) || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    setLoading(true);
    setError('');

    try {
      await authApi.register(email, password, fullName);
      // Auto login after registration
      const response = await authApi.login(email, password);
      localStorage.setItem('token', response.data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(extractErrorMessage(err) || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  // Explicit submit handler to improve readability (avoid inline ternaries in JSX)
  const handleSubmit = () => {
    if (tabValue === 0) {
      void handleLogin();
    } else {
      void handleRegister();
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, val: number) => setTabValue(val);

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Sparta AI
        </Typography>

        <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
          <Tab label="Login" />
          <Tab label="Register" />
        </Tabs>

        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {tabValue === 1 && (
            <TextField
              label="Full Name"
              value={fullName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFullName(e.target.value)}
            />
          )}

          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
          />

          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
          />

          {error && <Alert severity="error">{error}</Alert>}

          <Button variant="contained" size="large" onClick={handleSubmit} disabled={loading}>
            {tabValue === 0 ? 'Login' : 'Register'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;
