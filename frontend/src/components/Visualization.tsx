import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import Plot from 'react-plotly.js';

interface VisualizationProps {
  data: any;
  chartType: string;
}

const Visualization: React.FC<VisualizationProps> = ({ data, chartType }: VisualizationProps) => {
  if (!data) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">
          No visualization data available
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Visualization ({chartType})
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Plot
          data={data.data}
          layout={data.layout}
          config={{ responsive: true }}
          style={{ width: '100%', height: '500px' }}
        />
      </Paper>
    </Box>
  );
};

export default Visualization;
