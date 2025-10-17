"""
Advanced Data Transformation - AI-Powered Data Cleaning
Intelligent data transformation with AI suggestions
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer, KNNImputer
import logging

logger = logging.getLogger(__name__)


class DataTransformation:
    """Advanced data transformation with AI suggestions"""
    
    @staticmethod
    def suggest_transformations(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Suggest transformations based on data analysis"""
        suggestions = []
        
        # Missing value suggestions
        missing = df.isnull().sum()
        for col in missing[missing > 0].index:
            pct = (missing[col] / len(df)) * 100
            if pct < 5:
                suggestions.append({
                    "type": "impute",
                    "column": col,
                    "method": "mean" if df[col].dtype in [np.float64, np.int64] else "mode",
                    "reason": f"{pct:.1f}% missing - can be imputed",
                    "priority": "high"
                })
            elif pct < 30:
                suggestions.append({
                    "type": "impute",
                    "column": col,
                    "method": "knn",
                    "reason": f"{pct:.1f}% missing - use KNN imputation",
                    "priority": "medium"
                })
            else:
                suggestions.append({
                    "type": "drop",
                    "column": col,
                    "reason": f"{pct:.1f}% missing - consider dropping",
                    "priority": "low"
                })
        
        # Skewness suggestions
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            skew = df[col].skew()
            if abs(skew) > 2:
                suggestions.append({
                    "type": "transform",
                    "column": col,
                    "method": "log" if skew > 0 else "sqrt",
                    "reason": f"Highly skewed ({skew:.2f})",
                    "priority": "medium"
                })
        
        # Outlier suggestions
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 3*IQR) | (df[col] > Q3 + 3*IQR)][col]
            if len(outliers) > 0:
                pct = (len(outliers) / len(df)) * 100
                suggestions.append({
                    "type": "outlier",
                    "column": col,
                    "method": "cap" if pct < 5 else "remove",
                    "reason": f"{len(outliers)} outliers ({pct:.1f}%)",
                    "priority": "medium"
                })
        
        # Categorical encoding suggestions
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            unique_count = df[col].nunique()
            if unique_count == 2:
                suggestions.append({
                    "type": "encode",
                    "column": col,
                    "method": "binary",
                    "reason": "Binary categorical variable",
                    "priority": "high"
                })
            elif unique_count < 10:
                suggestions.append({
                    "type": "encode",
                    "column": col,
                    "method": "onehot",
                    "reason": f"{unique_count} categories - use one-hot encoding",
                    "priority": "high"
                })
            else:
                suggestions.append({
                    "type": "encode",
                    "column": col,
                    "method": "label",
                    "reason": f"{unique_count} categories - use label encoding",
                    "priority": "medium"
                })
        
        return suggestions
    
    @staticmethod
    def apply_transformation(
        df: pd.DataFrame,
        transformation: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, str]:
        """Apply a single transformation"""
        try:
            df_copy = df.copy()
            trans_type = transformation["type"]
            column = transformation.get("column")
            method = transformation.get("method")
            
            if trans_type == "impute":
                df_copy = DataTransformation._impute_missing(df_copy, column, method)
                message = f"Imputed missing values in {column} using {method}"
            
            elif trans_type == "transform":
                df_copy = DataTransformation._apply_math_transform(df_copy, column, method)
                message = f"Applied {method} transformation to {column}"
            
            elif trans_type == "outlier":
                df_copy = DataTransformation._handle_outliers(df_copy, column, method)
                message = f"Handled outliers in {column} using {method}"
            
            elif trans_type == "encode":
                df_copy = DataTransformation._encode_categorical(df_copy, column, method)
                message = f"Encoded {column} using {method}"
            
            elif trans_type == "drop":
                df_copy = df_copy.drop(columns=[column])
                message = f"Dropped column {column}"
            
            elif trans_type == "scale":
                df_copy = DataTransformation._scale_features(df_copy, column, method)
                message = f"Scaled {column} using {method}"
            
            else:
                return df, f"Unknown transformation type: {trans_type}"
            
            return df_copy, message
        
        except Exception as e:
            logger.error(f"Transformation error: {e}")
            return df, f"Error: {str(e)}"
    
    @staticmethod
    def _impute_missing(df: pd.DataFrame, column: str, method: str) -> pd.DataFrame:
        """Impute missing values"""
        if method == "mean":
            df[column].fillna(df[column].mean(), inplace=True)
        elif method == "median":
            df[column].fillna(df[column].median(), inplace=True)
        elif method == "mode":
            df[column].fillna(df[column].mode()[0], inplace=True)
        elif method == "knn":
            imputer = KNNImputer(n_neighbors=5)
            df[[column]] = imputer.fit_transform(df[[column]])
        elif method == "forward":
            df[column].fillna(method='ffill', inplace=True)
        elif method == "backward":
            df[column].fillna(method='bfill', inplace=True)
        
        return df
    
    @staticmethod
    def _apply_math_transform(df: pd.DataFrame, column: str, method: str) -> pd.DataFrame:
        """Apply mathematical transformation"""
        if method == "log":
            df[f"{column}_log"] = np.log1p(df[column])
        elif method == "sqrt":
            df[f"{column}_sqrt"] = np.sqrt(np.abs(df[column]))
        elif method == "square":
            df[f"{column}_sq"] = df[column] ** 2
        elif method == "reciprocal":
            df[f"{column}_recip"] = 1 / (df[column] + 1e-10)
        
        return df
    
    @staticmethod
    def _handle_outliers(df: pd.DataFrame, column: str, method: str) -> pd.DataFrame:
        """Handle outliers"""
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 3 * IQR
        upper = Q3 + 3 * IQR
        
        if method == "cap":
            df[column] = df[column].clip(lower, upper)
        elif method == "remove":
            df = df[(df[column] >= lower) & (df[column] <= upper)]
        
        return df
    
    @staticmethod
    def _encode_categorical(df: pd.DataFrame, column: str, method: str) -> pd.DataFrame:
        """Encode categorical variables"""
        if method == "binary":
            df[column] = (df[column] == df[column].unique()[0]).astype(int)
        elif method == "label":
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column].astype(str))
        elif method == "onehot":
            dummies = pd.get_dummies(df[column], prefix=column)
            df = pd.concat([df, dummies], axis=1)
            df.drop(columns=[column], inplace=True)
        
        return df
    
    @staticmethod
    def _scale_features(df: pd.DataFrame, column: str, method: str) -> pd.DataFrame:
        """Scale features"""
        if method == "standard":
            scaler = StandardScaler()
            df[f"{column}_scaled"] = scaler.fit_transform(df[[column]])
        elif method == "minmax":
            scaler = MinMaxScaler()
            df[f"{column}_scaled"] = scaler.fit_transform(df[[column]])
        
        return df
    
    @staticmethod
    def auto_clean(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Automatically clean data with best practices"""
        operations = []
        df_clean = df.copy()
        
        # Remove duplicates
        before = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        if len(df_clean) < before:
            operations.append(f"Removed {before - len(df_clean)} duplicate rows")
        
        # Handle missing values
        for col in df_clean.columns:
            missing_pct = (df_clean[col].isnull().sum() / len(df_clean)) * 100
            if missing_pct > 50:
                df_clean = df_clean.drop(columns=[col])
                operations.append(f"Dropped {col} (>{missing_pct:.0f}% missing)")
            elif missing_pct > 0:
                if df_clean[col].dtype in [np.float64, np.int64]:
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                    operations.append(f"Imputed {col} with median")
                else:
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
                    operations.append(f"Imputed {col} with mode")
        
        # Convert data types
        for col in df_clean.select_dtypes(include=['object']).columns:
            if df_clean[col].nunique() / len(df_clean) < 0.05:
                df_clean[col] = df_clean[col].astype('category')
                operations.append(f"Converted {col} to category")
        
        return df_clean, operations
