"""
Statistical Analysis Engine for Sparta AI

Provides comprehensive statistical analysis capabilities including:
- Descriptive statistics and data summarization
- Correlation analysis (Pearson, Spearman, Kendall)
- Hypothesis testing (t-tests, ANOVA, chi-square, etc.)
- Regression analysis (linear, polynomial, logistic)
- Time series analysis and forecasting
- Outlier detection and distribution fitting
- Automatic test selection and assumption checking
- Plain English interpretations and insights
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# Statistical libraries
from scipy import stats
from scipy.stats import (
    normaltest, shapiro, levene, bartlett, chi2_contingency
)
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson


class DataType(Enum):
    """Data type classification for statistical analysis."""
    CONTINUOUS = "continuous"
    ORDINAL = "ordinal"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    COUNT = "count"
    TIME_SERIES = "time_series"


class TestType(Enum):
    """Available statistical tests."""
    T_TEST_IND = "independent_t_test"
    T_TEST_PAIRED = "paired_t_test"
    T_TEST_ONE = "one_sample_t_test"
    ANOVA = "anova"
    KRUSKAL_WALLIS = "kruskal_wallis"
    MANN_WHITNEY = "mann_whitney"
    WILCOXON = "wilcoxon"
    CHI_SQUARE = "chi_square"
    FISHER_EXACT = "fisher_exact"
    CORRELATION = "correlation"
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    TIME_SERIES = "time_series_analysis"


class EffectSize(Enum):
    """Effect size interpretation categories."""
    NEGLIGIBLE = "negligible"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"


@dataclass
class AssumptionCheckResult:
    """Results from checking statistical test assumptions."""
    test_name: str
    passed: bool
    statistic: Optional[float] = None
    p_value: Optional[float] = None
    interpretation: str = ""
    recommendation: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatisticalTestResult:
    """Comprehensive results from a statistical test."""
    test_type: str
    test_name: str
    statistic: float
    p_value: float
    degrees_of_freedom: Optional[Union[int, Tuple[int, int]]] = None
    effect_size: Optional[float] = None
    effect_size_name: Optional[str] = None
    effect_size_interpretation: Optional[str] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    power: Optional[float] = None
    sample_size: int = 0
    
    # Interpretation
    is_significant: bool = False
    significance_level: float = 0.05
    interpretation: str = ""
    recommendation: str = ""
    
    # Additional details
    assumptions_met: bool = True
    assumption_checks: List[AssumptionCheckResult] = field(default_factory=list)
    alternative_tests: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Visualization suggestions
    suggested_visualizations: List[str] = field(default_factory=list)


@dataclass
class DescriptiveStats:
    """Comprehensive descriptive statistics."""
    variable_name: str
    n: int
    n_missing: int
    mean: Optional[float] = None
    median: Optional[float] = None
    mode: Optional[Union[float, str]] = None
    std: Optional[float] = None
    variance: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    range: Optional[float] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    coefficient_of_variation: Optional[float] = None
    
    # Distribution info
    is_normal: Optional[bool] = None
    normality_p_value: Optional[float] = None
    
    # Outliers
    n_outliers: int = 0
    outlier_indices: List[int] = field(default_factory=list)
    
    # For categorical data
    unique_values: Optional[int] = None
    most_common: Optional[List[Tuple[Any, int]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "variable_name": self.variable_name,
            "n": self.n,
            "n_missing": self.n_missing,
            "mean": self.mean,
            "median": self.median,
            "mode": self.mode,
            "std": self.std,
            "variance": self.variance,
            "min": self.min_value,
            "max": self.max_value,
            "range": self.range,
            "q1": self.q1,
            "q3": self.q3,
            "iqr": self.iqr,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "cv": self.coefficient_of_variation,
            "is_normal": self.is_normal,
            "normality_p_value": self.normality_p_value,
            "n_outliers": self.n_outliers,
            "unique_values": self.unique_values,
            "most_common": self.most_common
        }


class AssumptionChecker:
    """
    Checks statistical assumptions for various tests.
    
    Provides methods to validate:
    - Normality (Shapiro-Wilk, Anderson-Darling, Kolmogorov-Smirnov)
    - Homogeneity of variance (Levene, Bartlett)
    - Independence (Durbin-Watson)
    - Linearity and homoscedasticity for regression
    """
    
    @staticmethod
    def check_normality(data: np.ndarray, method: str = "shapiro", 
                       alpha: float = 0.05) -> AssumptionCheckResult:
        """
        Check if data follows a normal distribution.
        
        Args:
            data: Array of data values
            method: Test method ("shapiro", "normaltest", "anderson")
            alpha: Significance level
            
        Returns:
            AssumptionCheckResult with test details
        """
        data = np.array(data)
        data = data[~np.isnan(data)]  # Remove NaN values
        
        if len(data) < 3:
            return AssumptionCheckResult(
                test_name="Normality Test",
                passed=False,
                interpretation="Insufficient data for normality test (n < 3)",
                recommendation="Collect more data or use non-parametric tests"
            )
        
        try:
            if method == "shapiro":
                if len(data) > 5000:
                    # Shapiro-Wilk can be slow for large samples
                    method = "normaltest"
                else:
                    statistic, p_value = shapiro(data)
                    test_name = "Shapiro-Wilk Test"
            
            if method == "normaltest":
                statistic, p_value = normaltest(data)
                test_name = "D'Agostino-Pearson Test"
            
            elif method == "anderson":
                result = stats.anderson(data)
                # Use 5% significance level
                statistic = result.statistic  # type: ignore
                critical_value = result.critical_values[2]  # type: ignore # 5% level
                p_value = None  # Anderson doesn't provide p-value directly
                test_name = "Anderson-Darling Test"
                passed = statistic < critical_value
                
                interpretation = (
                    f"Data {'appears' if passed else 'does not appear'} normally distributed "
                    f"(statistic={statistic:.4f}, critical value at 5%={critical_value:.4f})"
                )
                
                return AssumptionCheckResult(
                    test_name=test_name,
                    passed=passed,
                    statistic=statistic,
                    interpretation=interpretation,
                    recommendation=(
                        "Normality assumption is satisfied" if passed else
                        "Consider using non-parametric alternatives or data transformation"
                    ),
                    details={"critical_values": result.critical_values.tolist(),  # type: ignore
                            "significance_levels": result.significance_level.tolist()}  # type: ignore
                )
            
            passed = p_value > alpha
            
            interpretation = (
                f"Data {'appears' if passed else 'does not appear'} normally distributed "
                f"(p={p_value:.4f}, α={alpha})"
            )
            
            recommendation = (
                "Normality assumption is satisfied" if passed else
                "Consider using non-parametric alternatives (Mann-Whitney, Kruskal-Wallis) "
                "or data transformation (log, square root)"
            )
            
            return AssumptionCheckResult(
                test_name=test_name,
                passed=passed,
                statistic=statistic,
                p_value=p_value,
                interpretation=interpretation,
                recommendation=recommendation,
                details={"alpha": alpha, "sample_size": len(data)}
            )
            
        except Exception as e:
            return AssumptionCheckResult(
                test_name="Normality Test",
                passed=False,
                interpretation=f"Error during normality test: {str(e)}",
                recommendation="Check data quality and try non-parametric tests"
            )
    
    @staticmethod
    def check_equal_variances(*groups: np.ndarray, method: str = "levene",
                             alpha: float = 0.05) -> AssumptionCheckResult:
        """
        Check homogeneity of variance across groups.
        
        Args:
            groups: Variable number of data arrays for each group
            method: Test method ("levene" or "bartlett")
            alpha: Significance level
            
        Returns:
            AssumptionCheckResult with test details
        """
        # Remove NaN values from each group
        clean_groups = [np.array(g)[~np.isnan(g)] for g in groups]
        
        if any(len(g) < 2 for g in clean_groups):
            return AssumptionCheckResult(
                test_name="Homogeneity of Variance Test",
                passed=False,
                interpretation="One or more groups have insufficient data (n < 2)",
                recommendation="Collect more data or use Welch's t-test/ANOVA"
            )
        
        try:
            if method == "levene":
                statistic, p_value = levene(*clean_groups)
                test_name = "Levene's Test"
            elif method == "bartlett":
                statistic, p_value = bartlett(*clean_groups)
                test_name = "Bartlett's Test"
            else:
                raise ValueError(f"Unknown method: {method}")
            
            passed = p_value > alpha
            
            interpretation = (
                f"Variances {'appear equal' if passed else 'appear unequal'} across groups "
                f"(p={p_value:.4f}, α={alpha})"
            )
            
            recommendation = (
                "Homogeneity of variance assumption is satisfied" if passed else
                "Consider using Welch's t-test/ANOVA or data transformation"
            )
            
            return AssumptionCheckResult(
                test_name=test_name,
                passed=passed,
                statistic=statistic,
                p_value=p_value,
                interpretation=interpretation,
                recommendation=recommendation,
                details={
                    "alpha": alpha,
                    "n_groups": len(clean_groups),
                    "group_sizes": [len(g) for g in clean_groups]
                }
            )
            
        except Exception as e:
            return AssumptionCheckResult(
                test_name="Homogeneity of Variance Test",
                passed=False,
                interpretation=f"Error during variance test: {str(e)}",
                recommendation="Check data quality or use robust alternatives"
            )
    
    @staticmethod
    def check_independence(residuals: np.ndarray, 
                          alpha: float = 0.05) -> AssumptionCheckResult:
        """
        Check independence of observations using Durbin-Watson test.
        
        Args:
            residuals: Residuals from regression model
            alpha: Significance level
            
        Returns:
            AssumptionCheckResult with test details
        """
        residuals = np.array(residuals)
        residuals = residuals[~np.isnan(residuals)]
        
        if len(residuals) < 3:
            return AssumptionCheckResult(
                test_name="Durbin-Watson Test",
                passed=False,
                interpretation="Insufficient data for independence test (n < 3)",
                recommendation="Collect more data"
            )
        
        try:
            dw_statistic = durbin_watson(residuals)
            
            # DW statistic ranges from 0 to 4
            # Values around 2 suggest no autocorrelation
            # Values < 1 or > 3 suggest positive or negative autocorrelation
            passed = 1.5 <= dw_statistic <= 2.5
            
            if dw_statistic < 1.5:
                autocorr_type = "positive"
            elif dw_statistic > 2.5:
                autocorr_type = "negative"
            else:
                autocorr_type = "no"
            
            interpretation = (
                f"Evidence of {autocorr_type} autocorrelation "
                f"(Durbin-Watson={dw_statistic:.4f})"
            )
            
            recommendation = (
                "Independence assumption is satisfied" if passed else
                f"Consider using time series methods or adding lagged variables "
                f"to account for {autocorr_type} autocorrelation"
            )
            
            return AssumptionCheckResult(
                test_name="Durbin-Watson Test",
                passed=passed,
                statistic=dw_statistic,
                interpretation=interpretation,
                recommendation=recommendation,
                details={"autocorrelation_type": autocorr_type}
            )
            
        except Exception as e:
            return AssumptionCheckResult(
                test_name="Durbin-Watson Test",
                passed=False,
                interpretation=f"Error during independence test: {str(e)}",
                recommendation="Check data quality"
            )
    
    @staticmethod
    def check_homoscedasticity(x: np.ndarray, residuals: np.ndarray,
                               alpha: float = 0.05) -> AssumptionCheckResult:
        """
        Check homoscedasticity (constant variance of residuals) using Breusch-Pagan test.
        
        Args:
            x: Independent variable(s)
            residuals: Residuals from regression model
            alpha: Significance level
            
        Returns:
            AssumptionCheckResult with test details
        """
        try:
            # Ensure x is 2D
            if x.ndim == 1:
                x = x.reshape(-1, 1)
            
            lm_statistic, lm_pvalue, f_statistic, f_pvalue = het_breuschpagan(residuals, x)
            
            passed = lm_pvalue > alpha
            
            interpretation = (
                f"Residuals {'appear homoscedastic' if passed else 'appear heteroscedastic'} "
                f"(p={lm_pvalue:.4f}, α={alpha})"
            )
            
            recommendation = (
                "Homoscedasticity assumption is satisfied" if passed else
                "Consider using robust standard errors or weighted least squares"
            )
            
            return AssumptionCheckResult(
                test_name="Breusch-Pagan Test",
                passed=bool(passed),  # type: ignore
                statistic=lm_statistic,
                p_value=float(lm_pvalue),  # type: ignore
                interpretation=interpretation,
                recommendation=recommendation,
                details={
                    "lagrange_multiplier": lm_statistic,
                    "lm_pvalue": lm_pvalue,
                    "f_statistic": f_statistic,
                    "f_pvalue": f_pvalue,
                    "alpha": alpha
                }
            )
            
        except Exception as e:
            return AssumptionCheckResult(
                test_name="Breusch-Pagan Test",
                passed=False,
                interpretation=f"Error during homoscedasticity test: {str(e)}",
                recommendation="Check data quality or use robust methods"
            )


class TestSelector:
    """
    Automatically selects appropriate statistical tests based on data characteristics.
    
    Considers:
    - Data types (continuous, categorical, ordinal)
    - Number of groups/variables
    - Sample sizes
    - Distribution characteristics
    - Study design (independent vs paired)
    """
    
    @staticmethod
    def detect_data_type(data: Union[pd.Series, np.ndarray]) -> DataType:
        """
        Automatically detect the type of data.
        
        Args:
            data: Data to analyze
            
        Returns:
            DataType enum value
        """
        if isinstance(data, pd.Series):
            # Check pandas dtype
            if pd.api.types.is_numeric_dtype(data):
                unique_values = data.nunique()
                total_values = len(data.dropna())
                
                if unique_values == 2:
                    return DataType.BINARY
                elif unique_values <= 10 and unique_values / total_values < 0.05:
                    return DataType.CATEGORICAL
                elif data.min() >= 0 and (data % 1 == 0).all():
                    return DataType.COUNT
                else:
                    return DataType.CONTINUOUS
            elif pd.api.types.is_object_dtype(data):  # type: ignore
                return DataType.CATEGORICAL
            elif pd.api.types.is_datetime64_any_dtype(data):
                return DataType.TIME_SERIES
        
        # For numpy arrays
        data_array = np.array(data)
        
        # Try to detect if numeric
        try:
            # If we can convert to float, it's numeric
            numeric_data = data_array.astype(float)
            clean_data = numeric_data[~np.isnan(numeric_data)]
            unique_values = len(np.unique(clean_data))
            total_values = len(clean_data)
            
            if unique_values == 2:
                return DataType.BINARY
            # Only treat as categorical if very few unique values relative to total
            elif unique_values <= 10 and total_values > 0 and unique_values / total_values < 0.05:
                return DataType.CATEGORICAL
            # Check if all values are non-negative integers (count data)
            elif np.all(clean_data >= 0) and np.all(clean_data % 1 == 0):
                return DataType.COUNT
            else:
                return DataType.CONTINUOUS
        except (ValueError, TypeError):
            # If can't convert to float, treat as categorical
            return DataType.CATEGORICAL
    
    @staticmethod
    def select_comparison_test(group_data: List[np.ndarray], 
                               paired: bool = False,
                               check_assumptions: bool = True) -> Tuple[TestType, Dict[str, Any]]:
        """
        Select appropriate test for comparing groups.
        
        Args:
            group_data: List of data arrays for each group
            paired: Whether groups are paired/dependent
            check_assumptions: Whether to check test assumptions
            
        Returns:
            Tuple of (TestType, metadata dict)
        """
        n_groups = len(group_data)
        metadata = {"n_groups": n_groups, "paired": paired}
        
        if n_groups < 2:
            raise ValueError("Need at least 2 groups for comparison")
        
        # Check sample sizes
        group_sizes = [len(g) for g in group_data]
        min_size = min(group_sizes)
        metadata["group_sizes"] = group_sizes
        metadata["min_size"] = min_size
        
        # For 2 groups
        if n_groups == 2:
            if paired:
                if check_assumptions:
                    # Check normality of differences
                    differences = group_data[0] - group_data[1]
                    normality = AssumptionChecker.check_normality(differences)
                    metadata["normality_check"] = normality
                    
                    if normality.passed:
                        return TestType.T_TEST_PAIRED, metadata
                    else:
                        return TestType.WILCOXON, metadata
                else:
                    return TestType.T_TEST_PAIRED, metadata
            else:
                if check_assumptions:
                    # Check normality for both groups
                    norm1 = AssumptionChecker.check_normality(group_data[0])
                    norm2 = AssumptionChecker.check_normality(group_data[1])
                    metadata["normality_group1"] = norm1
                    metadata["normality_group2"] = norm2
                    
                    if norm1.passed and norm2.passed:
                        # Check equal variances
                        var_check = AssumptionChecker.check_equal_variances(
                            group_data[0], group_data[1]
                        )
                        metadata["variance_check"] = var_check
                        return TestType.T_TEST_IND, metadata
                    else:
                        return TestType.MANN_WHITNEY, metadata
                else:
                    return TestType.T_TEST_IND, metadata
        
        # For 3+ groups
        else:
            if paired:
                if check_assumptions:
                    # Check normality for each group
                    all_normal = all(
                        AssumptionChecker.check_normality(g).passed 
                        for g in group_data
                    )
                    metadata["all_normal"] = all_normal
                    
                    if all_normal:
                        return TestType.ANOVA, metadata  # Repeated measures ANOVA
                    else:
                        return TestType.KRUSKAL_WALLIS, metadata  # Friedman test
                else:
                    return TestType.ANOVA, metadata
            else:
                if check_assumptions:
                    # Check normality for all groups
                    all_normal = all(
                        AssumptionChecker.check_normality(g).passed 
                        for g in group_data
                    )
                    metadata["all_normal"] = all_normal
                    
                    if all_normal:
                        # Check equal variances
                        var_check = AssumptionChecker.check_equal_variances(*group_data)
                        metadata["variance_check"] = var_check
                        return TestType.ANOVA, metadata
                    else:
                        return TestType.KRUSKAL_WALLIS, metadata
                else:
                    return TestType.ANOVA, metadata
    
    @staticmethod
    def select_correlation_test(x: np.ndarray, y: np.ndarray,
                                check_assumptions: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Select appropriate correlation test based on data characteristics.
        
        Args:
            x: First variable
            y: Second variable
            check_assumptions: Whether to check test assumptions
            
        Returns:
            Tuple of (correlation method, metadata dict)
        """
        metadata = {}
        
        if check_assumptions:
            # Check normality for both variables
            norm_x = AssumptionChecker.check_normality(x)
            norm_y = AssumptionChecker.check_normality(y)
            metadata["normality_x"] = norm_x
            metadata["normality_y"] = norm_y
            
            if norm_x.passed and norm_y.passed:
                return "pearson", metadata
            else:
                # Spearman is more robust to outliers
                return "spearman", metadata
        else:
            return "pearson", metadata


