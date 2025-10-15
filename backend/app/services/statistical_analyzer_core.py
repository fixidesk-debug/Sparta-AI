"""
Core Statistical Analysis Engine - Main Analyzer Class

Provides comprehensive statistical analysis methods for Sparta AI.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Union
from scipy import stats
from scipy.stats import (
    ttest_ind, ttest_rel, f_oneway,
    kruskal, mannwhitneyu, skew, kurtosis
)
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from .statistical_analyzer import (
    DataType, TestType, EffectSize,
    StatisticalTestResult, DescriptiveStats,
    AssumptionChecker, TestSelector, EffectSizeCalculator, PowerAnalyzer
)


class OutlierDetector:
    """
    Multiple methods for outlier detection.
    """
    
    @staticmethod
    def iqr_method(data: np.ndarray, multiplier: float = 1.5) -> Tuple[List[int], np.ndarray]:
        """
        Detect outliers using IQR method.
        
        Args:
            data: Data array
            multiplier: IQR multiplier (default 1.5)
            
        Returns:
            Tuple of (outlier indices, mask array)
        """
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr_value = q3 - q1
        
        lower_bound = q1 - multiplier * iqr_value
        upper_bound = q3 + multiplier * iqr_value
        
        outlier_mask = (data < lower_bound) | (data > upper_bound)
        outlier_indices = np.where(outlier_mask)[0].tolist()
        
        return outlier_indices, outlier_mask  # type: ignore
    
    @staticmethod
    def zscore_method(data: np.ndarray, threshold: float = 3.0) -> Tuple[List[int], np.ndarray]:
        """
        Detect outliers using Z-score method.
        
        Args:
            data: Data array
            threshold: Z-score threshold (default 3.0)
            
        Returns:
            Tuple of (outlier indices, mask array)
        """
        z_scores = np.abs(stats.zscore(data, nan_policy='omit'))
        outlier_mask = z_scores > threshold
        outlier_indices = np.where(outlier_mask)[0].tolist()
        
        return outlier_indices, outlier_mask  # type: ignore
    
    @staticmethod
    def modified_zscore_method(data: np.ndarray, threshold: float = 3.5) -> Tuple[List[int], np.ndarray]:
        """
        Detect outliers using modified Z-score (more robust).
        
        Args:
            data: Data array
            threshold: Modified Z-score threshold (default 3.5)
            
        Returns:
            Tuple of (outlier indices, mask array)
        """
        median = np.median(data)
        mad = np.median(np.abs(data - median))
        
        if mad == 0:
            # If MAD is 0, use standard deviation
            modified_z_scores = np.abs(data - median) / np.std(data)
        else:
            modified_z_scores = 0.6745 * (data - median) / mad
        
        outlier_mask = modified_z_scores > threshold
        outlier_indices = np.where(outlier_mask)[0].tolist()
        
        return outlier_indices, outlier_mask  # type: ignore
    
    @staticmethod
    def isolation_forest_method(data: np.ndarray, contamination: float = 0.1) -> Tuple[List[int], np.ndarray]:
        """
        Detect outliers using Isolation Forest algorithm.
        
        Args:
            data: Data array
            contamination: Expected proportion of outliers
            
        Returns:
            Tuple of (outlier indices, mask array)
        """
        from sklearn.ensemble import IsolationForest
        
        data_2d = data.reshape(-1, 1)
        clf = IsolationForest(contamination=contamination, random_state=42)
        predictions = clf.fit_predict(data_2d)
        
        outlier_mask = predictions == -1
        outlier_indices = np.where(outlier_mask)[0].tolist()
        
        return outlier_indices, outlier_mask  # type: ignore


class StatisticalAnalyzer:
    """
    Comprehensive statistical analysis engine for Sparta AI.
    
    Provides methods for:
    - Descriptive statistics
    - Hypothesis testing (t-tests, ANOVA, chi-square, etc.)
    - Correlation and regression analysis
    - Time series analysis and forecasting
    - Outlier detection
    - Distribution fitting
    """
    
    def __init__(self, alpha: float = 0.05, confidence_level: float = 0.95):
        """
        Initialize the statistical analyzer.
        
        Args:
            alpha: Significance level for hypothesis tests
            confidence_level: Confidence level for intervals
        """
        self.alpha = alpha
        self.confidence_level = confidence_level
        self.assumption_checker = AssumptionChecker()
        self.test_selector = TestSelector()
        self.effect_calculator = EffectSizeCalculator()
        self.power_analyzer = PowerAnalyzer()
        self.outlier_detector = OutlierDetector()
    
    def describe(self, data: Union[pd.Series, np.ndarray], 
                variable_name: str = "variable") -> DescriptiveStats:
        """
        Compute comprehensive descriptive statistics.
        
        Args:
            data: Data to analyze
            variable_name: Name of the variable
            
        Returns:
            DescriptiveStats object with all statistics
        """
        if isinstance(data, pd.Series):
            data_array = data.values
        else:
            data_array = np.array(data)
        
        # Handle missing values
        n_total = len(data_array)
        clean_data = data_array[~np.isnan(data_array)]  # type: ignore
        n = len(clean_data)
        n_missing = n_total - n
        
        if n == 0:
            return DescriptiveStats(
                variable_name=variable_name,
                n=0,
                n_missing=n_missing
            )
        
        # Detect data type
        data_type = self.test_selector.detect_data_type(data)
        
        stats_dict = {
            "variable_name": variable_name,
            "n": n,
            "n_missing": n_missing
        }
        
        # For numerical data
        if data_type in [DataType.CONTINUOUS, DataType.COUNT]:
            stats_dict["mean"] = float(np.mean(clean_data))
            stats_dict["median"] = float(np.median(clean_data))
            stats_dict["std"] = float(np.std(clean_data, ddof=1))
            stats_dict["variance"] = float(np.var(clean_data, ddof=1))
            stats_dict["min_value"] = float(np.min(clean_data))
            stats_dict["max_value"] = float(np.max(clean_data))
            stats_dict["range"] = float(np.ptp(clean_data))
            stats_dict["q1"] = float(np.percentile(clean_data, 25))
            stats_dict["q3"] = float(np.percentile(clean_data, 75))
            stats_dict["iqr"] = float(stats_dict["q3"] - stats_dict["q1"])
            stats_dict["skewness"] = float(skew(clean_data))
            stats_dict["kurtosis"] = float(kurtosis(clean_data))
            
            # Coefficient of variation
            if stats_dict["mean"] != 0:
                stats_dict["coefficient_of_variation"] = abs(stats_dict["std"] / stats_dict["mean"])
            
            # Mode (most common value)
            mode_result = stats.mode(clean_data, keepdims=False)
            stats_dict["mode"] = float(mode_result.mode)
            
            # Normality test
            if n >= 3:
                normality = self.assumption_checker.check_normality(clean_data)
                stats_dict["is_normal"] = normality.passed
                stats_dict["normality_p_value"] = normality.p_value
            
            # Outlier detection
            outlier_indices, _ = self.outlier_detector.iqr_method(clean_data)
            stats_dict["n_outliers"] = len(outlier_indices)
            stats_dict["outlier_indices"] = outlier_indices
        
        # For categorical data
        else:
            unique_values = np.unique(clean_data)
            stats_dict["unique_values"] = len(unique_values)
            
            # Most common values
            value_counts = pd.Series(clean_data).value_counts()
            stats_dict["most_common"] = list(zip(value_counts.index[:5], value_counts.values[:5]))
            
            # Mode
            stats_dict["mode"] = value_counts.index[0]
        
        return DescriptiveStats(**stats_dict)
    
    def t_test_independent(self, group1: np.ndarray, group2: np.ndarray,
                          equal_var: bool = True,
                          alternative: str = "two-sided") -> StatisticalTestResult:
        """
        Perform independent samples t-test.
        
        Args:
            group1: First group data
            group2: Second group data
            equal_var: Whether to assume equal variances (Student's vs Welch's)
            alternative: "two-sided", "less", or "greater"
            
        Returns:
            StatisticalTestResult with comprehensive results
        """
        # Clean data
        group1 = np.array(group1)[~np.isnan(group1)]
        group2 = np.array(group2)[~np.isnan(group2)]
        
        # Check assumptions
        assumption_checks = []
        
        norm1 = self.assumption_checker.check_normality(group1)
        norm2 = self.assumption_checker.check_normality(group2)
        assumption_checks.extend([norm1, norm2])
        
        assumptions_met = norm1.passed and norm2.passed
        
        if equal_var:
            var_check = self.assumption_checker.check_equal_variances(group1, group2)
            assumption_checks.append(var_check)
            assumptions_met = assumptions_met and var_check.passed
        
        # Perform t-test
        test_result = ttest_ind(group1, group2, equal_var=equal_var, alternative=alternative)
        statistic = float(test_result[0])  # type: ignore
        p_value = float(test_result[1])  # type: ignore
        
        # Calculate effect size
        effect_size, effect_interp = self.effect_calculator.cohens_d(group1, group2, paired=False)
        
        # Calculate confidence interval for mean difference
        mean_diff = np.mean(group1) - np.mean(group2)
        se_diff = np.sqrt(np.var(group1, ddof=1)/len(group1) + np.var(group2, ddof=1)/len(group2))
        df = len(group1) + len(group2) - 2
        t_crit = stats.t.ppf(1 - self.alpha/2, df)
        ci = (mean_diff - t_crit * se_diff, mean_diff + t_crit * se_diff)
        
        # Calculate power
        power = self.power_analyzer.calculate_power_ttest(
            n_per_group=min(len(group1), len(group2)),
            effect_size=abs(effect_size),
            alpha=self.alpha
        )
        
        # Interpretation
        is_significant = p_value < self.alpha
        
        interpretation = (
            f"{'Significant' if is_significant else 'No significant'} difference between groups "
            f"(t={statistic:.4f}, p={p_value:.4f}, Cohen's d={effect_size:.4f}). "
            f"The mean difference is {mean_diff:.4f} with {self.confidence_level*100:.0f}% CI [{ci[0]:.4f}, {ci[1]:.4f}]. "
            f"Effect size is {effect_interp}."
        )
        
        recommendation = ""
        if not assumptions_met:
            recommendation = "Consider using Mann-Whitney U test (non-parametric alternative) as normality assumptions are violated."
        elif power < 0.8:
            recommendation = f"Statistical power is low ({power:.2f}). Consider increasing sample size."
        
        alternative_tests = []
        if not assumptions_met:
            alternative_tests.append("Mann-Whitney U test")
        if not equal_var:
            alternative_tests.append("Welch's t-test")
        
        return StatisticalTestResult(
            test_type=TestType.T_TEST_IND.value,
            test_name="Independent t-test" if equal_var else "Welch's t-test",
            statistic=statistic,
            p_value=p_value,
            degrees_of_freedom=df,
            effect_size=effect_size,
            effect_size_name="Cohen's d",
            effect_size_interpretation=effect_interp,
            confidence_interval=ci,
            power=power,
            sample_size=len(group1) + len(group2),
            is_significant=is_significant,
            significance_level=self.alpha,
            interpretation=interpretation,
            recommendation=recommendation,
            assumptions_met=assumptions_met,
            assumption_checks=assumption_checks,
            alternative_tests=alternative_tests,
            metadata={
                "group1_mean": float(np.mean(group1)),
                "group2_mean": float(np.mean(group2)),
                "group1_std": float(np.std(group1, ddof=1)),
                "group2_std": float(np.std(group2, ddof=1)),
                "group1_n": len(group1),
                "group2_n": len(group2),
                "mean_difference": mean_diff,
                "equal_var_assumed": equal_var,
                "alternative": alternative
            },
            suggested_visualizations=["boxplot", "violin_plot", "histogram", "qq_plot"]
        )
    
    def t_test_paired(self, before: np.ndarray, after: np.ndarray,
                     alternative: str = "two-sided") -> StatisticalTestResult:
        """
        Perform paired samples t-test.
        
        Args:
            before: Measurements before intervention
            after: Measurements after intervention
            alternative: "two-sided", "less", or "greater"
            
        Returns:
            StatisticalTestResult with comprehensive results
        """
        # Clean data
        before = np.array(before)
        after = np.array(after)
        
        # Remove pairs with any missing values
        valid_mask = ~(np.isnan(before) | np.isnan(after))
        before = before[valid_mask]
        after = after[valid_mask]
        
        if len(before) != len(after):
            raise ValueError("Paired t-test requires equal sample sizes")
        
        # Calculate differences
        differences = before - after
        
        # Check normality of differences
        assumption_checks = []
        norm_check = self.assumption_checker.check_normality(differences)
        assumption_checks.append(norm_check)
        assumptions_met = norm_check.passed
        
        # Perform paired t-test
        statistic, p_value = ttest_rel(before, after, alternative=alternative)
        
        # Calculate effect size
        effect_size, effect_interp = self.effect_calculator.cohens_d(before, after, paired=True)
        
        # Calculate confidence interval for mean difference
        mean_diff = np.mean(differences)
        se_diff = np.std(differences, ddof=1) / np.sqrt(len(differences))
        df = len(differences) - 1
        t_crit = stats.t.ppf(1 - self.alpha/2, df)
        ci = (mean_diff - t_crit * se_diff, mean_diff + t_crit * se_diff)
        
        # Interpretation
        is_significant = p_value < self.alpha
        
        interpretation = (
            f"{'Significant' if is_significant else 'No significant'} change detected "
            f"(t={statistic:.4f}, p={p_value:.4f}, Cohen's d={effect_size:.4f}). "
            f"The mean difference is {mean_diff:.4f} with {self.confidence_level*100:.0f}% CI [{ci[0]:.4f}, {ci[1]:.4f}]. "
            f"Effect size is {effect_interp}."
        )
        
        recommendation = ""
        if not assumptions_met:
            recommendation = "Consider using Wilcoxon signed-rank test (non-parametric alternative) as normality assumption is violated."
        
        alternative_tests = []
        if not assumptions_met:
            alternative_tests.append("Wilcoxon signed-rank test")
        
        return StatisticalTestResult(
            test_type=TestType.T_TEST_PAIRED.value,
            test_name="Paired Samples t-test",
            statistic=statistic,
            p_value=p_value,
            degrees_of_freedom=df,
            effect_size=effect_size,
            effect_size_name="Cohen's d",
            effect_size_interpretation=effect_interp,
            confidence_interval=ci,
            sample_size=len(differences),
            is_significant=is_significant,
            significance_level=self.alpha,
            interpretation=interpretation,
            recommendation=recommendation,
            assumptions_met=assumptions_met,
            assumption_checks=assumption_checks,
            alternative_tests=alternative_tests,
            metadata={
                "before_mean": float(np.mean(before)),
                "after_mean": float(np.mean(after)),
                "mean_difference": mean_diff,
                "differences_std": float(np.std(differences, ddof=1)),
                "n_pairs": len(differences),
                "alternative": alternative
            },
            suggested_visualizations=["paired_plot", "difference_histogram", "before_after_boxplot"]
        )
    
    def anova(self, *groups: np.ndarray, post_hoc: bool = True) -> StatisticalTestResult:
        """
        Perform one-way ANOVA.
        
        Args:
            groups: Variable number of group data arrays
            post_hoc: Whether to perform post-hoc tests (Tukey HSD)
            
        Returns:
            StatisticalTestResult with comprehensive results
        """
        # Clean data
        clean_groups = [np.array(g)[~np.isnan(g)] for g in groups]
        
        if len(clean_groups) < 2:
            raise ValueError("ANOVA requires at least 2 groups")
        
        # Check assumptions
        assumption_checks = []
        
        # Normality for each group
        all_normal = True
        for i, group in enumerate(clean_groups):
            norm = self.assumption_checker.check_normality(group)
            assumption_checks.append(norm)
            all_normal = all_normal and norm.passed
        
        # Homogeneity of variance
        var_check = self.assumption_checker.check_equal_variances(*clean_groups)
        assumption_checks.append(var_check)
        assumptions_met = all_normal and var_check.passed
        
        # Perform ANOVA
        statistic, p_value = f_oneway(*clean_groups)
        
        # Calculate effect size (eta-squared)
        effect_size, effect_interp = self.effect_calculator.eta_squared(clean_groups)
        
        # Degrees of freedom
        k = len(clean_groups)  # number of groups
        n = sum(len(g) for g in clean_groups)  # total sample size
        df_between = k - 1
        df_within = n - k
        df = (df_between, df_within)
        
        # Interpretation
        is_significant = p_value < self.alpha
        
        interpretation = (
            f"{'Significant' if is_significant else 'No significant'} difference among groups "
            f"(F({df_between},{df_within})={statistic:.4f}, p={p_value:.4f}, η²={effect_size:.4f}). "
            f"Effect size is {effect_interp}."
        )
        
        # Post-hoc tests
        post_hoc_results = None
        if post_hoc and is_significant:
            # Prepare data for Tukey HSD
            all_data = []
            group_labels = []
            for i, group in enumerate(clean_groups):
                all_data.extend(group)
                group_labels.extend([f"Group {i+1}"] * len(group))
            
            try:
                tukey = pairwise_tukeyhsd(all_data, group_labels, alpha=self.alpha)
                post_hoc_results = str(tukey)
            except Exception as e:
                post_hoc_results = f"Post-hoc test failed: {str(e)}"
        
        recommendation = ""
        if not assumptions_met:
            recommendation = "Consider using Kruskal-Wallis test (non-parametric alternative) as assumptions are violated."
        elif is_significant and post_hoc:
            recommendation = "Significant difference detected. Review post-hoc tests to identify which groups differ."
        
        alternative_tests = []
        if not assumptions_met:
            alternative_tests.append("Kruskal-Wallis test")
        if not var_check.passed:
            alternative_tests.append("Welch's ANOVA")
        
        metadata = {
            "n_groups": k,
            "total_n": n,
            "group_means": [float(np.mean(g)) for g in clean_groups],
            "group_stds": [float(np.std(g, ddof=1)) for g in clean_groups],
            "group_sizes": [len(g) for g in clean_groups]
        }
        
        if post_hoc_results:
            metadata["post_hoc_tests"] = post_hoc_results
        
        return StatisticalTestResult(
            test_type=TestType.ANOVA.value,
            test_name="One-way ANOVA",
            statistic=statistic,
            p_value=p_value,
            degrees_of_freedom=df,
            effect_size=effect_size,
            effect_size_name="Eta-squared (η²)",
            effect_size_interpretation=effect_interp,
            sample_size=n,
            is_significant=is_significant,
            significance_level=self.alpha,
            interpretation=interpretation,
            recommendation=recommendation,
            assumptions_met=assumptions_met,
            assumption_checks=assumption_checks,
            alternative_tests=alternative_tests,
            metadata=metadata,
            suggested_visualizations=["boxplot", "violin_plot", "means_plot_with_error_bars"]
        )
    
    def mann_whitney_u(self, group1: np.ndarray, group2: np.ndarray,
                      alternative: str = "two-sided") -> StatisticalTestResult:
        """
        Perform Mann-Whitney U test (non-parametric alternative to independent t-test).
        
        Args:
            group1: First group data
            group2: Second group data
            alternative: "two-sided", "less", or "greater"
            
        Returns:
            StatisticalTestResult with comprehensive results
        """
        # Clean data
        group1 = np.array(group1)[~np.isnan(group1)]
        group2 = np.array(group2)[~np.isnan(group2)]
        
        # Perform Mann-Whitney U test
        statistic, p_value = mannwhitneyu(group1, group2, alternative=alternative)
        
        # Calculate rank-biserial correlation as effect size
        n1, n2 = len(group1), len(group2)
        rank_biserial = 1 - (2*statistic) / (n1 * n2)
        
        # Interpret effect size
        abs_rb = abs(rank_biserial)
        if abs_rb < 0.1:
            effect_interp = EffectSize.NEGLIGIBLE.value
        elif abs_rb < 0.3:
            effect_interp = EffectSize.SMALL.value
        elif abs_rb < 0.5:
            effect_interp = EffectSize.MEDIUM.value
        else:
            effect_interp = EffectSize.LARGE.value
        
        # Interpretation
        is_significant = p_value < self.alpha
        
        median1 = np.median(group1)
        median2 = np.median(group2)
        
        interpretation = (
            f"{'Significant' if is_significant else 'No significant'} difference in distributions "
            f"(U={statistic:.4f}, p={p_value:.4f}). "
            f"Group 1 median: {median1:.4f}, Group 2 median: {median2:.4f}. "
            f"Rank-biserial correlation: {rank_biserial:.4f} ({effect_interp} effect)."
        )
        
        recommendation = (
            "Mann-Whitney U test is appropriate when normality assumptions are violated "
            "or for ordinal data. It tests whether one distribution is stochastically greater than the other."
        )
        
        return StatisticalTestResult(
            test_type=TestType.MANN_WHITNEY.value,
            test_name="Mann-Whitney U Test",
            statistic=statistic,
            p_value=p_value,
            effect_size=rank_biserial,
            effect_size_name="Rank-biserial correlation",
            effect_size_interpretation=effect_interp,
            sample_size=n1 + n2,
            is_significant=is_significant,
            significance_level=self.alpha,
            interpretation=interpretation,
            recommendation=recommendation,
            assumptions_met=True,  # Non-parametric test has fewer assumptions
            metadata={
                "group1_median": float(median1),
                "group2_median": float(median2),
                "group1_n": n1,
                "group2_n": n2,
                "alternative": alternative,
                "test_type": "non-parametric"
            },
            suggested_visualizations=["boxplot", "violin_plot", "histogram"]
        )
    
    def kruskal_wallis(self, *groups: np.ndarray) -> StatisticalTestResult:
        """
        Perform Kruskal-Wallis H test (non-parametric alternative to ANOVA).
        
        Args:
            groups: Variable number of group data arrays
            
        Returns:
            StatisticalTestResult with comprehensive results
        """
        # Clean data
        clean_groups = [np.array(g)[~np.isnan(g)] for g in groups]
        
        if len(clean_groups) < 2:
            raise ValueError("Kruskal-Wallis test requires at least 2 groups")
        
        # Perform Kruskal-Wallis test
        statistic, p_value = kruskal(*clean_groups)
        
        # Calculate epsilon-squared as effect size
        n = sum(len(g) for g in clean_groups)
        k = len(clean_groups)
        epsilon_squared = (statistic - k + 1) / (n - k)
        
        # Interpret effect size
        if epsilon_squared < 0.01:
            effect_interp = EffectSize.NEGLIGIBLE.value
        elif epsilon_squared < 0.06:
            effect_interp = EffectSize.SMALL.value
        elif epsilon_squared < 0.14:
            effect_interp = EffectSize.MEDIUM.value
        else:
            effect_interp = EffectSize.LARGE.value
        
        # Degrees of freedom
        df = k - 1
        
        # Interpretation
        is_significant = p_value < self.alpha
        
        medians = [np.median(g) for g in clean_groups]
        
        interpretation = (
            f"{'Significant' if is_significant else 'No significant'} difference in distributions "
            f"(H({df})={statistic:.4f}, p={p_value:.4f}). "
            f"Epsilon-squared: {epsilon_squared:.4f} ({effect_interp} effect). "
            f"Group medians: {', '.join([f'{m:.4f}' for m in medians])}"
        )
        
        recommendation = (
            "Kruskal-Wallis test is appropriate when ANOVA assumptions are violated "
            "or for ordinal data. It tests whether the distributions of multiple groups differ."
        )
        
        return StatisticalTestResult(
            test_type=TestType.KRUSKAL_WALLIS.value,
            test_name="Kruskal-Wallis H Test",
            statistic=statistic,
            p_value=p_value,
            degrees_of_freedom=df,
            effect_size=epsilon_squared,
            effect_size_name="Epsilon-squared (ε²)",
            effect_size_interpretation=effect_interp,
            sample_size=n,
            is_significant=is_significant,
            significance_level=self.alpha,
            interpretation=interpretation,
            recommendation=recommendation,
            assumptions_met=True,  # Non-parametric test
            metadata={
                "n_groups": k,
                "group_medians": [float(m) for m in medians],
                "group_sizes": [len(g) for g in clean_groups],
                "test_type": "non-parametric"
            },
            suggested_visualizations=["boxplot", "violin_plot"]
        )


# Continue in next part...
