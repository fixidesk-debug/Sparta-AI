"""
Data Cleaner

Common data cleaning and preprocessing operations with intelligent suggestions.

Features:
- Missing value handling (multiple strategies)
- Outlier detection and treatment
- Duplicate removal
- Data normalization and scaling
- Type conversions
- Text cleaning
- Feature encoding

Author: Sparta AI Team
Date: October 14, 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import KNNImputer
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaning and preprocessing operations.
    
    Provides intelligent data cleaning with multiple strategies:
    - Missing value imputation
    - Outlier handling
    - Duplicate removal
    - Normalization
    - Type conversions
    
    Example:
        >>> cleaner = DataCleaner()
        >>> df_clean = cleaner.handle_missing_values(df, strategy='mean')
        >>> df_clean = cleaner.remove_outliers(df_clean, columns=['age', 'salary'])
    """
    
    def __init__(self):
        """Initialize DataCleaner"""
        self.scalers: Dict[str, Any] = {}
        self.imputers: Dict[str, Any] = {}
    
    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = 'auto',
        columns: Optional[List[str]] = None,
        fill_value: Any = None
    ) -> pd.DataFrame:
        """
        Handle missing values with various strategies.
        
        Args:
            df: DataFrame to clean
            strategy: Strategy to use:
                - 'auto': Automatic strategy based on data type
                - 'drop': Drop rows with missing values
                - 'mean': Fill with mean (numeric only)
                - 'median': Fill with median (numeric only)
                - 'mode': Fill with most frequent value
                - 'forward': Forward fill
                - 'backward': Backward fill
                - 'constant': Fill with constant value
                - 'knn': KNN imputation
            columns: Specific columns to process (None = all)
            fill_value: Value for 'constant' strategy
            
        Returns:
            DataFrame with handled missing values
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df.columns.tolist()
        
        if strategy == 'drop':
            initial_rows = len(df_clean)
            df_clean = df_clean.dropna(subset=columns)
            logger.info(f"Dropped {initial_rows - len(df_clean)} rows with missing values")
        
        elif strategy == 'auto':
            # Automatic strategy based on data type
            for col in columns:
                if df_clean[col].isna().any():
                    if pd.api.types.is_numeric_dtype(df_clean[col]):
                        # Use median for numeric
                        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                    elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                        # Forward fill for datetime
                        df_clean[col] = df_clean[col].ffill()
                    else:
                        # Use mode for categorical
                        mode_value = df_clean[col].mode()
                        if len(mode_value) > 0:
                            df_clean[col] = df_clean[col].fillna(mode_value[0])
        
        elif strategy in ['mean', 'median', 'mode']:
            for col in columns:
                if df_clean[col].isna().any():
                    if strategy == 'mean' and pd.api.types.is_numeric_dtype(df_clean[col]):
                        df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
                    elif strategy == 'median' and pd.api.types.is_numeric_dtype(df_clean[col]):
                        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                    elif strategy == 'mode':
                        mode_value = df_clean[col].mode()
                        if len(mode_value) > 0:
                            df_clean[col] = df_clean[col].fillna(mode_value[0])
        
        elif strategy == 'forward':
            df_clean[columns] = df_clean[columns].ffill()
        
        elif strategy == 'backward':
            df_clean[columns] = df_clean[columns].bfill()
        
        elif strategy == 'constant':
            if fill_value is None:
                fill_value = 0
            df_clean[columns] = df_clean[columns].fillna(fill_value)
        
        elif strategy == 'knn':
            # KNN imputation for numeric columns
            numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df_clean[col])]
            if numeric_cols:
                imputer = KNNImputer(n_neighbors=5)
                df_clean[numeric_cols] = imputer.fit_transform(df_clean[numeric_cols])
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return df_clean
    
    def remove_duplicates(
        self,
        df: pd.DataFrame,
        subset: Optional[List[str]] = None,
        keep: str = 'first'
    ) -> pd.DataFrame:
        """
        Remove duplicate rows.
        
        Args:
            df: DataFrame to clean
            subset: Columns to consider for duplicates (None = all)
            keep: Which duplicates to keep ('first', 'last', False)
            
        Returns:
            DataFrame without duplicates
        """
        initial_rows = len(df)
        # Type cast to satisfy pandas literal type requirement
        if keep == 'first':
            keep_param = 'first'
        elif keep == 'last':
            keep_param = 'last'
        else:
            keep_param = False
        df_clean = df.drop_duplicates(subset=subset, keep=keep_param)
        removed = initial_rows - len(df_clean)
        
        if removed > 0:
            logger.info(f"Removed {removed} duplicate rows ({removed/initial_rows*100:.1f}%)")
        
        return df_clean
    
    def remove_outliers(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Remove outliers from numeric columns.
        
        Args:
            df: DataFrame to clean
            columns: Numeric columns to check (None = all numeric)
            method: Detection method ('iqr', 'zscore')
            threshold: Threshold for outlier detection
                - IQR: multiplier (default 1.5)
                - Z-score: number of standard deviations (default 3)
            
        Returns:
            DataFrame with outliers removed
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        
        mask = pd.Series([True] * len(df_clean), index=df_clean.index)
        
        for col in columns:
            if not pd.api.types.is_numeric_dtype(df_clean[col]):
                continue
            
            clean_col = df_clean[col].dropna()
            
            if method == 'iqr':
                Q1 = clean_col.quantile(0.25)
                Q3 = clean_col.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                mask &= (df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound) | df_clean[col].isna()
            
            elif method == 'zscore':
                mean = clean_col.mean()
                std = clean_col.std()
                z_scores = np.abs((df_clean[col] - mean) / std)
                mask &= (z_scores <= threshold) | df_clean[col].isna()
        
        initial_rows = len(df_clean)
        df_clean = df_clean[mask]
        removed = initial_rows - len(df_clean)
        
        if removed > 0:
            logger.info(f"Removed {removed} rows with outliers ({removed/initial_rows*100:.1f}%)")
        
        return df_clean
    
    def cap_outliers(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """
        Cap outliers instead of removing them (Winsorization).
        
        Args:
            df: DataFrame to clean
            columns: Numeric columns to cap (None = all numeric)
            method: Detection method ('iqr', 'percentile')
            threshold: Threshold for outlier detection
            
        Returns:
            DataFrame with capped outliers
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if not pd.api.types.is_numeric_dtype(df_clean[col]):
                continue
            
            if method == 'iqr':
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
            elif method == 'percentile':
                lower_bound = df_clean[col].quantile(0.01)
                upper_bound = df_clean[col].quantile(0.99)
            else:
                continue
            
            # Cap values
            df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
        
        logger.info(f"Capped outliers in {len(columns)} columns")
        
        return df_clean
    
    def normalize_column(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'standard'
    ) -> pd.DataFrame:
        """
        Normalize/scale numeric columns.
        
        Args:
            df: DataFrame to normalize
            columns: Columns to normalize (None = all numeric)
            method: Normalization method:
                - 'standard': StandardScaler (mean=0, std=1)
                - 'minmax': MinMaxScaler (range 0-1)
                - 'robust': RobustScaler (median and IQR)
            
        Returns:
            DataFrame with normalized columns
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        
        # Select scaler
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        # Fit and transform
        df_clean[columns] = scaler.fit_transform(df_clean[columns])
        
        # Store scaler for later use
        for col in columns:
            self.scalers[col] = scaler
        
        logger.info(f"Normalized {len(columns)} columns using {method} scaling")
        
        return df_clean
    
    def convert_types(
        self,
        df: pd.DataFrame,
        type_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Convert column data types.
        
        Args:
            df: DataFrame to convert
            type_mapping: Dict mapping column names to target types
                          Types: 'int', 'float', 'str', 'category', 'datetime', 'bool'
            
        Returns:
            DataFrame with converted types
        """
        df_clean = df.copy()
        
        for col, target_type in type_mapping.items():
            if col not in df_clean.columns:
                logger.warning(f"Column '{col}' not found, skipping")
                continue
            
            try:
                if target_type == 'int':
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').astype('Int64')
                elif target_type == 'float':
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                elif target_type == 'str':
                    df_clean[col] = df_clean[col].astype(str)
                elif target_type == 'category':
                    df_clean[col] = df_clean[col].astype('category')
                elif target_type == 'datetime':
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                elif target_type == 'bool':
                    df_clean[col] = df_clean[col].astype(bool)
                else:
                    logger.warning(f"Unknown type '{target_type}' for column '{col}'")
                
                logger.info(f"Converted '{col}' to {target_type}")
            
            except Exception as e:
                logger.error(f"Failed to convert '{col}' to {target_type}: {e}")
        
        return df_clean
    
    def clean_text(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        lowercase: bool = True,
        remove_punctuation: bool = False,
        remove_numbers: bool = False,
        strip_whitespace: bool = True
    ) -> pd.DataFrame:
        """
        Clean text columns.
        
        Args:
            df: DataFrame to clean
            columns: Text columns to clean (None = all object columns)
            lowercase: Convert to lowercase
            remove_punctuation: Remove punctuation
            remove_numbers: Remove numbers
            strip_whitespace: Strip leading/trailing whitespace
            
        Returns:
            DataFrame with cleaned text
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.select_dtypes(include=['object']).columns.tolist()
        
        for col in columns:
            if col not in df_clean.columns:
                continue
            
            # Convert to string
            df_clean[col] = df_clean[col].astype(str)
            
            if lowercase:
                df_clean[col] = df_clean[col].str.lower()
            
            if strip_whitespace:
                df_clean[col] = df_clean[col].str.strip()
            
            if remove_punctuation:
                df_clean[col] = df_clean[col].str.replace(r'[^\w\s]', '', regex=True)
            
            if remove_numbers:
                df_clean[col] = df_clean[col].str.replace(r'\d+', '', regex=True)
        
        logger.info(f"Cleaned text in {len(columns)} columns")
        
        return df_clean
    
    def encode_categorical(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'onehot'
    ) -> pd.DataFrame:
        """
        Encode categorical variables.
        
        Args:
            df: DataFrame to encode
            columns: Categorical columns (None = all object/category columns)
            method: Encoding method:
                - 'onehot': One-hot encoding
                - 'label': Label encoding (ordinal)
                - 'target': Target encoding (requires target column)
            
        Returns:
            DataFrame with encoded categories
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if method == 'onehot':
            df_clean = pd.get_dummies(df_clean, columns=columns, prefix=columns)
            logger.info(f"One-hot encoded {len(columns)} columns")
        
        elif method == 'label':
            for col in columns:
                df_clean[col] = df_clean[col].astype('category').cat.codes
            logger.info(f"Label encoded {len(columns)} columns")
        
        else:
            raise ValueError(f"Unknown encoding method: {method}")
        
        return df_clean
    
    def handle_imbalanced_data(
        self,
        df: pd.DataFrame,
        target_column: str,
        method: str = 'oversample'
    ) -> pd.DataFrame:
        """
        Handle imbalanced datasets.
        
        Args:
            df: DataFrame to balance
            target_column: Target column for balancing
            method: Balancing method:
                - 'oversample': Oversample minority class
                - 'undersample': Undersample majority class
            
        Returns:
            Balanced DataFrame
        """
        df_clean = df.copy()
        
        # Get class counts
        class_counts = df_clean[target_column].value_counts()
        
        if method == 'oversample':
            # Oversample minority classes to match majority
            max_size = class_counts.max()
            balanced_dfs = []
            
            for class_label in class_counts.index:
                class_df = df_clean[df_clean[target_column] == class_label]
                balanced_dfs.append(class_df.sample(max_size, replace=True, random_state=42))
            
            df_clean = pd.concat(balanced_dfs, ignore_index=True)
        
        elif method == 'undersample':
            # Undersample majority classes to match minority
            min_size = class_counts.min()
            balanced_dfs = []
            
            for class_label in class_counts.index:
                class_df = df_clean[df_clean[target_column] == class_label]
                balanced_dfs.append(class_df.sample(min_size, random_state=42))
            
            df_clean = pd.concat(balanced_dfs, ignore_index=True)
        
        else:
            raise ValueError(f"Unknown balancing method: {method}")
        
        logger.info(f"Balanced dataset using {method}: {len(df)} → {len(df_clean)} rows")
        
        return df_clean
    
    def auto_clean(
        self,
        df: pd.DataFrame,
        handle_missing: bool = True,
        remove_duplicates: bool = True,
        handle_outliers: bool = False,
        normalize: bool = False
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Automatic data cleaning with common operations.
        
        Args:
            df: DataFrame to clean
            handle_missing: Handle missing values
            remove_duplicates: Remove duplicate rows
            handle_outliers: Remove or cap outliers
            normalize: Normalize numeric columns
            
        Returns:
            Tuple of (cleaned DataFrame, cleaning report)
        """
        df_clean = df.copy()
        report = {
            'initial_rows': len(df),
            'initial_columns': len(df.columns),
            'operations': []
        }
        
        # Handle missing values
        if handle_missing:
            missing_before = df_clean.isna().sum().sum()
            df_clean = self.handle_missing_values(df_clean, strategy='auto')
            missing_after = df_clean.isna().sum().sum()
            report['operations'].append({
                'operation': 'handle_missing',
                'missing_before': int(missing_before),
                'missing_after': int(missing_after)
            })
        
        # Remove duplicates
        if remove_duplicates:
            rows_before = len(df_clean)
            df_clean = self.remove_duplicates(df_clean)
            report['operations'].append({
                'operation': 'remove_duplicates',
                'removed': int(rows_before - len(df_clean))
            })
        
        # Handle outliers
        if handle_outliers:
            rows_before = len(df_clean)
            df_clean = self.cap_outliers(df_clean, method='iqr')
            report['operations'].append({
                'operation': 'cap_outliers',
                'rows_affected': int(rows_before - len(df_clean))
            })
        
        # Normalize
        if normalize:
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                df_clean = self.normalize_column(df_clean, columns=numeric_cols)
                report['operations'].append({
                    'operation': 'normalize',
                    'columns': numeric_cols
                })
        
        report['final_rows'] = len(df_clean)
        report['final_columns'] = len(df_clean.columns)
        
        logger.info(f"Auto-cleaning complete: {report['initial_rows']} → {report['final_rows']} rows")
        
        return df_clean, report