class EffectSizeCalculator:
    """
    Calculates effect sizes and provides interpretations.
    
    Implements:
    - Cohen's d for t-tests
    - Eta-squared and omega-squared for ANOVA
    - Phi and Cramer's V for chi-square
    - R-squared for correlation and regression
    - Cliff's delta for non-parametric tests
    """
    
    @staticmethod
    def cohens_d(group1: np.ndarray, group2: np.ndarray, 
                 paired: bool = False) -> Tuple[float, str]:
        """
        Calculate Cohen's d effect size.
        
        Args:
            group1: First group data
            group2: Second group data
            paired: Whether groups are paired
            
        Returns:
            Tuple of (effect size, interpretation)
        """
        if paired:
            differences = group1 - group2
            d = np.mean(differences) / np.std(differences, ddof=1)
        else:
            mean_diff = np.mean(group1) - np.mean(group2)
            pooled_std = np.sqrt((np.var(group1, ddof=1) + np.var(group2, ddof=1)) / 2)
            d = mean_diff / pooled_std
        
        abs_d = abs(d)
        if abs_d < 0.2:
            interpretation = EffectSize.NEGLIGIBLE.value
        elif abs_d < 0.5:
            interpretation = EffectSize.SMALL.value
        elif abs_d < 0.8:
            interpretation = EffectSize.MEDIUM.value
        else:
            interpretation = EffectSize.LARGE.value
        
        return float(d), interpretation  # type: ignore
    
    @staticmethod
    def eta_squared(groups: List[np.ndarray]) -> Tuple[float, str]:
        """
        Calculate eta-squared effect size for ANOVA.
        
        Args:
            groups: List of group data arrays
            
        Returns:
            Tuple of (effect size, interpretation)
        """
        # Combine all data
        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)
        
        # Between-group sum of squares
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
        
        # Total sum of squares
        ss_total = np.sum((all_data - grand_mean)**2)
        
        eta_sq = ss_between / ss_total
        
        if eta_sq < 0.01:
            interpretation = EffectSize.NEGLIGIBLE.value
        elif eta_sq < 0.06:
            interpretation = EffectSize.SMALL.value
        elif eta_sq < 0.14:
            interpretation = EffectSize.MEDIUM.value
        else:
            interpretation = EffectSize.LARGE.value
        
        return float(eta_sq), interpretation  # type: ignore
    
    @staticmethod
    def cramers_v(contingency_table: np.ndarray) -> Tuple[float, str]:
        """
        Calculate Cramer's V effect size for chi-square test.
        
        Args:
            contingency_table: Contingency table from chi-square test
            
        Returns:
            Tuple of (effect size, interpretation)
        """
        chi2 = chi2_contingency(contingency_table)[0]
        n = np.sum(contingency_table)
        min_dim = min(contingency_table.shape) - 1
        
        v = np.sqrt(chi2 / (n * min_dim))
        
        if v < 0.1:
            interpretation = EffectSize.NEGLIGIBLE.value
        elif v < 0.3:
            interpretation = EffectSize.SMALL.value
        elif v < 0.5:
            interpretation = EffectSize.MEDIUM.value
        else:
            interpretation = EffectSize.LARGE.value
        
        return v, interpretation
    
    @staticmethod
    def r_squared_interpretation(r_squared: float) -> str:
        """
        Interpret R-squared value.
        
        Args:
            r_squared: R-squared value
            
        Returns:
            Interpretation string
        """
        if r_squared < 0.10:
            return EffectSize.NEGLIGIBLE.value
        elif r_squared < 0.30:
            return EffectSize.SMALL.value
        elif r_squared < 0.50:
            return EffectSize.MEDIUM.value
        else:
            return EffectSize.LARGE.value


