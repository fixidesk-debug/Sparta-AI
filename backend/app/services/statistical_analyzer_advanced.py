"""
Advanced Statistical Analysis - Correlation, Regression, and Time Series

Provides advanced analysis methods for Sparta AI.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, accuracy_score, precision_recall_fscore_support
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.outliers_influence import variance_inflation_factor

from .statistical_analyzer import (
    AssumptionCheckResult, AssumptionChecker, EffectSizeCalculator
)


@dataclass
class CorrelationResult:
    """Results from correlation analysis."""
    variable1: str
    variable2: str
    correlation_coefficient: float
    p_value: float
    method: str  # pearson, spearman, kendall
    n: int
    confidence_interval: Optional[Tuple[float, float]] = None
    is_significant: bool = False
    significance_level: float = 0.05
    interpretation: str = ""
    strength: str = ""  # weak, moderate, strong
    direction: str = ""  # positive, negative, none
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "variable1": self.variable1,
            "variable2": self.variable2,
            "correlation": self.correlation_coefficient,
            "p_value": self.p_value,
            "method": self.method,
            "n": self.n,
            "confidence_interval": self.confidence_interval,
            "is_significant": self.is_significant,
            "interpretation": self.interpretation,
            "strength": self.strength,
            "direction": self.direction
        }


@dataclass
class RegressionResult:
    """Results from regression analysis."""
    model_type: str
    coefficients: Dict[str, float]
    intercept: float
    r_squared: float
    adjusted_r_squared: float
    rmse: float
    mae: float
    n: int
    n_features: int
    
    # Statistical tests
    coefficient_p_values: Optional[Dict[str, float]] = None
    coefficient_ci: Optional[Dict[str, Tuple[float, float]]] = None
    
    # Diagnostics
    residuals: Optional[np.ndarray] = None
    assumptions_met: bool = True
    assumption_checks: List[AssumptionCheckResult] = field(default_factory=list)
    vif_values: Optional[Dict[str, float]] = None  # Variance Inflation Factor
    
    # Interpretation
    interpretation: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # Predictions
    predictions: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding large arrays)."""
        return {
            "model_type": self.model_type,
            "coefficients": self.coefficients,
            "intercept": self.intercept,
            "r_squared": self.r_squared,
            "adjusted_r_squared": self.adjusted_r_squared,
            "rmse": self.rmse,
            "mae": self.mae,
            "n": self.n,
            "n_features": self.n_features,
            "coefficient_p_values": self.coefficient_p_values,
            "coefficient_ci": self.coefficient_ci,
            "assumptions_met": self.assumptions_met,
            "vif_values": self.vif_values,
            "interpretation": self.interpretation,
            "recommendations": self.recommendations
        }


