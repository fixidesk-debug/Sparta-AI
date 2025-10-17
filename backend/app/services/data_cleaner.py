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
        # Validate input types and basic invariants early to avoid bypasses
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        allowed_strategies = {'auto', 'drop', 'mean', 'median', 'mode', 'forward', 'backward', 'constant', 'knn'}
        if strategy not in allowed_strategies:
            raise ValueError(f"Unknown strategy: {strategy}")

        df_clean = df.copy()

        # Determine target columns and validate existence to avoid unexpected behavior
        if columns is None:
            columns = df_clean.columns.tolist()
        else:
            # Keep only columns that actually exist and warn about missing ones
            valid_columns = [c for c in columns if c in df_clean.columns]
            missing_columns = [c for c in columns if c not in df_clean.columns]
            if missing_columns:
                logger.warning(f"Requested columns not found and will be skipped: {missing_columns}")
            columns = valid_columns

        # Small helper functions reduce per-function branching and keep logic testable
        def _fill_statistic(col: str, stat: str) -> None:
            if not df_clean[col].isna().any():
                return
            if stat == 'mean' and pd.api.types.is_numeric_dtype(df_clean[col]):
                value = df_clean[col].mean()
            elif stat == 'median' and pd.api.types.is_numeric_dtype(df_clean[col]):
                value = df_clean[col].median()
            elif stat == 'mode':
                mode_vals = df_clean[col].mode()
                value = mode_vals[0] if len(mode_vals) > 0 else None
            else:
                # Nothing to do for non-applicable types
                return
            if value is not None:
                df_clean.loc[:, col] = df_clean[col].fillna(value)

        def _fill_forward_backward(cols: List[str], method: str) -> None:
            if not cols:
                return
            if method == 'forward':
                df_clean.loc[:, cols] = df_clean[cols].ffill()
            else:
                df_clean.loc[:, cols] = df_clean[cols].bfill()

        def _fill_constant(cols: List[str], value: Any) -> None:
            if value is None:
                logger.warning("fill_value is None for 'constant' strategy; defaulting to 0")
                value_to_use = 0
            else:
                value_to_use = value
            if cols:
                df_clean.loc[:, cols] = df_clean[cols].fillna(value_to_use)

        def _knn_impute(numeric_cols: List[str]) -> None:
            if not numeric_cols:
                return
            imputer = KNNImputer(n_neighbors=5)
            # KNNImputer returns numpy array; preserve column order
            try:
                imputed = imputer.fit_transform(df_clean[numeric_cols])
                df_clean.loc[:, numeric_cols] = imputed
            except Exception as e:
                logger.error(f"KNN imputation failed: {e}")
                raise

        # Strategy dispatch to keep branching shallow in this function
        if strategy == 'drop':
            initial_rows = len(df_clean)
            df_clean = df_clean.dropna(subset=columns)
            logger.info(f"Dropped {initial_rows - len(df_clean)} rows with missing values")

        elif strategy == 'auto':
            # Per-column automatic policy
            for col in columns:
                if not df_clean[col].isna().any():
                    continue
                if pd.api.types.is_numeric_dtype(df_clean[col]):
                    # Prefer median for robustness
                    _fill_statistic(col, 'median')
                elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                    # Forward-fill datetimes
                    _fill_forward_backward([col], 'forward')
                else:
                    # Categorical/text -> mode
                    _fill_statistic(col, 'mode')

        elif strategy in {'mean', 'median', 'mode'}:
            for col in columns:
                _fill_statistic(col, strategy)

        elif strategy in {'forward', 'backward'}:
            _fill_forward_backward(columns, strategy)

        elif strategy == 'constant':
            _fill_constant(columns, fill_value)

        elif strategy == 'knn':
            numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df_clean[col])]
            _knn_impute(numeric_cols)

        # Return cleaned copy (explicit, no in-place surprises)
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
        
        # Ensure mask is a boolean Series indexed to df_clean
        mask = pd.Series(True, index=df_clean.index, dtype=bool)
        
        for col in columns:
            if not pd.api.types.is_numeric_dtype(df_clean[col]):
                continue
            
            clean_col = df_clean[col].dropna()
            
            if method == 'iqr':
                Q1 = clean_col.quantile(0.25)
                Q3 = clean_col.quantile(0.75)
                IQR = Q3 - Q1
                # If IQR is zero there is no spread; skip this column
                if IQR == 0 or np.isclose(IQR, 0.0):
                    continue
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                # Use explicit parentheses to avoid precedence mistakes and ensure correct boolean logic
                condition = ((df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)) | (df_clean[col].isna())
                mask &= condition
            
            elif method == 'zscore':
                mean = clean_col.mean()
                std = clean_col.std()
                # Guard against zero std to avoid division by zero and unintended masking
                if std == 0 or np.isclose(std, 0.0):
                    continue
                z_scores = np.abs((df_clean[col] - mean) / std)
                condition = (z_scores <= threshold) | (df_clean[col].isna())
                mask &= condition
        
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
        # Basic validation to avoid unexpected bypasses or misuse
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        allowed_methods = {'iqr', 'percentile'}
        if method not in allowed_methods:
            raise ValueError(f"Unknown method: {method}. Allowed: {sorted(allowed_methods)}")
        if not isinstance(threshold, (int, float)) or threshold < 0:
            raise ValueError("threshold must be a non-negative number")
        
        df_clean = df.copy()
        
        # Determine numeric columns (and validate requested columns)
        if columns is None:
            columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        else:
            # Keep only columns that exist and are numeric; warn about others
            valid_columns = [c for c in columns if c in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[c])]
            missing_columns = [c for c in columns if c not in df_clean.columns]
            non_numeric = [c for c in columns if c in df_clean.columns and not pd.api.types.is_numeric_dtype(df_clean[c])]
            if missing_columns:
                logger.warning(f"Requested columns not found and will be skipped: {missing_columns}")
            if non_numeric:
                logger.warning(f"Requested non-numeric columns will be skipped: {non_numeric}")
            columns = valid_columns
        
        if not columns:
            logger.info("No numeric columns to cap; returning original DataFrame")
            return df_clean
        
        for col in columns:
            # Use dropna for robust quantile/std computation
            non_na = df_clean[col].dropna()
            if non_na.empty:
                # Nothing to cap in an all-NA column
                continue
            
            if method == 'iqr':
                Q1 = non_na.quantile(0.25)
                Q3 = non_na.quantile(0.75)
                IQR = Q3 - Q1
                # If IQR is zero there is no variability; skip capping for this column
                if IQR == 0 or np.isclose(IQR, 0.0):
                    logger.debug(f"Skipping IQR capping for column '{col}' due to zero IQR")
                    continue
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
            elif method == 'percentile':
                # Use robust percentiles computed on non-NA values
                lower_bound = non_na.quantile(0.01)
                upper_bound = non_na.quantile(0.99)
                # If bounds are NaN or equal, skip
                if pd.isna(lower_bound) or pd.isna(upper_bound) or np.isclose(lower_bound, upper_bound):
                    logger.debug(f"Skipping percentile capping for column '{col}' due to invalid bounds")
                    continue
            else:
                # This branch should not be reached due to earlier validation
                continue
            
            # Cap values while preserving NaNs
            df_clean[col] = df_clean[col].where(df_clean[col].isna(), df_clean[col].clip(lower=lower_bound, upper=upper_bound))
        
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
        # Basic validation
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if not isinstance(method, str):
            raise TypeError("method must be a string")

        df_clean = df.copy()

        # Determine numeric columns (and validate requested columns)
        if columns is None:
            columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        else:
            # Keep only existing numeric columns and warn about others
            valid_columns = [c for c in columns if c in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[c])]
            missing_columns = [c for c in columns if c not in df_clean.columns]
            non_numeric = [c for c in columns if c in df_clean.columns and not pd.api.types.is_numeric_dtype(df_clean[c])]
            if missing_columns:
                logger.warning(f"Requested columns not found and will be skipped: {missing_columns}")
            if non_numeric:
                logger.warning(f"Requested non-numeric columns will be skipped: {non_numeric}")
            columns = valid_columns

        if not columns:
            logger.info("No numeric columns to normalize; returning original DataFrame")
            return df_clean

        # Select scaler
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown normalization method: {method}")

        # Fit and transform with error handling; ensure we operate on a copy
        try:
            scaled_values = scaler.fit_transform(df_clean[columns])
            # Preserve column alignment and types
            df_clean.loc[:, columns] = scaled_values
        except Exception as e:
            logger.error(f"Normalization failed for columns {columns} with method '{method}': {e}")
            raise

        # Store scaler keyed by the tuple of columns to avoid incorrectly re-using a single scaler per-column
        key = tuple(columns)
        self.scalers[key] = scaler

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
        method: str = 'onehot',
        target_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Encode categorical variables.
        
        Args:
            df: DataFrame to encode
            columns: Categorical columns (None = all object/category columns)
            method: Encoding method:
                - 'onehot': One-hot encoding
                - 'label': Label encoding (ordinal)
                - 'target': Target encoding (requires target_column)
            target_column: Required when method == 'target' to compute target statistics
            
        Returns:
            DataFrame with encoded categories
        """
        # Validate inputs early to avoid unintended modifications or information leaks
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if not isinstance(method, str):
            raise TypeError("method must be a string")

        allowed_methods = {'onehot', 'label', 'target'}
        if method not in allowed_methods:
            raise ValueError(f"Unknown encoding method: {method}. Allowed: {sorted(allowed_methods)}")

        df_clean = df.copy()

        # Default to object/category columns if none specified
        if columns is None:
            columns = df_clean.select_dtypes(include=['object', 'category']).columns.tolist()
        else:
            # Keep only columns that actually exist to avoid encoding unintended data
            valid_columns = [c for c in columns if c in df_clean.columns]
            missing_columns = [c for c in columns if c not in df_clean.columns]
            if missing_columns:
                logger.warning(f"Requested columns not found and will be skipped: {missing_columns}")
            columns = valid_columns

        # For target encoding, require a valid target column and exclude it from encoding set
        if method == 'target':
            if not target_column:
                raise ValueError("target_column must be provided for 'target' encoding")
            if target_column not in df_clean.columns:
                raise ValueError(f"Specified target_column '{target_column}' not found in DataFrame")
            # Ensure we do not accidentally encode the target column itself
            if target_column in columns:
                columns = [c for c in columns if c != target_column]
                logger.debug(f"Excluded target column '{target_column}' from encoding columns")

        # Nothing to do if no valid columns remain
        if not columns:
            logger.info("No categorical columns to encode; returning original DataFrame")
            return df_clean

        if method == 'onehot':
            # Use get_dummies safely on the explicit column list
            try:
                df_clean = pd.get_dummies(df_clean, columns=columns, prefix=columns, drop_first=False, dummy_na=False)
                logger.info(f"One-hot encoded {len(columns)} columns")
            except Exception as e:
                logger.error(f"One-hot encoding failed for columns {columns}: {e}")
                raise

        elif method == 'label':
            for col in columns:
                try:
                    # Preserve NaNs as -1 by using categorical codes
                    df_clean[col] = df_clean[col].astype('category').cat.codes
                except Exception as e:
                    logger.error(f"Label encoding failed for column '{col}': {e}")
                    raise
            logger.info(f"Label encoded {len(columns)} columns")

        elif method == 'target':
            # Simple target encoding: replace category by mean(target) for that category.
            # Use a new column to avoid overwriting original category unless explicitly desired.
            for col in columns:
                try:
                    # Compute mapping on training data (here, the provided df)
                    mapping = df_clean.groupby(col)[target_column].mean()
                    # Map values; preserve NaNs
                    encoded_col = df_clean[col].map(mapping)
                    # Create a new column name to make operation explicit and avoid accidental overwrites
                    new_col_name = f"{col}_te"
                    df_clean[new_col_name] = encoded_col
                except Exception as e:
                    logger.error(f"Target encoding failed for column '{col}': {e}")
                    raise
            logger.info(f"Target encoded {len(columns)} columns using target '{target_column}'")

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
        # Basic validation to prevent accidental bypasses or KeyError/unauthorized access
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if not isinstance(target_column, str):
            raise TypeError("target_column must be a string")
        if target_column not in df.columns:
            raise ValueError(f"target_column '{target_column}' not found in DataFrame")
        allowed_methods = {'oversample', 'undersample'}
        if method not in allowed_methods:
            raise ValueError(f"Unknown balancing method: {method}. Allowed: {sorted(allowed_methods)}")

        df_clean = df.copy()

        # Ensure target column has meaningful values (no silent handling of all-NA targets)
        if df_clean[target_column].isna().all():
            raise ValueError(f"target_column '{target_column}' contains only missing values; please provide a valid target.")

        # Compute class counts explicitly and exclude rows with NA target to avoid ambiguous behavior
        if df_clean[target_column].isna().any():
            logger.warning(f"Rows with missing values in target_column '{target_column}' will be excluded from balancing")
            df_clean = df_clean[df_clean[target_column].notna()]

        # Get class counts (use value_counts on the cleaned target)
        class_counts = df_clean[target_column].value_counts()

        if len(class_counts) <= 1:
            # Nothing meaningful to balance if only one class remains
            logger.info("Target has a single class after preprocessing; returning original DataFrame")
            return df_clean

        if method == 'oversample':
            # Oversample minority classes to match majority
            max_size = int(class_counts.max())
            balanced_dfs = []

            for class_label in class_counts.index:
                class_df = df_clean[df_clean[target_column] == class_label]
                # If class_df is empty (defensive), skip
                if class_df.empty:
                    logger.debug(f"Skipping empty class '{class_label}' during oversampling")
                    continue
                balanced_dfs.append(class_df.sample(max_size, replace=True, random_state=42))

            if not balanced_dfs:
                logger.info("No classes available to oversample; returning original DataFrame")
                return df_clean

            df_clean = pd.concat(balanced_dfs, ignore_index=True)

        elif method == 'undersample':
            # Undersample majority classes to match minority
            min_size = int(class_counts.min())
            balanced_dfs = []

            for class_label in class_counts.index:
                class_df = df_clean[df_clean[target_column] == class_label]
                if class_df.empty:
                    logger.debug(f"Skipping empty class '{class_label}' during undersampling")
                    continue
                balanced_dfs.append(class_df.sample(min_size, replace=False, random_state=42))

            if not balanced_dfs:
                logger.info("No classes available to undersample; returning original DataFrame")
                return df_clean

            df_clean = pd.concat(balanced_dfs, ignore_index=True)

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
