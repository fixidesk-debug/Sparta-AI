import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, CircularProgress } from '@mui/material';
import { Send } from '@mui/icons-material';
import { queryApi } from '../api/endpoints';

const QueryInput: React.FC = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const result = await queryApi.ask(query);
      setResponse(result.data.response);
    } catch (err: any) {
      setResponse('Error: ' + (err.response?.data?.detail || 'Failed to process query'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Ask a Question
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={2}
          placeholder="Ask anything about your data..."
          value={query}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
          onKeyPress={(e: React.KeyboardEvent) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
        />
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || !query.trim()}
          startIcon={loading ? <CircularProgress size={20} /> : <Send />}
        >
          Ask
        </Button>
      </Box>

      {response && (
        <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
          <Typography variant="subtitle2" color="primary" gutterBottom>
            Response:
          </Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {response}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default QueryInput;