@dataclass
class TimeSeriesResult:
    """Results from time series analysis."""
    analysis_type: str  # decomposition, stationarity, forecasting
    
    # Decomposition components
    trend: Optional[np.ndarray] = None
    seasonal: Optional[np.ndarray] = None
    residual: Optional[np.ndarray] = None
    
    # Stationarity test
    is_stationary: Optional[bool] = None
    adf_statistic: Optional[float] = None
    adf_pvalue: Optional[float] = None
    
    # Forecasting
    forecast: Optional[np.ndarray] = None
    forecast_ci_lower: Optional[np.ndarray] = None
    forecast_ci_upper: Optional[np.ndarray] = None
    forecast_steps: int = 0
    
    # Model info
    model_type: Optional[str] = None
    model_params: Optional[Dict[str, Any]] = None
    
    # Interpretation
    interpretation: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding large arrays)."""
        result = {
            "analysis_type": self.analysis_type,
            "is_stationary": self.is_stationary,
            "adf_statistic": self.adf_statistic,
            "adf_pvalue": self.adf_pvalue,
            "forecast_steps": self.forecast_steps,
            "model_type": self.model_type,
            "model_params": self.model_params,
            "interpretation": self.interpretation,
            "recommendations": self.recommendations
        }
        
        # Include array lengths instead of full arrays
        if self.trend is not None:
            result["trend_length"] = len(self.trend)
        if self.forecast is not None:
            result["forecast_length"] = len(self.forecast)
        
        return result


class CorrelationAnalyzer:
    """
    Performs various correlation analyses.
    """
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.assumption_checker = AssumptionChecker()
    
    def correlate(self, x: np.ndarray, y: np.ndarray,
                 method: str = "auto",
                 var1_name: str = "Variable 1",
                 var2_name: str = "Variable 2") -> CorrelationResult:
        """
        Compute correlation between two variables.
        
        Args:
            x: First variable
            y: Second variable
            method: "auto", "pearson", "spearman", or "kendall"
            var1_name: Name of first variable
            var2_name: Name of second variable
            
        Returns:
            CorrelationResult with comprehensive results
        """
        # Clean data
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean = x[mask]
        y_clean = y[mask]
        n = len(x_clean)
        
        if n < 3:
            return CorrelationResult(
                variable1=var1_name,
                variable2=var2_name,
                correlation_coefficient=np.nan,
                p_value=np.nan,
                method=method,
                n=n,
                interpretation="Insufficient data for correlation analysis (n < 3)"
            )
        
        # Auto-select method based on normality
        if method == "auto":
            norm_x = self.assumption_checker.check_normality(x_clean)
            norm_y = self.assumption_checker.check_normality(y_clean)
            
            if norm_x.passed and norm_y.passed:
                method = "pearson"
            else:
                method = "spearman"
        
        # Compute correlation
        if method == "pearson":
            corr_result = pearsonr(x_clean, y_clean)
            # Extract values - scipy returns tuple-like objects
            corr = float(corr_result[0])  # type: ignore
            p_value = float(corr_result[1])  # type: ignore
            # Fisher z-transformation for CI
            z = np.arctanh(corr)
            se = 1 / np.sqrt(n - 3)
            z_crit = stats.norm.ppf(1 - self.alpha/2)
            ci_lower = float(np.tanh(z - z_crit * se))
            ci_upper = float(np.tanh(z + z_crit * se))
            ci = (ci_lower, ci_upper)
        elif method == "spearman":
            corr_result = spearmanr(x_clean, y_clean)
            corr = float(corr_result[0])  # type: ignore
            p_value = float(corr_result[1])  # type: ignore
            ci = None  # CI calculation for Spearman is complex
        elif method == "kendall":
            corr_result = kendalltau(x_clean, y_clean)
            corr = float(corr_result[0])  # type: ignore
            p_value = float(corr_result[1])  # type: ignore
            ci = None
        else:
            raise ValueError(f"Unknown correlation method: {method}")
        
        # Interpret strength
        abs_corr = abs(corr)
        if abs_corr < 0.1:
            strength = "negligible"
        elif abs_corr < 0.3:
            strength = "weak"
        elif abs_corr < 0.5:
            strength = "moderate"
        elif abs_corr < 0.7:
            strength = "strong"
        else:
            strength = "very strong"
        
        # Interpret direction
        if corr > 0.05:
            direction = "positive"
        elif corr < -0.05:
            direction = "negative"
        else:
            direction = "none"
        
        is_significant = p_value < self.alpha
        
        interpretation = (
            f"{'Significant' if is_significant else 'No significant'} "
            f"{strength} {direction} {method.title()} correlation "
            f"(r={corr:.4f}, p={p_value:.4f}, n={n})"
        )
        
        if ci:
            interpretation += f" with 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]"
        
        return CorrelationResult(
            variable1=var1_name,
            variable2=var2_name,
            correlation_coefficient=corr,
            p_value=p_value,
            method=method,
            n=n,
            confidence_interval=ci,
            is_significant=is_significant,
            significance_level=self.alpha,
            interpretation=interpretation,
            strength=strength,
            direction=direction
        )
    
    def correlation_matrix(self, data: pd.DataFrame,
                          method: str = "pearson") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compute correlation matrix with p-values.
        
        Args:
            data: DataFrame with numerical variables
            method: "pearson", "spearman", or "kendall"
            
        Returns:
            Tuple of (correlation matrix, p-value matrix)
        """
        cols = data.select_dtypes(include=[np.number]).columns
        n_cols = len(cols)
        
        corr_matrix = np.zeros((n_cols, n_cols))
        p_matrix = np.zeros((n_cols, n_cols))
        
        for i, col1 in enumerate(cols):
            for j, col2 in enumerate(cols):
                if i == j:
                    corr_matrix[i, j] = 1.0
                    p_matrix[i, j] = 0.0
                elif i < j:
                    result = self.correlate(
                        np.asarray(data[col1].values),
                        np.asarray(data[col2].values),
                        method=method
                    )
                    corr_matrix[i, j] = result.correlation_coefficient
                    corr_matrix[j, i] = result.correlation_coefficient
                    p_matrix[i, j] = result.p_value
                    p_matrix[j, i] = result.p_value
        
        return (
            pd.DataFrame(corr_matrix, index=cols, columns=cols),
            pd.DataFrame(p_matrix, index=cols, columns=cols)
        )


