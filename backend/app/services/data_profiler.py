"""
Data Profiler

Automatic data profiling and insights generation for intelligent data analysis.

Features:
- Statistical summaries
- Data type detection and conversion
- Missing value analysis
- Data quality assessment
- Column relationship detection
- Outlier identification
- Visualization recommendations

Author: Sparta AI Team
Date: October 14, 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class DataProfiler:
    """
    Automatic data profiling and insights generation.
    
    Provides comprehensive analysis of datasets including:
    - Type detection
    - Statistical summaries
    - Missing value patterns
    - Data quality metrics
    - Correlation analysis
    - Outlier detection
    
    Example:
        >>> profiler = DataProfiler()
        >>> profile = profiler.profile_dataset(df)
        >>> insights = profiler.get_insights(df)
    """
    
    # Thresholds for data quality assessment
    HIGH_MISSING_THRESHOLD = 0.5  # 50% missing considered high
    LOW_CARDINALITY_THRESHOLD = 10  # Unique values
    HIGH_CARDINALITY_THRESHOLD = 100  # Unique values for categorical
    OUTLIER_Z_SCORE = 3.0  # Standard deviations for outlier detection
    CORRELATION_THRESHOLD = 0.7  # Strong correlation
    
    def __init__(self):
        """Initialize DataProfiler"""
        self.profile_cache: Dict[str, Any] = {}
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        try:
            if pd.isna(value) or isinstance(value, complex):
                return 0.0
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
    def _safe_int(self, value) -> int:
        """Safely convert value to int"""
        try:
            if pd.isna(value):
                return 0
            return int(value)
        except (TypeError, ValueError):
            return 0
    
    def detect_column_type(self, series: pd.Series) -> str:
        """
        Detect the semantic type of a column.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Detected type: 'numeric', 'categorical', 'datetime', 'text', 'binary', 'id'
        """
        # Check for all missing
        if series.isna().all():
            return 'unknown'
        
        # Check pandas dtype first
        if pd.api.types.is_numeric_dtype(series):
            # Check if it's actually an ID column
            if self._is_id_column(series):
                return 'id'
            # Check if it's binary (0/1 or True/False)
            if set(series.dropna().unique()).issubset({0, 1, True, False}):
                return 'binary'
            return 'numeric'
        
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        # Check if it can be converted to datetime
        if self._can_convert_to_datetime(series):
            return 'datetime'
        
        # Check for categorical vs text
        if pd.api.types.is_object_dtype(series):
            unique_ratio = series.nunique() / len(series)
            
            if self._is_id_column(series):
                return 'id'
            elif unique_ratio < 0.05 or series.nunique() < self.HIGH_CARDINALITY_THRESHOLD:
                return 'categorical'
            else:
                return 'text'
        
        return 'other'
    
    def _is_id_column(self, series: pd.Series) -> bool:
        """Check if column appears to be an ID column"""
        # Check column name
        name_lower = str(series.name).lower() if series.name else ''
        if any(id_term in name_lower for id_term in ['id', 'key', 'uuid', 'guid']):
            return True
        
        # Check if all values are unique
        if len(series) > 10 and series.nunique() == len(series):
            return True
        
        return False
    
    def _can_convert_to_datetime(self, series: pd.Series, sample_size: int = 100) -> bool:
        """Check if series can be converted to datetime"""
        try:
            sample = series.dropna().head(sample_size)
            if len(sample) == 0:
                return False
            
            # Try to convert without warnings by using format inference
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pd.to_datetime(sample, errors='raise')
            return True
        except:
            return False
    
    def get_numeric_summary(self, series: pd.Series) -> Dict[str, Any]:
        """
        Get statistical summary for numeric column.
        
        Args:
            series: Numeric Series
            
        Returns:
            Dictionary with statistics
        """
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return {'error': 'No valid data'}
        
        try:
            mean_val = clean_series.mean()
            std_val = clean_series.std()
            return {
                'count': int(len(clean_series)),
                'mean': float(mean_val) if pd.notna(mean_val) and not isinstance(mean_val, complex) else 0.0,
                'median': float(clean_series.median()) if pd.notna(clean_series.median()) else 0.0,
                'std': float(std_val) if pd.notna(std_val) and not isinstance(std_val, complex) else 0.0,
                'min': self._safe_float(clean_series.min()),
                'max': self._safe_float(clean_series.max()),
                'q25': float(clean_series.quantile(0.25)) if pd.notna(clean_series.quantile(0.25)) else 0.0,
                'q75': float(clean_series.quantile(0.75)) if pd.notna(clean_series.quantile(0.75)) else 0.0,
                'skewness': float(clean_series.skew()) if pd.notna(clean_series.skew()) else 0.0,  # type: ignore[arg-type]
                'kurtosis': float(clean_series.kurtosis()) if pd.notna(clean_series.kurtosis()) else 0.0,  # type: ignore[arg-type]
                'variance': float(clean_series.var()) if pd.notna(clean_series.var()) else 0.0,  # type: ignore[arg-type]
                'range': self._safe_float(clean_series.max() - clean_series.min()) if pd.notna(clean_series.max()) and pd.notna(clean_series.min()) else 0.0,
                'iqr': float(clean_series.quantile(0.75) - clean_series.quantile(0.25)) if pd.notna(clean_series.quantile(0.75)) and pd.notna(clean_series.quantile(0.25)) else 0.0,
                'cv': float(std_val / mean_val) if pd.notna(mean_val) and pd.notna(std_val) and mean_val != 0 and not isinstance(mean_val, complex) and not isinstance(std_val, complex) else None,
            }
        except (TypeError, ValueError):
            return {'error': 'Cannot compute numeric statistics'}
    
    def get_categorical_summary(self, series: pd.Series) -> Dict[str, Any]:
        """
        Get summary for categorical column.
        
        Args:
            series: Categorical Series
            
        Returns:
            Dictionary with category information
        """
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return {'error': 'No valid data'}
        
        value_counts = clean_series.value_counts()
        
        return {
            'count': int(len(clean_series)),
            'unique': int(series.nunique()),
            'top': str(value_counts.index[0]) if len(value_counts) > 0 else None,
            'top_freq': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            'top_percent': float(value_counts.iloc[0] / len(clean_series) * 100) if len(value_counts) > 0 else 0,
            'distribution': {
                str(k): int(v) for k, v in value_counts.head(10).items()
            },
            'entropy': float(stats.entropy(value_counts)),
            'mode_count': int(len(clean_series[clean_series == value_counts.index[0]])) if len(value_counts) > 0 else 0,
        }
    
    def get_text_summary(self, series: pd.Series) -> Dict[str, Any]:
        """
        Get summary for text column.
        
        Args:
            series: Text Series
            
        Returns:
            Dictionary with text statistics
        """
        clean_series = series.dropna().astype(str)
        
        if len(clean_series) == 0:
            return {'error': 'No valid data'}
        
        lengths = clean_series.str.len()
        
        return {
            'count': int(len(clean_series)),
            'unique': int(series.nunique()),
            'mean_length': float(lengths.mean()),
            'min_length': self._safe_int(lengths.min()),
            'max_length': self._safe_int(lengths.max()),
            'median_length': self._safe_float(lengths.median()),
            'empty_strings': int((clean_series == '').sum()),
        }
    
    def get_datetime_summary(self, series: pd.Series) -> Dict[str, Any]:
        """
        Get summary for datetime column.
        
        Args:
            series: Datetime Series
            
        Returns:
            Dictionary with datetime statistics
        """
        # Try to convert if not already datetime
        if not pd.api.types.is_datetime64_any_dtype(series):
            try:
                series = pd.to_datetime(series, errors='coerce')
            except:
                return {'error': 'Cannot convert to datetime'}
        
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return {'error': 'No valid data'}
        
        try:
            min_val = clean_series.min()
            max_val = clean_series.max()
            range_val = max_val - min_val
            
            return {
                'count': int(len(clean_series)),
                'min': str(min_val),
                'max': str(max_val),
                'range_days': int(range_val.days) if hasattr(range_val, 'days') else 0,
                'unique': int(series.nunique()),
            }
        except (TypeError, AttributeError):
            return {'error': 'Cannot compute datetime statistics'}
    
    def analyze_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze missing value patterns.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with missing value analysis
        """
        missing_count = df.isna().sum()
        missing_percent = (missing_count / len(df)) * 100
        
        # Identify columns with missing values
        columns_with_missing = missing_count[missing_count > 0].sort_values(ascending=False)
        
        # Missing value patterns
        missing_patterns = {}
        if len(columns_with_missing) > 0:
            # Check for rows with all missing
            all_missing_rows = df.isna().all(axis=1).sum()
            
            # Check for columns with all missing
            all_missing_cols = df.isna().all(axis=0).sum()
            
            missing_patterns = {
                'rows_all_missing': int(all_missing_rows),  # type: ignore[arg-type]
                'cols_all_missing': int(all_missing_cols),  # type: ignore[arg-type]
            }
        
        return {
            'total_missing': int(missing_count.sum()),
            'total_cells': int(df.size),
            'percent_missing': float((missing_count.sum() / df.size) * 100),
            'columns_with_missing': {
                col: {
                    'count': int(missing_count[col]),  # type: ignore[arg-type]
                    'percent': float(missing_percent[col])  # type: ignore[arg-type]
                }
                for col in columns_with_missing.index
            },
            'patterns': missing_patterns,
        }
    
    def detect_outliers(self, series: pd.Series, method: str = 'zscore') -> Dict[str, Any]:
        """
        Detect outliers in numeric column.
        
        Args:
            series: Numeric Series
            method: Detection method ('zscore', 'iqr', 'isolation_forest')
            
        Returns:
            Dictionary with outlier information
        """
        clean_series = series.dropna()
        
        if len(clean_series) == 0 or not pd.api.types.is_numeric_dtype(clean_series):
            return {'error': 'No valid numeric data'}
        
        try:
            if method == 'zscore':
                z_scores = np.abs(stats.zscore(clean_series))
                outliers = z_scores > self.OUTLIER_Z_SCORE
            elif method == 'iqr':
                Q1 = clean_series.quantile(0.25)
                Q3 = clean_series.quantile(0.75)
                IQR = Q3 - Q1
                outliers = (clean_series < (Q1 - 1.5 * IQR)) | (clean_series > (Q3 + 1.5 * IQR))
            else:
                return {'error': f'Unknown method: {method}'}
        except (TypeError, ValueError):
            return {'error': 'Cannot compute outliers for this data type'}
        
        outlier_values = clean_series[outliers]
        
        return {
            'method': method,
            'count': int(outliers.sum()),
            'percent': float((outliers.sum() / len(clean_series)) * 100),
            'indices': outlier_values.index.tolist()[:100],  # Limit to first 100
            'values': outlier_values.values.tolist()[:100],
            'has_outliers': bool(outliers.any()),
        }
    
    def analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze correlations between numeric columns.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with correlation analysis
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns'}
        
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= self.CORRELATION_THRESHOLD:  # type: ignore[arg-type,operator]
                    strong_correlations.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': float(corr_value),  # type: ignore[arg-type]
                        'strength': 'positive' if corr_value > 0 else 'negative'  # type: ignore[operator]
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'max_correlation': float(corr_matrix.abs().max().max()) if len(corr_matrix) > 0 else 0,
        }
    
    def assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess overall data quality.
        
        Args:
            df: DataFrame to assess
            
        Returns:
            Dictionary with quality metrics
        """
        missing_analysis = self.analyze_missing_values(df)
        
        # Check for duplicates
        duplicate_rows = df.duplicated().sum()
        
        # Check data types consistency
        type_issues = []
        for col in df.columns:
            col_type = self.detect_column_type(df[col])
            if col_type == 'unknown':
                type_issues.append(col)
        
        # Calculate quality score (0-100)
        quality_score = 100
        
        # Deduct for missing values
        quality_score -= min(missing_analysis['percent_missing'], 30)
        
        # Deduct for duplicates
        duplicate_percent = (duplicate_rows / len(df)) * 100
        quality_score -= min(duplicate_percent, 20)
        
        # Deduct for type issues
        quality_score -= min(len(type_issues) * 5, 20)
        
        quality_score = max(0, quality_score)
        
        return {
            'quality_score': float(quality_score),
            'rating': self._get_quality_rating(quality_score),
            'rows': int(len(df)),
            'columns': int(len(df.columns)),
            'duplicate_rows': int(duplicate_rows),
            'duplicate_percent': float(duplicate_percent),
            'missing_percent': float(missing_analysis['percent_missing']),
            'type_issues': type_issues,
            'issues': self._generate_quality_issues(df, missing_analysis, duplicate_rows),
        }
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert quality score to rating"""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Fair'
        elif score >= 40:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _generate_quality_issues(
        self, 
        df: pd.DataFrame, 
        missing_analysis: Dict,
        duplicate_rows: int
    ) -> List[str]:
        """Generate list of data quality issues"""
        issues = []
        
        if missing_analysis['percent_missing'] > 10:
            issues.append(f"High missing values: {missing_analysis['percent_missing']:.1f}%")
        
        if duplicate_rows > 0:
            issues.append(f"Contains {duplicate_rows} duplicate rows")
        
        for col, info in missing_analysis['columns_with_missing'].items():
            if info['percent'] > self.HIGH_MISSING_THRESHOLD * 100:
                issues.append(f"Column '{col}' has {info['percent']:.1f}% missing values")
        
        return issues
    
    def profile_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Create comprehensive profile for a single column.
        
        Args:
            series: Pandas Series to profile
            
        Returns:
            Dictionary with column profile
        """
        col_type = self.detect_column_type(series)
        
        profile = {
            'name': series.name,
            'type': col_type,
            'dtype': str(series.dtype),
            'count': int(len(series)),
            'missing': int(series.isna().sum()),
            'missing_percent': float((series.isna().sum() / len(series)) * 100),
            'unique': int(series.nunique()),
            'unique_percent': float((series.nunique() / len(series)) * 100),
        }
        
        # Add type-specific summary
        if col_type == 'numeric':
            profile['summary'] = self.get_numeric_summary(series)
            profile['outliers'] = self.detect_outliers(series)
        elif col_type == 'categorical':
            profile['summary'] = self.get_categorical_summary(series)
        elif col_type == 'text':
            profile['summary'] = self.get_text_summary(series)
        elif col_type == 'datetime':
            profile['summary'] = self.get_datetime_summary(series)
        
        return profile
    
    def profile_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create comprehensive profile for entire dataset.
        
        Args:
            df: DataFrame to profile
            
        Returns:
            Dictionary with complete dataset profile
        """
        logger.info(f"Profiling dataset: {len(df)} rows, {len(df.columns)} columns")
        
        # Overall statistics
        profile = {
            'overview': {
                'rows': int(len(df)),
                'columns': int(len(df.columns)),
                'memory_mb': float(df.memory_usage(deep=True).sum() / (1024 * 1024)),
                'duplicates': int(df.duplicated().sum()),
            },
            'columns': {},
            'missing_analysis': self.analyze_missing_values(df),
            'quality': self.assess_data_quality(df),
        }
        
        # Profile each column
        for col in df.columns:
            profile['columns'][col] = self.profile_column(df[col])
        
        # Add correlation analysis for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            profile['correlations'] = self.analyze_correlations(df)
        
        logger.info(f"Profile complete. Quality score: {profile['quality']['quality_score']:.1f}")
        
        return profile
    
    def get_insights(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Generate human-readable insights about the dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of insight dictionaries with type and message
        """
        insights = []
        profile = self.profile_dataset(df)
        
        # Data quality insights
        quality = profile['quality']
        insights.append({
            'type': 'quality',
            'severity': 'info' if quality['quality_score'] >= 75 else 'warning',
            'message': f"Data quality: {quality['rating']} ({quality['quality_score']:.0f}/100)"
        })
        
        # Missing values insights
        if quality['missing_percent'] > 10:
            insights.append({
                'type': 'missing',
                'severity': 'warning',
                'message': f"{quality['missing_percent']:.1f}% of data is missing"
            })
        
        # Duplicate insights
        if quality['duplicate_rows'] > 0:
            insights.append({
                'type': 'duplicates',
                'severity': 'warning',
                'message': f"Found {quality['duplicate_rows']} duplicate rows ({quality['duplicate_percent']:.1f}%)"
            })
        
        # Column-specific insights
        for col_name, col_profile in profile['columns'].items():
            if col_profile['type'] == 'numeric' and 'outliers' in col_profile:
                outliers = col_profile['outliers']
                if outliers.get('has_outliers'):
                    insights.append({
                        'type': 'outliers',
                        'severity': 'info',
                        'message': f"Column '{col_name}' has {outliers['count']} outliers ({outliers['percent']:.1f}%)"
                    })
        
        # Correlation insights
        if 'correlations' in profile:
            strong_corr = profile['correlations'].get('strong_correlations', [])
            for corr in strong_corr[:3]:  # Top 3
                insights.append({
                    'type': 'correlation',
                    'severity': 'info',
                    'message': f"Strong {corr['strength']} correlation between '{corr['col1']}' and '{corr['col2']}' ({corr['correlation']:.2f})"
                })
        
        return insights
