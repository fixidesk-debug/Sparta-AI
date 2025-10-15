import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, Alert } from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import { execApi } from '../api/endpoints';

const CodeExecutor: React.FC = () => {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleExecute = async () => {
    if (!code.trim()) return;

    setLoading(true);
    setOutput('');
    setError('');

    try {
      const result = await execApi.run(code);
      if (result.data.error) {
        setError(result.data.error);
      } else {
        setOutput(result.data.output || 'Code executed successfully (no output)');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Code Executor
      </Typography>

      <TextField
        fullWidth
        multiline
        rows={8}
        placeholder="# Write Python code here&#10;print('Hello, Sparta AI!')"
        value={code}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCode(e.target.value)}
        sx={{ mb: 2, fontFamily: 'monospace' }}
      />

      <Button
        variant="contained"
        onClick={handleExecute}
        disabled={loading || !code.trim()}
        startIcon={<PlayArrow />}
        sx={{ mb: 2 }}
      >
        Run Code
      </Button>

      {output && (
        <Paper sx={{ p: 2, bgcolor: 'grey.100', mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Output:
          </Typography>
          <Typography
            variant="body2"
            component="pre"
            sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}
          >
            {output}
          </Typography>
        </Paper>
      )}

      {error && (
        <Alert severity="error">
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default CodeExecutor;
