"""
Unified Statistical Analysis Interface

This module provides a single, easy-to-use interface for all statistical analysis capabilities.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import asdict

# Import all analysis components
from .statistical_analyzer_core import StatisticalAnalyzer, OutlierDetector
from .statistical_analyzer_advanced import (
    CorrelationAnalyzer, RegressionAnalyzer, TimeSeriesAnalyzer
)
from .statistical_analyzer_reports import (
    ResultInterpreter, VisualizationSuggester, ReportGenerator
)


class SpartaStatistics:
    """
    Unified interface for all statistical analysis capabilities in Sparta AI.
    
    This class provides a single entry point for:
    - Descriptive statistics
    - Hypothesis testing (parametric and non-parametric)
    - Correlation and regression analysis
    - Time series analysis and forecasting
    - Automatic test selection and assumption checking
    - Plain English interpretations and comprehensive reports
    
    Example:
        >>> stats = SpartaStatistics()
        >>> 
        >>> # Descriptive analysis
        >>> result = stats.describe(data, variable_name="Temperature")
        >>> 
        >>> # Compare groups automatically
        >>> result = stats.compare_groups(group1, group2, group3)
        >>> 
        >>> # Get comprehensive report
        >>> report = stats.generate_report(result)
    """
    
    def __init__(self, alpha: float = 0.05, confidence_level: float = 0.95,
                 auto_select_tests: bool = True):
        """
        Initialize the Sparta Statistics engine.
        
        Args:
            alpha: Significance level for hypothesis tests (default: 0.05)
            confidence_level: Confidence level for intervals (default: 0.95)
            auto_select_tests: Whether to automatically select appropriate tests (default: True)
        """
        self.alpha = alpha
        self.confidence_level = confidence_level
        self.auto_select_tests = auto_select_tests
        
        # Initialize all components
        self.analyzer = StatisticalAnalyzer(alpha, confidence_level)
        self.correlation = CorrelationAnalyzer(alpha)
        self.regression = RegressionAnalyzer(alpha)
        self.time_series = TimeSeriesAnalyzer()
        self.outlier_detector = OutlierDetector()
        self.report_generator = ReportGenerator()
        self.viz_suggester = VisualizationSuggester()
        self.interpreter = ResultInterpreter()
    
    # ==================== Descriptive Statistics ====================
    
    def describe(self, data: Union[pd.Series, np.ndarray, List],
                variable_name: str = "variable") -> Dict[str, Any]:
        """
        Compute comprehensive descriptive statistics.
        
        Args:
            data: Data to analyze
            variable_name: Name of the variable
            
        Returns:
            Dictionary with descriptive statistics
        """
        if isinstance(data, list):
            data = np.array(data)
        
        stats = self.analyzer.describe(data, variable_name)
        return stats.to_dict()
    
    def detect_outliers(self, data: Union[np.ndarray, List],
                       method: str = "iqr",
                       **kwargs) -> Dict[str, Any]:
        """
        Detect outliers using various methods.
        
        Args:
            data: Data to analyze
            method: "iqr", "zscore", "modified_zscore", or "isolation_forest"
            **kwargs: Additional parameters for the method
            
        Returns:
            Dictionary with outlier information
        """
        if isinstance(data, list):
            data = np.array(data)
        
        if method == "iqr":
            multiplier = kwargs.get("multiplier", 1.5)
            indices, mask = self.outlier_detector.iqr_method(data, multiplier)
        elif method == "zscore":
            threshold = kwargs.get("threshold", 3.0)
            indices, mask = self.outlier_detector.zscore_method(data, threshold)
        elif method == "modified_zscore":
            threshold = kwargs.get("threshold", 3.5)
            indices, mask = self.outlier_detector.modified_zscore_method(data, threshold)
        elif method == "isolation_forest":
            contamination = kwargs.get("contamination", 0.1)
            indices, mask = self.outlier_detector.isolation_forest_method(data, contamination)
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
        
        return {
            "method": method,
            "n_outliers": len(indices),
            "outlier_indices": indices,
            "outlier_percentage": len(indices) / len(data) * 100,
            "outlier_values": data[indices].tolist() if len(indices) > 0 else []
        }
    
    # ==================== Group Comparisons ====================
    
    def compare_groups(self, *groups: Union[np.ndarray, List],
                      test_type: str = "auto",
                      paired: bool = False,
                      post_hoc: bool = True) -> Dict[str, Any]:
        """
        Compare multiple groups using appropriate statistical tests.
        
        Args:
            groups: Variable number of group data arrays
            test_type: "auto", "ttest", "anova", "mannwhitney", "kruskal", etc.
            paired: Whether groups are paired/dependent
            post_hoc: Whether to perform post-hoc tests for ANOVA
            
        Returns:
            Dictionary with test results and interpretation
        """
        # Convert to numpy arrays
        groups_array: List[np.ndarray] = [np.asarray(g) for g in groups]
        
        if self.auto_select_tests and test_type == "auto":
            # Automatically select appropriate test
            test_enum, metadata = self.analyzer.test_selector.select_comparison_test(
                groups_array, paired=paired, check_assumptions=True
            )
            test_type = test_enum.value
        
        # Perform appropriate test
        if len(groups_array) == 2:
            if test_type in ["auto", "independent_t_test", "t_test_independent", "ttest"]:
                result = self.analyzer.t_test_independent(groups_array[0], groups_array[1])
            elif test_type in ["paired_t_test", "t_test_paired"]:
                result = self.analyzer.t_test_paired(groups_array[0], groups_array[1])
            elif test_type == "mann_whitney":
                result = self.analyzer.mann_whitney_u(groups_array[0], groups_array[1])
            else:
                raise ValueError(f"Unknown test type for 2 groups: {test_type}")
        else:
            if test_type in ["auto", "anova"]:
                result = self.analyzer.anova(*groups_array, post_hoc=post_hoc)
            elif test_type == "kruskal_wallis":
                result = self.analyzer.kruskal_wallis(*groups_array)
            else:
                raise ValueError(f"Unknown test type for {len(groups_array)} groups: {test_type}")
        
        # Convert to dictionary and add visualizations
        result_dict = {
            "test_name": result.test_name,
            "test_type": result.test_type,
            "statistic": result.statistic,
            "p_value": result.p_value,
            "is_significant": result.is_significant,
            "significance_level": result.significance_level,
            "interpretation": result.interpretation,
            "effect_size": result.effect_size,
            "effect_size_name": result.effect_size_name,
            "effect_size_interpretation": result.effect_size_interpretation,
            "confidence_interval": result.confidence_interval,
            "power": result.power,
            "sample_size": result.sample_size,
            "assumptions_met": result.assumptions_met,
            "recommendation": result.recommendation,
            "alternative_tests": result.alternative_tests,
            "suggested_visualizations": result.suggested_visualizations,
            "metadata": result.metadata,
            # Extract post_hoc_results from metadata for convenience
            "post_hoc_results": result.metadata.get("post_hoc_tests") if result.metadata else None
        }
        
        return result_dict
    
    # ==================== Correlation Analysis ====================
    
    def correlate(self, x: Union[np.ndarray, List], y: Union[np.ndarray, List],
                 method: str = "auto",
                 var1_name: str = "Variable 1",
                 var2_name: str = "Variable 2") -> Dict[str, Any]:
        """
        Compute correlation between two variables.
        
        Args:
            x: First variable
            y: Second variable
            method: "auto", "pearson", "spearman", or "kendall"
            var1_name: Name of first variable
            var2_name: Name of second variable
            
        Returns:
            Dictionary with correlation results
        """
        if isinstance(x, list):
            x = np.array(x)
        if isinstance(y, list):
            y = np.array(y)
        
        result = self.correlation.correlate(x, y, method, var1_name, var2_name)
        return result.to_dict()
    
    def correlation_matrix(self, data: pd.DataFrame,
                          method: str = "pearson") -> Dict[str, Any]:
        """
        Compute correlation matrix for all numeric variables.
        
        Args:
            data: DataFrame with variables
            method: "pearson", "spearman", or "kendall"
            
        Returns:
            Dictionary with correlation and p-value matrices
        """
        corr_matrix, p_matrix = self.correlation.correlation_matrix(data, method)
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "p_value_matrix": p_matrix.to_dict(),
            "method": method,
            "variables": corr_matrix.columns.tolist()
        }
    
    # ==================== Regression Analysis ====================
    
    def linear_regression(self, X: Union[np.ndarray, pd.DataFrame, List],
                         y: Union[np.ndarray, List],
                         feature_names: Optional[List[str]] = None,
                         check_assumptions: bool = True) -> Dict[str, Any]:
        """
        Perform linear regression analysis.
        
        Args:
            X: Independent variable(s)
            y: Dependent variable
            feature_names: Names of features
            check_assumptions: Whether to check regression assumptions
            
        Returns:
            Dictionary with regression results
        """
        if isinstance(X, list):
            X = np.array(X)
        if isinstance(y, list):
            y = np.array(y)
        
        result = self.regression.linear_regression(X, y, feature_names, check_assumptions)
        return result.to_dict()
    
    def polynomial_regression(self, X: Union[np.ndarray, List],
                            y: Union[np.ndarray, List],
                            degree: int = 2,
                            feature_name: str = "X") -> Dict[str, Any]:
        """
        Perform polynomial regression analysis.
        
        Args:
            X: Independent variable
            y: Dependent variable
            degree: Polynomial degree
            feature_name: Name of feature
            
        Returns:
            Dictionary with regression results
        """
        if isinstance(X, list):
            X = np.array(X)
        if isinstance(y, list):
            y = np.array(y)
        
        result = self.regression.polynomial_regression(X, y, degree, feature_name)
        return result.to_dict()
    
    def logistic_regression(self, X: Union[np.ndarray, pd.DataFrame, List],
                           y: Union[np.ndarray, List],
                           feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform logistic regression for binary classification.
        
        Args:
            X: Independent variable(s)
            y: Binary dependent variable (0/1)
            feature_names: Names of features
            
        Returns:
            Dictionary with regression results
        """
        if isinstance(X, list):
            X = np.array(X)
        if isinstance(y, list):
            y = np.array(y)
        
        result = self.regression.logistic_regression(X, y, feature_names)
        # Remove non-serializable arrays
        result.pop('predictions', None)
        result.pop('predicted_probabilities', None)
        return result
    
    # ==================== Time Series Analysis ====================
    
    def decompose_time_series(self, data: Union[pd.Series, np.ndarray, List],
                             period: int,
                             model: str = "additive") -> Dict[str, Any]:
        """
        Decompose time series into components.
        
        Args:
            data: Time series data
            period: Seasonal period
            model: "additive" or "multiplicative"
            
        Returns:
            Dictionary with decomposition results
        """
        if isinstance(data, list):
            data = np.array(data)
        
        result = self.time_series.decompose(data, period, model)
        result_dict = result.to_dict()
        
        # Add component arrays (limited)
        result_dict["trend_sample"] = result.trend[:10].tolist() if result.trend is not None else None
        result_dict["seasonal_sample"] = result.seasonal[:10].tolist() if result.seasonal is not None else None
        
        return result_dict
    
    def test_stationarity(self, data: Union[pd.Series, np.ndarray, List]) -> Dict[str, Any]:
        """
        Test if time series is stationary.
        
        Args:
            data: Time series data
            
        Returns:
            Dictionary with stationarity test results
        """
        if isinstance(data, list):
            data = np.array(data)
        
        result = self.time_series.test_stationarity(data, self.alpha)
        return result.to_dict()
    
    def forecast(self, data: Union[pd.Series, np.ndarray, List],
                steps: int = 10,
                order: Tuple[int, int, int] = (1, 1, 1)) -> Dict[str, Any]:
        """
        Forecast future values using ARIMA.
        
        Args:
            data: Historical time series data
            steps: Number of steps to forecast
            order: ARIMA order (p, d, q)
            
        Returns:
            Dictionary with forecast results
        """
        if isinstance(data, list):
            data = np.array(data)
        
        result = self.time_series.forecast_arima(data, order, steps)
        result_dict = result.to_dict()
        
        # Add forecast arrays
        result_dict["forecast"] = result.forecast.tolist() if result.forecast is not None else None
        result_dict["forecast_ci_lower"] = result.forecast_ci_lower.tolist() if result.forecast_ci_lower is not None else None
        result_dict["forecast_ci_upper"] = result.forecast_ci_upper.tolist() if result.forecast_ci_upper is not None else None
        
        return result_dict
    
    # ==================== Report Generation ====================
    
    def generate_report(self, result: Any, report_type: str = "auto") -> str:
        """
        Generate comprehensive markdown report.
        
        Args:
            result: Statistical analysis result object
            report_type: "auto", "descriptive", "test", "correlation", "regression"
            
        Returns:
            Markdown-formatted report
        """
        # Auto-detect report type
        if report_type == "auto":
            if hasattr(result, 'test_name'):
                report_type = "test"
            elif hasattr(result, 'correlation_coefficient'):
                report_type = "correlation"
            elif hasattr(result, 'r_squared'):
                report_type = "regression"
            elif hasattr(result, 'mean'):
                report_type = "descriptive"
        
        # Generate appropriate report
        if report_type == "descriptive":
            return self.report_generator.generate_descriptive_report(result)
        elif report_type == "test":
            return self.report_generator.generate_test_report(result)
        elif report_type == "correlation":
            return self.report_generator.generate_correlation_report(result)
        elif report_type == "regression":
            return self.report_generator.generate_regression_report(result)
        else:
            return f"Unknown report type: {report_type}"
    
    def suggest_visualizations(self, analysis_type: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Get visualization suggestions for analysis type.
        
        Args:
            analysis_type: "descriptive", "comparison", "correlation", "regression", "timeseries"
            **kwargs: Additional parameters specific to analysis type
            
        Returns:
            List of visualization suggestions
        """
        if analysis_type == "descriptive":
            data_type = kwargs.get("data_type", "continuous")
            return self.viz_suggester.suggest_for_descriptive(data_type)
        elif analysis_type == "comparison":
            n_groups = kwargs.get("n_groups", 2)
            test_type = kwargs.get("test_type", "ttest")
            return self.viz_suggester.suggest_for_comparison(test_type, n_groups)
        elif analysis_type == "correlation":
            n_variables = kwargs.get("n_variables", 2)
            return self.viz_suggester.suggest_for_correlation(n_variables)
        elif analysis_type == "regression":
            n_predictors = kwargs.get("n_predictors", 1)
            return self.viz_suggester.suggest_for_regression(n_predictors)
        elif analysis_type == "timeseries":
            ts_type = kwargs.get("ts_type", "decomposition")
            return self.viz_suggester.suggest_for_time_series(ts_type)
        else:
            return []
    
    # ==================== API Wrapper Methods ====================
    
    def analyze_descriptive(self, data: Union[np.ndarray, List, pd.Series],
                           variable_name: str = "variable") -> Dict[str, Any]:
        """Wrapper for API compatibility - calls describe()"""
        # Convert pandas Series to list for compatibility
        if isinstance(data, pd.Series):
            data = data.tolist()
        return self.describe(data, variable_name)
    
    def analyze_correlation(self, x: Union[np.ndarray, List],
                           y: Union[np.ndarray, List],
                           method: Optional[str] = None,
                           var1_name: str = "Variable 1",
                           var2_name: str = "Variable 2",
                           alpha: Optional[float] = None) -> Dict[str, Any]:
        """Wrapper for API compatibility - analyzes correlation between two variables"""
        if isinstance(x, list):
            x = np.array(x)
        if isinstance(y, list):
            y = np.array(y)
        
        use_alpha = alpha if alpha is not None else self.alpha
        use_method = method if method else "auto"
        
        result = self.correlation.correlate(
            x, y, method=use_method,
            var1_name=var1_name, var2_name=var2_name
        )
        return asdict(result)
    
    def analyze_regression(self, X: Union[np.ndarray, pd.DataFrame, List],
                          y: Union[np.ndarray, List],
                          regression_type: str = "linear",
                          degree: Optional[int] = None,
                          feature_names: Optional[List[str]] = None,
                          check_assumptions: bool = True,
                          alpha: Optional[float] = None) -> Dict[str, Any]:
        """Wrapper for API compatibility - performs regression analysis"""
        if isinstance(X, list):
            X = np.array(X).reshape(-1, 1)
        if isinstance(y, list):
            y = np.array(y)
        
        if regression_type == "linear":
            result = self.regression.linear_regression(X, y, feature_names, check_assumptions)
        elif regression_type == "polynomial":
            if degree is None:
                degree = 2
            # Convert to 1D array for polynomial regression
            x_poly = X.values.ravel() if isinstance(X, pd.DataFrame) else X.ravel() if len(X.shape) > 1 else X
            result = self.regression.polynomial_regression(x_poly, y, degree)
        elif regression_type == "logistic":
            # Logistic regression returns a dict directly
            return self.regression.logistic_regression(X, y, feature_names)
        else:
            raise ValueError(f"Unknown regression type: {regression_type}")
        
        # Check if result is already a dict (some regression methods return dicts)
        if isinstance(result, dict):
            return result
        return result.to_dict()
    
    def analyze_time_series(self, data: Union[np.ndarray, List, pd.Series],
                           analysis_type: str = "decomposition",
                           period: Optional[int] = None,
                           model_type: str = "additive",
                           forecast_steps: int = 10,
                           arima_order: Optional[Tuple[int, int, int]] = None,
                           alpha: Optional[float] = None) -> Dict[str, Any]:
        """Wrapper for API compatibility - performs time series analysis"""
        # Convert to numpy array
        if isinstance(data, list):
            data_array: np.ndarray = np.array(data)
        elif isinstance(data, pd.Series):
            data_array = np.array(data.values)
        else:
            data_array = data
        
        if analysis_type == "stationarity":
            result = self.time_series.test_stationarity(data_array, alpha or self.alpha)
        elif analysis_type == "decomposition":
            if period is None:
                raise ValueError("Period required for decomposition")
            result = self.time_series.decompose(data_array, period, model_type)
        elif analysis_type == "forecast":
            # Ensure we have a valid tuple for arima_order
            if arima_order is None:
                arima_tuple: Tuple[int, int, int] = (1, 1, 1)
            elif isinstance(arima_order, list) and len(arima_order) == 3:
                arima_tuple = (int(arima_order[0]), int(arima_order[1]), int(arima_order[2]))
            else:
                arima_tuple = arima_order
            result = self.time_series.forecast_arima(data_array, arima_tuple, forecast_steps)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # Check if result is already a dict
        if isinstance(result, dict):
            return result
        return result.to_dict()
    
    # ==================== Utility Methods ====================
    
    def interpret_p_value(self, p_value: float) -> str:
        """Get plain English interpretation of p-value."""
        return self.interpreter.interpret_p_value(p_value, self.alpha)
    
    def interpret_effect_size(self, effect_size: float, effect_name: str,
                            interpretation: str) -> str:
        """Get plain English interpretation of effect size."""
        return self.interpreter.interpret_effect_size(effect_size, effect_name, interpretation)
    
    def calculate_power(self, n_per_group: int, effect_size: float,
                       test_type: str = "ttest") -> float:
        """
        Calculate statistical power.
        
        Args:
            n_per_group: Sample size per group
            effect_size: Expected effect size
            test_type: "ttest" or "anova"
            
        Returns:
            Statistical power (0-1)
        """
        if test_type == "ttest":
            return self.analyzer.power_analyzer.calculate_power_ttest(
                n_per_group, effect_size, self.alpha
            )
        else:
            raise NotImplementedError(f"Power calculation for {test_type} not yet implemented")
    
    def required_sample_size(self, effect_size: float, power: float = 0.8,
                           test_type: str = "ttest") -> int:
        """
        Calculate required sample size.
        
        Args:
            effect_size: Expected effect size
            power: Desired statistical power
            test_type: "ttest" or "anova"
            
        Returns:
            Required sample size per group
        """
        if test_type == "ttest":
            return self.analyzer.power_analyzer.calculate_required_sample_size_ttest(
                effect_size, power, self.alpha
            )
        else:
            raise NotImplementedError(f"Sample size calculation for {test_type} not yet implemented")


# Create a singleton instance for easy access
stats_engine = SpartaStatistics()

# Alias for API compatibility
StatisticsEngine = SpartaStatistics

# Export main interface
__all__ = [
    'SpartaStatistics',
    'StatisticsEngine',
    'stats_engine',
]