class RegressionAnalyzer:
    """
    Performs various regression analyses.
    """
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.assumption_checker = AssumptionChecker()
    
    def linear_regression(self, X: Union[np.ndarray, pd.DataFrame],
                         y: np.ndarray,
                         feature_names: Optional[List[str]] = None,
                         check_assumptions: bool = True) -> RegressionResult:
        """
        Perform linear regression analysis.
        
        Args:
            X: Independent variable(s)
            y: Dependent variable
            feature_names: Names of features
            check_assumptions: Whether to check regression assumptions
            
        Returns:
            RegressionResult with comprehensive results
        """
        # Handle input
        if isinstance(X, pd.DataFrame):
            feature_names = X.columns.tolist()
            X = X.values
        elif X.ndim == 1:
            X = X.reshape(-1, 1)
            if feature_names is None:
                feature_names = ["X"]
        elif feature_names is None:
            feature_names = [f"X{i+1}" for i in range(X.shape[1])]
        
        # Clean data (remove rows with any NaN)
        mask = ~(np.isnan(y) | np.any(np.isnan(X), axis=1))
        X_clean = X[mask]
        y_clean = y[mask]
        
        n = len(y_clean)
        n_features = X_clean.shape[1]
        
        # Fit model
        model = LinearRegression()
        model.fit(X_clean, y_clean)
        
        # Predictions
        y_pred = model.predict(X_clean)
        residuals = y_clean - y_pred
        
        # Calculate metrics
        r_squared = r2_score(y_clean, y_pred)
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - n_features - 1)
        rmse = np.sqrt(mean_squared_error(y_clean, y_pred))
        mae = mean_absolute_error(y_clean, y_pred)
        
        # Create coefficient dictionary
        coefficients = {name: float(coef) for name, coef in zip(feature_names, model.coef_)}
        
        # Check assumptions
        assumption_checks = []
        assumptions_met = True
        
        if check_assumptions:
            # 1. Linearity (checked implicitly through residual plots)
            
            # 2. Independence of residuals
            independence = self.assumption_checker.check_independence(residuals)
            assumption_checks.append(independence)
            assumptions_met = assumptions_met and independence.passed
            
            # 3. Homoscedasticity
            homoscedasticity = self.assumption_checker.check_homoscedasticity(X_clean, residuals)
            assumption_checks.append(homoscedasticity)
            assumptions_met = assumptions_met and homoscedasticity.passed
            
            # 4. Normality of residuals
            normality = self.assumption_checker.check_normality(residuals)
            assumption_checks.append(normality)
            assumptions_met = assumptions_met and normality.passed
            
            # 5. Multicollinearity (VIF)
            vif_values = {}
            if n_features > 1:
                try:
                    for i, name in enumerate(feature_names):
                        vif = variance_inflation_factor(X_clean, i)
                        vif_values[name] = float(vif)
                        if vif > 10:  # Common threshold
                            assumptions_met = False
                except:
                    pass
        else:
            vif_values = None
        
        # Interpretation
        r_squared_interp = EffectSizeCalculator.r_squared_interpretation(r_squared)
        
        interpretation = (
            f"Linear regression model explains {r_squared*100:.1f}% of variance "
            f"(R²={r_squared:.4f}, Adjusted R²={adj_r_squared:.4f}). "
            f"Model fit is {r_squared_interp}. "
            f"RMSE={rmse:.4f}, MAE={mae:.4f}."
        )
        
        # Recommendations
        recommendations = []
        if not assumptions_met:
            recommendations.append("Some regression assumptions are violated. Review diagnostic plots.")
        if vif_values and any(vif > 10 for vif in vif_values.values()):
            high_vif_features = [name for name, vif in vif_values.items() if vif > 10]
            recommendations.append(
                f"High multicollinearity detected for {', '.join(high_vif_features)}. "
                "Consider removing correlated features or using regularization (Ridge/Lasso)."
            )
        if r_squared < 0.3:
            recommendations.append(
                "Low R² suggests weak model fit. Consider adding more features, "
                "transforming variables, or using non-linear models."
            )
        
        return RegressionResult(
            model_type="linear",
            coefficients=coefficients,
            intercept=float(model.intercept_),
            r_squared=r_squared,
            adjusted_r_squared=adj_r_squared,
            rmse=rmse,
            mae=mae,
            n=n,
            n_features=n_features,
            residuals=residuals,
            assumptions_met=assumptions_met,
            assumption_checks=assumption_checks,
            vif_values=vif_values,
            interpretation=interpretation,
            recommendations=recommendations,
            predictions=y_pred
        )
    
    def polynomial_regression(self, X: np.ndarray, y: np.ndarray,
                            degree: int = 2,
                            feature_name: str = "X") -> RegressionResult:
        """
        Perform polynomial regression.
        
        Args:
            X: Independent variable (1D)
            y: Dependent variable
            degree: Polynomial degree
            feature_name: Name of feature
            
        Returns:
            RegressionResult with comprehensive results
        """
        # Ensure X is 1D
        if X.ndim > 1:
            X = X.ravel()
        
        # Clean data
        mask = ~(np.isnan(X) | np.isnan(y))
        X_clean = X[mask].reshape(-1, 1)
        y_clean = y[mask]
        
        # Create polynomial features
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        X_poly = poly.fit_transform(X_clean)
        
        # Fit model
        model = LinearRegression()
        model.fit(X_poly, y_clean)
        
        # Predictions
        y_pred = model.predict(X_poly)
        residuals = y_clean - y_pred
        
        # Calculate metrics
        n = len(y_clean)
        n_features = X_poly.shape[1]
        r_squared = r2_score(y_clean, y_pred)
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - n_features - 1)
        rmse = np.sqrt(mean_squared_error(y_clean, y_pred))
        mae = mean_absolute_error(y_clean, y_pred)
        
        # Create coefficient dictionary
        feature_names = [f"{feature_name}^{i+1}" for i in range(degree)]
        coefficients = {name: float(coef) for name, coef in zip(feature_names, model.coef_)}
        
        # Interpretation
        interpretation = (
            f"Polynomial regression (degree {degree}) explains {r_squared*100:.1f}% of variance "
            f"(R²={r_squared:.4f}). RMSE={rmse:.4f}, MAE={mae:.4f}."
        )
        
        recommendations = []
        if degree > 3:
            recommendations.append(
                "High-degree polynomial may lead to overfitting. "
                "Consider cross-validation or regularization."
            )
        
        return RegressionResult(
            model_type="polynomial",
            coefficients=coefficients,
            intercept=float(model.intercept_),
            r_squared=r_squared,
            adjusted_r_squared=adj_r_squared,
            rmse=rmse,
            mae=mae,
            n=n,
            n_features=n_features,
            residuals=residuals,
            interpretation=interpretation,
            recommendations=recommendations,
            predictions=y_pred
        )
    
    def logistic_regression(self, X: Union[np.ndarray, pd.DataFrame],
                           y: np.ndarray,
                           feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform logistic regression for binary classification.
        
        Args:
            X: Independent variable(s)
            y: Binary dependent variable (0/1)
            feature_names: Names of features
            
        Returns:
            Dictionary with comprehensive results
        """
        # Handle input
        if isinstance(X, pd.DataFrame):
            feature_names = X.columns.tolist()
            X = X.values
        elif X.ndim == 1:
            X = X.reshape(-1, 1)
            if feature_names is None:
                feature_names = ["X"]
        elif feature_names is None:
            feature_names = [f"X{i+1}" for i in range(X.shape[1])]
        
        # Clean data
        mask = ~(np.isnan(y) | np.any(np.isnan(X), axis=1))
        X_clean = X[mask]
        y_clean = y[mask]
        
        # Fit model
        model = LogisticRegression(max_iter=1000)
        model.fit(X_clean, y_clean)
        
        # Predictions
        y_pred = model.predict(X_clean)
        y_pred_proba = model.predict_proba(X_clean)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_clean, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_clean, y_pred, average='binary'
        )
        
        # Create coefficient dictionary
        coefficients = {name: float(coef) for name, coef in zip(feature_names, model.coef_[0])}
        
        interpretation = (
            f"Logistic regression model achieved {accuracy*100:.1f}% accuracy. "
            f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1-score: {f1:.3f}."
        )
        
        return {
            "model_type": "Logistic Regression",
            "coefficients": coefficients,
            "intercept": float(model.intercept_[0]),
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "n": len(y_clean),
            "n_features": len(feature_names),
            "interpretation": interpretation,
            "predictions": y_pred,
            "predicted_probabilities": y_pred_proba
        }


class TimeSeriesAnalyzer:
    """
    Performs time series analysis and forecasting.
    """
    
    def __init__(self):
        pass
    
    def decompose(self, data: Union[pd.Series, np.ndarray],
                 period: int,
                 model: str = "additive") -> TimeSeriesResult:
        """
        Decompose time series into trend, seasonal, and residual components.
        
        Args:
            data: Time series data
            period: Seasonal period (e.g., 12 for monthly data with yearly seasonality)
            model: "additive" or "multiplicative"
            
        Returns:
            TimeSeriesResult with decomposition components
        """
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
        
        # Perform decomposition
        result = seasonal_decompose(data, model=model, period=period, extrapolate_trend=1)  # type: ignore
        
        interpretation = (
            f"{model.title()} decomposition completed. "
            f"Series decomposed into trend, seasonal (period={period}), and residual components."
        )
        
        recommendations = [
            "Review trend component to identify long-term patterns",
            "Analyze seasonal component for recurring patterns",
            "Check residual component for remaining structure (should be random)"
        ]
        
        return TimeSeriesResult(
            analysis_type="decomposition",
            trend=result.trend.values,
            seasonal=result.seasonal.values,
            residual=result.resid.values,
            model_type=model,
            interpretation=interpretation,
            recommendations=recommendations
        )
    
    def test_stationarity(self, data: Union[pd.Series, np.ndarray],
                         alpha: float = 0.05) -> TimeSeriesResult:
        """
        Test if time series is stationary using Augmented Dickey-Fuller test.
        
        Args:
            data: Time series data
            alpha: Significance level
            
        Returns:
            TimeSeriesResult with stationarity test results
        """
        if isinstance(data, pd.Series):
            data_array: np.ndarray = np.asarray(data.values)
        else:
            data_array = data
        
        # Remove NaN values
        data_clean = data_array[~np.isnan(data_array)]
        
        # Perform ADF test
        adf_result = adfuller(data_clean)
        adf_statistic = float(adf_result[0])
        adf_pvalue = float(adf_result[1])
        
        is_stationary = bool(adf_pvalue < alpha)
        
        interpretation = (
            f"Time series {'is' if is_stationary else 'is not'} stationary "
            f"(ADF statistic={adf_statistic:.4f}, p={adf_pvalue:.4f})."
        )
        
        recommendations = []
        if not is_stationary:
            recommendations.append(
                "Series is non-stationary. Consider differencing or transformation "
                "before modeling with ARIMA."
            )
        else:
            recommendations.append("Series is stationary and suitable for time series modeling.")
        
        return TimeSeriesResult(
            analysis_type="stationarity",
            is_stationary=is_stationary,
            adf_statistic=adf_statistic,
            adf_pvalue=adf_pvalue,
            interpretation=interpretation,
            recommendations=recommendations
        )
    
    def forecast_arima(self, data: Union[pd.Series, np.ndarray],
                      order: Tuple[int, int, int] = (1, 1, 1),
                      steps: int = 10) -> TimeSeriesResult:
        """
        Forecast using ARIMA model.
        
        Args:
            data: Historical time series data
            order: ARIMA order (p, d, q)
            steps: Number of steps to forecast
            
        Returns:
            TimeSeriesResult with forecast
        """
        if isinstance(data, pd.Series):
            data_array: np.ndarray = np.asarray(data.values)
        else:
            data_array = data
        
        # Remove NaN values
        data_clean = data_array[~np.isnan(data_array)]
        
        try:
            # Fit ARIMA model
            model = ARIMA(data_clean, order=order)
            fitted_model = model.fit()
            
            # Forecast
            forecast_result = fitted_model.forecast(steps=steps)
            forecast = forecast_result
            
            # Get confidence intervals
            forecast_obj = fitted_model.get_forecast(steps=steps)
            forecast_ci = forecast_obj.conf_int()
            
            interpretation = (
                f"ARIMA{order} model fitted and {steps}-step forecast generated. "
                f"AIC={fitted_model.aic:.2f}, BIC={fitted_model.bic:.2f}."
            )
            
            recommendations = [
                "Review residual diagnostics to ensure model adequacy",
                "Consider trying different ARIMA orders and compare AIC/BIC",
                "Validate forecast accuracy on hold-out data"
            ]
            
            return TimeSeriesResult(
                analysis_type="forecasting",
                forecast=forecast,
                forecast_ci_lower=forecast_ci.iloc[:, 0].values,
                forecast_ci_upper=forecast_ci.iloc[:, 1].values,
                forecast_steps=steps,
                model_type=f"ARIMA{order}",
                model_params={"order": order, "aic": fitted_model.aic, "bic": fitted_model.bic},
                interpretation=interpretation,
                recommendations=recommendations
            )
        except Exception as e:
            return TimeSeriesResult(
                analysis_type="forecasting",
                forecast_steps=steps,
                interpretation=f"ARIMA forecasting failed: {str(e)}",
                recommendations=["Try different ARIMA parameters", "Check data quality and length"]
            )


# Continue in next part for report generation...
