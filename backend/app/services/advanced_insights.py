"""
Advanced Insights Generator - Automated Data Analysis
Automatically generates insights, patterns, and recommendations from data
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)


class AdvancedInsights:
    """Generate automated insights from data"""
    
    @staticmethod
    def generate_insights(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive insights"""
        insights = {
            "summary": AdvancedInsights._generate_summary(df),
            "patterns": AdvancedInsights._detect_patterns(df),
            "anomalies": AdvancedInsights._detect_anomalies(df),
            "correlations": AdvancedInsights._analyze_correlations(df),
            "recommendations": AdvancedInsights._generate_recommendations(df),
            "key_findings": []
        }
        
        insights["key_findings"] = AdvancedInsights._extract_key_findings(insights)
        return insights
    
    @staticmethod
    def _generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data summary"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2
        }
    
    @staticmethod
    def _detect_patterns(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect patterns in data"""
        patterns = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) < 10:
                continue
            
            # Trend detection
            if len(data) > 2:
                x = np.arange(len(data))
                slope, _, r_value, _, _ = stats.linregress(x, data)
                if abs(r_value) > 0.7:
                    trend = "increasing" if slope > 0 else "decreasing"
                    patterns.append({
                        "type": "trend",
                        "column": col,
                        "description": f"{col} shows {trend} trend (R²={r_value**2:.3f})",
                        "strength": abs(r_value)
                    })
            
            # Seasonality detection (simple)
            if len(data) > 20:
                autocorr = pd.Series(data.values).autocorr(lag=7)
                if abs(autocorr) > 0.6:
                    patterns.append({
                        "type": "seasonality",
                        "column": col,
                        "description": f"{col} shows potential weekly pattern",
                        "strength": abs(autocorr)
                    })
        
        return patterns
    
    @staticmethod
    def _detect_anomalies(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using IQR method"""
        anomalies = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) < 10:
                continue
            
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            if len(outliers) > 0:
                anomalies.append({
                    "column": col,
                    "count": len(outliers),
                    "percentage": (len(outliers) / len(data) * 100),
                    "description": f"Found {len(outliers)} outliers in {col}",
                    "range": f"[{lower_bound:.2f}, {upper_bound:.2f}]"
                })
        
        return anomalies
    
    @staticmethod
    def _analyze_correlations(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze correlations between numeric columns"""
        correlations = []
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return correlations
        
        corr_matrix = numeric_df.corr()
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    correlations.append({
                        "column1": col1,
                        "column2": col2,
                        "correlation": corr_value,
                        "strength": "strong" if abs(corr_value) > 0.9 else "moderate",
                        "description": f"{col1} and {col2} are {'positively' if corr_value > 0 else 'negatively'} correlated ({corr_value:.3f})"
                    })
        
        return correlations
    
    @staticmethod
    def _generate_recommendations(df: pd.DataFrame) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Missing data recommendations
        missing_pct = (df.isnull().sum() / len(df) * 100)
        high_missing = missing_pct[missing_pct > 30]
        if len(high_missing) > 0:
            recommendations.append(f"Consider removing or imputing {len(high_missing)} columns with >30% missing data")
        
        # Data type recommendations
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.05:
                recommendations.append(f"Convert '{col}' to categorical type for better performance")
        
        # Skewness recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            skewness = df[col].skew()
            if abs(skewness) > 2:
                recommendations.append(f"Apply log transformation to '{col}' (highly skewed: {skewness:.2f})")
        
        # Duplicate recommendations
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            recommendations.append(f"Remove {duplicates} duplicate rows")
        
        return recommendations
    
    @staticmethod
    def _extract_key_findings(insights: Dict[str, Any]) -> List[str]:
        """Extract key findings from insights"""
        findings = []
        
        # Summary findings
        summary = insights["summary"]
        findings.append(f"Dataset contains {summary['total_rows']:,} rows and {summary['total_columns']} columns")
        
        if summary["missing_percentage"] > 10:
            findings.append(f"⚠️ {summary['missing_percentage']:.1f}% of data is missing")
        
        # Pattern findings
        strong_patterns = [p for p in insights["patterns"] if p.get("strength", 0) > 0.8]
        if strong_patterns:
            findings.append(f"Found {len(strong_patterns)} strong patterns in the data")
        
        # Anomaly findings
        if insights["anomalies"]:
            total_anomalies = sum(a["count"] for a in insights["anomalies"])
            findings.append(f"Detected {total_anomalies} anomalies across {len(insights['anomalies'])} columns")
        
        # Correlation findings
        strong_corr = [c for c in insights["correlations"] if c["strength"] == "strong"]
        if strong_corr:
            findings.append(f"Found {len(strong_corr)} strong correlations between variables")
        
        return findings
