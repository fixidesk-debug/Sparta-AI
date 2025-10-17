"""
Advanced Charts Service - Generate heatmaps, box plots, violin plots, etc.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import logging
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


class AdvancedCharts:
    """Generate advanced chart types"""
    
    @staticmethod
    def generate_heatmap(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'pearson'
    ) -> Dict[str, Any]:
        """
        Generate correlation heatmap
        
        Args:
            df: DataFrame
            columns: Columns to include (None = all numeric)
            method: Correlation method ('pearson', 'spearman', 'kendall')
        """
        try:
            # Select numeric columns
            if columns:
                numeric_df = df[columns].select_dtypes(include=[np.number])
            else:
                numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                raise ValueError("No numeric columns found")
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr(method=method)
            
            # Convert to format for frontend
            heatmap_data = []
            for i, row_name in enumerate(corr_matrix.index):
                for j, col_name in enumerate(corr_matrix.columns):
                    heatmap_data.append({
                        'x': col_name,
                        'y': row_name,
                        'value': float(corr_matrix.iloc[i, j])
                    })
            
            return {
                'type': 'heatmap',
                'data': heatmap_data,
                'columns': list(corr_matrix.columns),
                'rows': list(corr_matrix.index),
                'title': f'{method.capitalize()} Correlation Heatmap'
            }
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {e}")
            raise
    
    @staticmethod
    def generate_box_plot(
        df: pd.DataFrame,
        column: str,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate box plot for a column
        
        Args:
            df: DataFrame
            column: Column to plot
            group_by: Optional column to group by
        """
        try:
            if column not in df.columns:
                raise ValueError(f"Column {column} not found")
            
            # Remove NaN values
            clean_df = df[[column, group_by] if group_by else [column]].dropna()
            
            if group_by and group_by in clean_df.columns:
                # Grouped box plot
                groups = clean_df.groupby(group_by)[column]
                box_data = []
                
                for name, group in groups:
                    values = group.values
                    q1 = np.percentile(values, 25)
                    q2 = np.percentile(values, 50)  # median
                    q3 = np.percentile(values, 75)
                    iqr = q3 - q1
                    lower_whisker = max(values.min(), q1 - 1.5 * iqr)
                    upper_whisker = min(values.max(), q3 + 1.5 * iqr)
                    outliers = values[(values < lower_whisker) | (values > upper_whisker)]
                    
                    box_data.append({
                        'group': str(name),
                        'min': float(lower_whisker),
                        'q1': float(q1),
                        'median': float(q2),
                        'q3': float(q3),
                        'max': float(upper_whisker),
                        'outliers': [float(x) for x in outliers]
                    })
            else:
                # Single box plot
                values = clean_df[column].values
                q1 = np.percentile(values, 25)
                q2 = np.percentile(values, 50)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                lower_whisker = max(values.min(), q1 - 1.5 * iqr)
                upper_whisker = min(values.max(), q3 + 1.5 * iqr)
                outliers = values[(values < lower_whisker) | (values > upper_whisker)]
                
                box_data = [{
                    'group': column,
                    'min': float(lower_whisker),
                    'q1': float(q1),
                    'median': float(q2),
                    'q3': float(q3),
                    'max': float(upper_whisker),
                    'outliers': [float(x) for x in outliers]
                }]
            
            return {
                'type': 'boxplot',
                'data': box_data,
                'column': column,
                'group_by': group_by,
                'title': f'Box Plot: {column}' + (f' by {group_by}' if group_by else '')
            }
            
        except Exception as e:
            logger.error(f"Error generating box plot: {e}")
            raise
    
    @staticmethod
    def generate_violin_plot(
        df: pd.DataFrame,
        column: str,
        group_by: Optional[str] = None,
        bins: int = 50
    ) -> Dict[str, Any]:
        """
        Generate violin plot (distribution plot)
        
        Args:
            df: DataFrame
            column: Column to plot
            group_by: Optional column to group by
            bins: Number of bins for distribution
        """
        try:
            if column not in df.columns:
                raise ValueError(f"Column {column} not found")
            
            clean_df = df[[column, group_by] if group_by else [column]].dropna()
            
            if group_by and group_by in clean_df.columns:
                # Grouped violin plot
                groups = clean_df.groupby(group_by)[column]
                violin_data = []
                
                for name, group in groups:
                    values = group.values
                    hist, bin_edges = np.histogram(values, bins=bins, density=True)
                    
                    violin_data.append({
                        'group': str(name),
                        'values': [float(x) for x in values],
                        'density': [float(x) for x in hist],
                        'bins': [float(x) for x in bin_edges],
                        'mean': float(values.mean()),
                        'median': float(np.median(values)),
                        'std': float(values.std())
                    })
            else:
                # Single violin plot
                values = clean_df[column].values
                hist, bin_edges = np.histogram(values, bins=bins, density=True)
                
                violin_data = [{
                    'group': column,
                    'values': [float(x) for x in values],
                    'density': [float(x) for x in hist],
                    'bins': [float(x) for x in bin_edges],
                    'mean': float(values.mean()),
                    'median': float(np.median(values)),
                    'std': float(values.std())
                }]
            
            return {
                'type': 'violin',
                'data': violin_data,
                'column': column,
                'group_by': group_by,
                'title': f'Violin Plot: {column}' + (f' by {group_by}' if group_by else '')
            }
            
        except Exception as e:
            logger.error(f"Error generating violin plot: {e}")
            raise
    
    @staticmethod
    def generate_histogram(
        df: pd.DataFrame,
        column: str,
        bins: int = 30
    ) -> Dict[str, Any]:
        """Generate histogram with distribution curve"""
        try:
            if column not in df.columns:
                raise ValueError(f"Column {column} not found")
            
            values = df[column].dropna().values
            
            # Calculate histogram
            hist, bin_edges = np.histogram(values, bins=bins)
            
            # Calculate statistics
            mean = float(values.mean())
            median = float(np.median(values))
            std = float(values.std())
            
            # Prepare data
            hist_data = []
            for i in range(len(hist)):
                hist_data.append({
                    'bin_start': float(bin_edges[i]),
                    'bin_end': float(bin_edges[i + 1]),
                    'count': int(hist[i]),
                    'bin_center': float((bin_edges[i] + bin_edges[i + 1]) / 2)
                })
            
            return {
                'type': 'histogram',
                'data': hist_data,
                'column': column,
                'mean': mean,
                'median': median,
                'std': std,
                'total_count': len(values),
                'title': f'Distribution: {column}'
            }
            
        except Exception as e:
            logger.error(f"Error generating histogram: {e}")
            raise
    
    @staticmethod
    def generate_scatter_matrix(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        sample_size: int = 1000
    ) -> Dict[str, Any]:
        """Generate scatter plot matrix for multiple columns"""
        try:
            # Select numeric columns
            if columns:
                numeric_df = df[columns].select_dtypes(include=[np.number])
            else:
                numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                raise ValueError("No numeric columns found")
            
            # Sample if too large
            if len(numeric_df) > sample_size:
                numeric_df = numeric_df.sample(n=sample_size, random_state=42)
            
            # Generate scatter data for each pair
            scatter_data = []
            column_list = list(numeric_df.columns)
            
            for i, col1 in enumerate(column_list):
                for j, col2 in enumerate(column_list):
                    if i != j:  # Skip diagonal
                        points = []
                        for idx in range(len(numeric_df)):
                            points.append({
                                'x': float(numeric_df[col1].iloc[idx]),
                                'y': float(numeric_df[col2].iloc[idx])
                            })
                        
                        scatter_data.append({
                            'x_column': col1,
                            'y_column': col2,
                            'points': points[:100]  # Limit points for performance
                        })
            
            return {
                'type': 'scatter_matrix',
                'data': scatter_data,
                'columns': column_list,
                'title': 'Scatter Plot Matrix'
            }
            
        except Exception as e:
            logger.error(f"Error generating scatter matrix: {e}")
            raise
    
    @staticmethod
    def generate_area_chart(
        df: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        stacked: bool = True
    ) -> Dict[str, Any]:
        """Generate area chart (stacked or unstacked)"""
        try:
            if x_column not in df.columns:
                raise ValueError(f"Column {x_column} not found")
            
            for col in y_columns:
                if col not in df.columns:
                    raise ValueError(f"Column {col} not found")
            
            # Sort by x column
            sorted_df = df.sort_values(by=x_column)
            
            # Prepare data
            area_data = []
            for idx in range(len(sorted_df)):
                data_point = {'x': str(sorted_df[x_column].iloc[idx])}
                for col in y_columns:
                    data_point[col] = float(sorted_df[col].iloc[idx])
                area_data.append(data_point)
            
            return {
                'type': 'area',
                'data': area_data,
                'x_column': x_column,
                'y_columns': y_columns,
                'stacked': stacked,
                'title': f'Area Chart: {", ".join(y_columns)}'
            }
            
        except Exception as e:
            logger.error(f"Error generating area chart: {e}")
            raise