class PowerAnalyzer:
    """
    Performs power analysis and sample size calculations.
    """
    
    @staticmethod
    def calculate_power_ttest(n_per_group: int, effect_size: float,
                             alpha: float = 0.05) -> float:
        """
        Calculate statistical power for independent t-test.
        
        Args:
            n_per_group: Sample size per group
            effect_size: Cohen's d effect size
            alpha: Significance level
            
        Returns:
            Statistical power (0-1)
        """
        power_analysis = TTestIndPower()
        power = power_analysis.solve_power(
            effect_size=effect_size,
            nobs1=n_per_group,
            alpha=alpha,
            ratio=1.0
        )
        return power
    
    @staticmethod
    def calculate_required_sample_size_ttest(effect_size: float, power: float = 0.8,
                                            alpha: float = 0.05) -> int:
        """
        Calculate required sample size for independent t-test.
        
        Args:
            effect_size: Cohen's d effect size
            power: Desired statistical power
            alpha: Significance level
            
        Returns:
            Required sample size per group
        """
        power_analysis = TTestIndPower()
        n = power_analysis.solve_power(
            effect_size=effect_size,
            power=power,
            alpha=alpha,
            ratio=1.0
        )
        return int(np.ceil(n))
    
    @staticmethod
    def calculate_power_anova(n_per_group: int, n_groups: int,
                             effect_size: float, alpha: float = 0.05) -> float:
        """
        Calculate statistical power for ANOVA.
        
        Args:
            n_per_group: Sample size per group
            n_groups: Number of groups
            effect_size: Effect size (f)
            alpha: Significance level
            
        Returns:
            Statistical power (0-1)
        """
        power_analysis = FTestAnovaPower()
        power = power_analysis.solve_power(
            effect_size=effect_size,
            nobs=n_per_group * n_groups,
            alpha=alpha,
            k_groups=n_groups
        )
        return power


# Continue in next part...
