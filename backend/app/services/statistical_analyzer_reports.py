"""
Result Interpretation and Report Generation

Provides plain English interpretations and comprehensive reports.
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timezone

from .statistical_analyzer import StatisticalTestResult, DescriptiveStats, AssumptionCheckResult
from .statistical_analyzer_advanced import CorrelationResult, RegressionResult


class ResultInterpreter:
    """
    Converts statistical results into plain English explanations.
    """
    
    @staticmethod
    def interpret_p_value(p_value: float, alpha: float = 0.05) -> str:
        """
        Provide plain English interpretation of p-value.
        
        Args:
            p_value: P-value from statistical test
            alpha: Significance level
            
        Returns:
            Plain English interpretation
        """
        if p_value < 0.001:
            return (
                "The p-value is less than 0.001, which is extremely small. "
                "This provides very strong evidence against the null hypothesis. "
                "The result is highly statistically significant."
            )
        elif p_value < 0.01:
            return (
                f"The p-value is {p_value:.4f}, which is less than 0.01. "
                f"This provides strong evidence against the null hypothesis. "
                f"The result is statistically significant."
            )
        elif p_value < alpha:
            return (
                f"The p-value is {p_value:.4f}, which is less than the significance level "
                f"of {alpha}. This provides sufficient evidence to reject the null hypothesis. "
                f"The result is statistically significant."
            )
        elif p_value < 0.10:
            return (
                f"The p-value is {p_value:.4f}, which is greater than the significance level "
                f"of {alpha} but less than 0.10. This suggests a marginally significant result. "
                f"Consider the practical significance and context."
            )
        else:
            return (
                f"The p-value is {p_value:.4f}, which is greater than the significance level "
                f"of {alpha}. There is insufficient evidence to reject the null hypothesis. "
                f"The result is not statistically significant."
            )
    
    @staticmethod
    def interpret_effect_size(effect_size: float, effect_name: str, 
                            interpretation: str) -> str:
        """
        Provide plain English interpretation of effect size.
        
        Args:
            effect_size: Effect size value
            effect_name: Name of effect size measure
            interpretation: Category (small, medium, large, etc.)
            
        Returns:
            Plain English interpretation
        """
        effect_descriptions = {
            "negligible": "practically meaningless",
            "small": "small but potentially noticeable",
            "medium": "moderate and likely noticeable",
            "large": "large and definitely noticeable",
            "very_large": "very large and substantial"
        }
        
        description = effect_descriptions.get(interpretation, interpretation)
        
        return (
            f"The {effect_name} is {effect_size:.4f}, which represents a {description} "
            f"effect. This tells us about the magnitude of the difference or relationship, "
            f"independent of sample size and statistical significance."
        )
    
    @staticmethod
    def interpret_confidence_interval(ci: Tuple[float, float], 
                                     confidence_level: float,
                                     parameter_name: str = "parameter") -> str:
        """
        Provide plain English interpretation of confidence interval.
        
        Args:
            ci: Confidence interval (lower, upper)
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            parameter_name: Name of parameter being estimated
            
        Returns:
            Plain English interpretation
        """
        return (
            f"We can be {confidence_level*100:.0f}% confident that the true {parameter_name} "
            f"falls between {ci[0]:.4f} and {ci[1]:.4f}. This means that if we repeated "
            f"this study many times, about {confidence_level*100:.0f}% of the intervals "
            f"we calculate would contain the true {parameter_name}."
        )
    
    @staticmethod
    def interpret_power(power: float, alpha: float = 0.05) -> str:
        """
        Provide plain English interpretation of statistical power.
        
        Args:
            power: Statistical power (0-1)
            alpha: Significance level
            
        Returns:
            Plain English interpretation
        """
        power_pct = power * 100
        
        if power >= 0.8:
            return (
                f"The statistical power is {power_pct:.1f}%, which is good. "
                f"This means there is a {power_pct:.1f}% chance of detecting a true effect "
                f"if it exists. The study has adequate power to detect meaningful differences."
            )
        elif power >= 0.5:
            return (
                f"The statistical power is {power_pct:.1f}%, which is moderate. "
                f"This means there is a {power_pct:.1f}% chance of detecting a true effect. "
                f"Consider increasing sample size for better power (aim for 80% or higher)."
            )
        else:
            return (
                f"The statistical power is {power_pct:.1f}%, which is low. "
                f"This means there is only a {power_pct:.1f}% chance of detecting a true effect. "
                f"The study is likely underpowered and may miss real differences. "
                f"Strongly consider increasing sample size."
            )
    
    @staticmethod
    def interpret_assumptions(assumption_checks: List[AssumptionCheckResult]) -> str:
        """
        Provide plain English summary of assumption checks.
        
        Args:
            assumption_checks: List of assumption check results
            
        Returns:
            Plain English interpretation
        """
        if not assumption_checks:
            return "No assumption checks were performed."
        
        passed = sum(1 for check in assumption_checks if check.passed)
        total = len(assumption_checks)
        
        if passed == total:
            return (
                f"All {total} statistical assumptions were met. "
                f"The test results are reliable and can be interpreted with confidence."
            )
        elif passed == 0:
            return (
                f"None of the {total} statistical assumptions were met. "
                f"The test results may not be reliable. Consider using alternative methods "
                f"or transforming the data."
            )
        else:
            failed_tests = [check.test_name for check in assumption_checks if not check.passed]
            return (
                f"{passed} out of {total} assumptions were met. "
                f"The following assumptions were violated: {', '.join(failed_tests)}. "
                f"Consider using robust alternatives or checking alternative test recommendations."
            )


class VisualizationSuggester:
    """
    Suggests appropriate visualizations for statistical analyses.
    """
    
    @staticmethod
    def suggest_for_descriptive(data_type: str, n_variables: int = 1) -> List[Dict[str, Any]]:
        """
        Suggest visualizations for descriptive statistics.
        
        Args:
            data_type: Type of data (continuous, categorical, etc.)
            n_variables: Number of variables
            
        Returns:
            List of visualization suggestions with descriptions
        """
        suggestions = []
        
        if data_type in ["continuous", "count"]:
            suggestions.extend([
                {
                    "chart_type": "histogram",
                    "description": "Shows the distribution of values and helps identify patterns like skewness or multimodality",
                    "priority": "high"
                },
                {
                    "chart_type": "boxplot",
                    "description": "Displays median, quartiles, and outliers; good for comparing distributions",
                    "priority": "high"
                },
                {
                    "chart_type": "violin_plot",
                    "description": "Combines boxplot with density plot to show full distribution shape",
                    "priority": "medium"
                },
                {
                    "chart_type": "qq_plot",
                    "description": "Assesses normality by comparing data to theoretical normal distribution",
                    "priority": "medium"
                }
            ])
        elif data_type in ["categorical", "binary"]:
            suggestions.extend([
                {
                    "chart_type": "bar_chart",
                    "description": "Shows frequency or proportion of each category",
                    "priority": "high"
                },
                {
                    "chart_type": "pie_chart",
                    "description": "Shows proportions of categories as parts of a whole",
                    "priority": "low"
                }
            ])
        
        return suggestions
    
    @staticmethod
    def suggest_for_comparison(test_type: str, n_groups: int) -> List[Dict[str, Any]]:
        """
        Suggest visualizations for group comparisons.
        
        Args:
            test_type: Type of statistical test
            n_groups: Number of groups being compared
            
        Returns:
            List of visualization suggestions
        """
        suggestions = []
        
        if n_groups == 2:
            suggestions.extend([
                {
                    "chart_type": "boxplot",
                    "description": "Compare distributions of both groups side-by-side",
                    "priority": "high"
                },
                {
                    "chart_type": "violin_plot",
                    "description": "Compare full distribution shapes between groups",
                    "priority": "high"
                },
                {
                    "chart_type": "histogram_overlay",
                    "description": "Overlay histograms to see distribution overlap",
                    "priority": "medium"
                }
            ])
        else:
            suggestions.extend([
                {
                    "chart_type": "boxplot",
                    "description": f"Compare distributions across all {n_groups} groups",
                    "priority": "high"
                },
                {
                    "chart_type": "violin_plot",
                    "description": f"Compare distribution shapes across all {n_groups} groups",
                    "priority": "high"
                },
                {
                    "chart_type": "means_plot",
                    "description": "Show means with confidence intervals for each group",
                    "priority": "medium"
                }
            ])
        
        if "paired" in test_type.lower():
            suggestions.append({
                "chart_type": "paired_plot",
                "description": "Connect before/after measurements for each subject",
                "priority": "high"
            })
        
        return suggestions
    
    @staticmethod
    def suggest_for_correlation(n_variables: int) -> List[Dict[str, Any]]:
        """
        Suggest visualizations for correlation analysis.
        
        Args:
            n_variables: Number of variables
            
        Returns:
            List of visualization suggestions
        """
        suggestions = []
        
        if n_variables == 2:
            suggestions.extend([
                {
                    "chart_type": "scatter_plot",
                    "description": "Shows relationship between two variables with optional trend line",
                    "priority": "high"
                },
                {
                    "chart_type": "hexbin_plot",
                    "description": "Better for large datasets; shows density of points",
                    "priority": "medium"
                }
            ])
        else:
            suggestions.extend([
                {
                    "chart_type": "correlation_matrix",
                    "description": "Heatmap showing correlations between all variable pairs",
                    "priority": "high"
                },
                {
                    "chart_type": "scatter_matrix",
                    "description": "Grid of scatter plots for all variable pairs",
                    "priority": "medium"
                }
            ])
        
        return suggestions
    
    @staticmethod
    def suggest_for_regression(n_predictors: int) -> List[Dict[str, Any]]:
        """
        Suggest visualizations for regression analysis.
        
        Args:
            n_predictors: Number of predictor variables
            
        Returns:
            List of visualization suggestions
        """
        suggestions = [
            {
                "chart_type": "residual_plot",
                "description": "Check for patterns in residuals (should be random)",
                "priority": "high"
            },
            {
                "chart_type": "qq_plot",
                "description": "Check normality of residuals",
                "priority": "high"
            },
            {
                "chart_type": "predicted_vs_actual",
                "description": "Compare predicted values to actual values",
                "priority": "high"
            }
        ]
        
        if n_predictors == 1:
            suggestions.insert(0, {
                "chart_type": "regression_line",
                "description": "Show fitted regression line with data points",
                "priority": "high"
            })
        
        return suggestions
    
    @staticmethod
    def suggest_for_time_series(analysis_type: str) -> List[Dict[str, Any]]:
        """
        Suggest visualizations for time series analysis.
        
        Args:
            analysis_type: Type of time series analysis
            
        Returns:
            List of visualization suggestions
        """
        suggestions = [
            {
                "chart_type": "line_plot",
                "description": "Show time series over time",
                "priority": "high"
            }
        ]
        
        if analysis_type == "decomposition":
            suggestions.extend([
                {
                    "chart_type": "decomposition_plot",
                    "description": "Show trend, seasonal, and residual components separately",
                    "priority": "high"
                },
                {
                    "chart_type": "seasonal_subseries",
                    "description": "Show seasonal patterns across cycles",
                    "priority": "medium"
                }
            ])
        elif analysis_type == "forecasting":
            suggestions.append({
                "chart_type": "forecast_plot",
                "description": "Show historical data with forecast and confidence intervals",
                "priority": "high"
            })
        
        suggestions.extend([
            {
                "chart_type": "acf_plot",
                "description": "Autocorrelation function to identify patterns",
                "priority": "medium"
            },
            {
                "chart_type": "pacf_plot",
                "description": "Partial autocorrelation function for model selection",
                "priority": "medium"
            }
        ])
        
        return suggestions


class ReportGenerator:
    """
    Generates comprehensive analysis reports.
    """
    
    def __init__(self):
        self.interpreter = ResultInterpreter()
        self.viz_suggester = VisualizationSuggester()
    
    def generate_descriptive_report(self, stats: DescriptiveStats) -> str:
        """
        Generate a comprehensive report for descriptive statistics.
        
        Args:
            stats: DescriptiveStats object
            
        Returns:
            Markdown-formatted report
        """
        report = f"# Descriptive Statistics Report: {stats.variable_name}\n\n"
        report += f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Summary\n\n"
        report += f"- **Sample Size:** {stats.n} observations"
        if stats.n_missing > 0:
            report += f" ({stats.n_missing} missing values)"
        report += "\n"
        
        if stats.mean is not None:
            report += f"- **Mean:** {stats.mean:.4f}\n"
            report += f"- **Median:** {stats.median:.4f}\n"
            report += f"- **Standard Deviation:** {stats.std:.4f}\n"
            report += f"- **Range:** {stats.min_value:.4f} to {stats.max_value:.4f}\n\n"
            
            report += "## Distribution Characteristics\n\n"
            
            if stats.skewness is not None:
                if abs(stats.skewness) < 0.5:
                    skew_interp = "approximately symmetric"
                elif stats.skewness > 0.5:
                    skew_interp = "right-skewed (positively skewed)"
                else:
                    skew_interp = "left-skewed (negatively skewed)"
                report += f"- **Skewness:** {stats.skewness:.4f} - The distribution is {skew_interp}\n"
            
            if stats.kurtosis is not None:
                if abs(stats.kurtosis) < 0.5:
                    kurt_interp = "similar to normal distribution"
                elif stats.kurtosis > 0.5:
                    kurt_interp = "heavy-tailed (more outliers than normal)"
                else:
                    kurt_interp = "light-tailed (fewer outliers than normal)"
                report += f"- **Kurtosis:** {stats.kurtosis:.4f} - The distribution is {kurt_interp}\n"
            
            if stats.is_normal is not None:
                report += f"- **Normality Test:** Distribution {'appears' if stats.is_normal else 'does not appear'} normal "
                report += f"(p={stats.normality_p_value:.4f})\n"
            
            report += "\n## Quartiles and Spread\n\n"
            report += f"- **First Quartile (Q1):** {stats.q1:.4f} (25% of data is below this value)\n"
            report += f"- **Third Quartile (Q3):** {stats.q3:.4f} (75% of data is below this value)\n"
            report += f"- **Interquartile Range (IQR):** {stats.iqr:.4f} (middle 50% of data spans this range)\n\n"
            
            if stats.n_outliers > 0:
                report += "## Outliers\n\n"
                report += f"- **Number of Outliers:** {stats.n_outliers} ({stats.n_outliers/stats.n*100:.1f}% of data)\n"
                report += "- Outliers are values that fall more than 1.5 × IQR below Q1 or above Q3\n\n"
        
        else:
            # Categorical data
            report += f"- **Unique Values:** {stats.unique_values}\n"
            if stats.most_common:
                report += f"- **Most Common Value:** {stats.most_common[0][0]} (appears {stats.most_common[0][1]} times)\n\n"
                
                report += "## Frequency Distribution\n\n"
                report += "Top 5 most common values:\n\n"
                for value, count in stats.most_common:
                    pct = count / stats.n * 100
                    report += f"- {value}: {count} ({pct:.1f}%)\n"
        
        report += "\n## Recommended Visualizations\n\n"
        data_type = "continuous" if stats.mean is not None else "categorical"
        viz_suggestions = self.viz_suggester.suggest_for_descriptive(data_type)
        
        for viz in viz_suggestions:
            if viz["priority"] == "high":
                report += f"- **{viz['chart_type']}**: {viz['description']}\n"
        
        return report
    
    def generate_test_report(self, result: StatisticalTestResult) -> str:
        """
        Generate a comprehensive report for a statistical test.
        
        Args:
            result: StatisticalTestResult object
            
        Returns:
            Markdown-formatted report
        """
        report = f"# Statistical Test Report: {result.test_name}\n\n"
        report += f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Test Results\n\n"
        report += f"- **Test Statistic:** {result.statistic:.4f}\n"
        report += f"- **P-value:** {result.p_value:.6f}\n"
        if result.degrees_of_freedom is not None:
            if isinstance(result.degrees_of_freedom, tuple):
                report += f"- **Degrees of Freedom:** {result.degrees_of_freedom[0]}, {result.degrees_of_freedom[1]}\n"
            else:
                report += f"- **Degrees of Freedom:** {result.degrees_of_freedom}\n"
        report += f"- **Sample Size:** {result.sample_size}\n"
        report += f"- **Significance Level:** {result.significance_level}\n"
        report += f"- **Result:** {'**Significant**' if result.is_significant else 'Not Significant'}\n\n"
        
        report += "## Interpretation\n\n"
        report += f"{result.interpretation}\n\n"
        
        report += "### P-value Explanation\n\n"
        report += self.interpreter.interpret_p_value(result.p_value, result.significance_level) + "\n\n"
        
        if result.effect_size is not None:
            report += "## Effect Size\n\n"
            report += f"- **{result.effect_size_name}:** {result.effect_size:.4f} ({result.effect_size_interpretation})\n\n"
            if result.effect_size_name and result.effect_size_interpretation:
                report += self.interpreter.interpret_effect_size(
                    result.effect_size,
                    result.effect_size_name,
                    result.effect_size_interpretation
                ) + "\n\n"
        
        if result.confidence_interval is not None:
            report += "## Confidence Interval\n\n"
            ci_level = 1 - result.significance_level
            report += f"- **{ci_level*100:.0f}% Confidence Interval:** "
            report += f"[{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]\n\n"
            report += self.interpreter.interpret_confidence_interval(
                result.confidence_interval,
                ci_level,
                "difference" if "test" in result.test_name.lower() else "parameter"
            ) + "\n\n"
        
        if result.power is not None:
            report += "## Statistical Power\n\n"
            report += f"- **Power:** {result.power:.4f} ({result.power*100:.1f}%)\n\n"
            report += self.interpreter.interpret_power(result.power, result.significance_level) + "\n\n"
        
        if result.assumption_checks:
            report += "## Assumption Checks\n\n"
            report += self.interpreter.interpret_assumptions(result.assumption_checks) + "\n\n"
            
            report += "### Detailed Assumption Results\n\n"
            for check in result.assumption_checks:
                status = "✓ Passed" if check.passed else "✗ Failed"
                report += f"**{check.test_name}:** {status}\n"
                report += f"- {check.interpretation}\n"
                if check.recommendation:
                    report += f"- Recommendation: {check.recommendation}\n"
                report += "\n"
        
        if result.recommendation:
            report += "## Recommendations\n\n"
            report += f"{result.recommendation}\n\n"
        
        if result.alternative_tests:
            report += "## Alternative Tests\n\n"
            report += "Consider these alternative tests:\n\n"
            for alt_test in result.alternative_tests:
                report += f"- {alt_test}\n"
            report += "\n"
        
        if result.suggested_visualizations:
            report += "## Recommended Visualizations\n\n"
            for viz in result.suggested_visualizations:
                report += f"- {viz}\n"
        
        return report
    
    def generate_correlation_report(self, result: CorrelationResult) -> str:
        """
        Generate a comprehensive report for correlation analysis.
        
        Args:
            result: CorrelationResult object
            
        Returns:
            Markdown-formatted report
        """
        report = "# Correlation Analysis Report\n\n"
        report += f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Variables\n\n"
        report += f"- **Variable 1:** {result.variable1}\n"
        report += f"- **Variable 2:** {result.variable2}\n"
        report += f"- **Sample Size:** {result.n}\n\n"
        
        report += "## Correlation Results\n\n"
        report += f"- **Method:** {result.method.title()} correlation\n"
        report += f"- **Correlation Coefficient:** {result.correlation_coefficient:.4f}\n"
        report += f"- **P-value:** {result.p_value:.6f}\n"
        report += f"- **Result:** {'**Significant**' if result.is_significant else 'Not Significant'}\n\n"
        
        if result.confidence_interval:
            report += f"- **95% Confidence Interval:** [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]\n\n"
        
        report += "## Interpretation\n\n"
        report += f"{result.interpretation}\n\n"
        
        report += f"The correlation is **{result.strength}** and **{result.direction}**. "
        
        if result.is_significant:
            report += "This relationship is statistically significant, meaning it's unlikely to have occurred by chance alone.\n\n"
        else:
            report += f"This relationship is not statistically significant at the {result.significance_level} level.\n\n"
        
        if abs(result.correlation_coefficient) > 0:
            direction_text = "increase" if result.correlation_coefficient > 0 else "decrease"
            report += f"As {result.variable1} increases, {result.variable2} tends to {direction_text}. "
            
            r_squared = result.correlation_coefficient ** 2
            report += f"About {r_squared*100:.1f}% of the variance in one variable can be explained by the other.\n\n"
        
        report += "## Recommended Visualizations\n\n"
        viz_suggestions = self.viz_suggester.suggest_for_correlation(2)
        for viz in viz_suggestions:
            if viz["priority"] == "high":
                report += f"- **{viz['chart_type']}**: {viz['description']}\n"
        
        return report
    
    def generate_regression_report(self, result: RegressionResult) -> str:
        """
        Generate a comprehensive report for regression analysis.
        
        Args:
            result: RegressionResult object
            
        Returns:
            Markdown-formatted report
        """
        report = f"# Regression Analysis Report: {result.model_type}\n\n"
        report += f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "## Model Summary\n\n"
        report += f"- **Model Type:** {result.model_type}\n"
        report += f"- **Sample Size:** {result.n}\n"
        report += f"- **Number of Predictors:** {result.n_features}\n"
        report += f"- **R-squared:** {result.r_squared:.4f} ({result.r_squared*100:.1f}% of variance explained)\n"
        report += f"- **Adjusted R-squared:** {result.adjusted_r_squared:.4f}\n"
        report += f"- **RMSE:** {result.rmse:.4f}\n"
        report += f"- **MAE:** {result.mae:.4f}\n\n"
        
        report += "## Coefficients\n\n"
        report += f"- **Intercept:** {result.intercept:.4f}\n\n"
        
        report += "| Predictor | Coefficient | Effect |\n"
        report += "|-----------|-------------|--------|\n"
        for name, coef in result.coefficients.items():
            effect = "increases" if coef > 0 else "decreases"
            report += f"| {name} | {coef:.4f} | One unit increase {effect} outcome by {abs(coef):.4f} |\n"
        report += "\n"
        
        report += "## Interpretation\n\n"
        report += f"{result.interpretation}\n\n"
        
        r_squared_interp = EffectSizeCalculator.r_squared_interpretation(result.r_squared)
        report += f"The model has a **{r_squared_interp}** fit, explaining {result.r_squared*100:.1f}% "
        report += "of the variance in the outcome variable. "
        
        if result.r_squared >= 0.7:
            report += "This is considered a strong model.\n\n"
        elif result.r_squared >= 0.5:
            report += "This is considered a moderate model.\n\n"
        elif result.r_squared >= 0.3:
            report += "This is considered a weak model. Consider adding more predictors or trying non-linear models.\n\n"
        else:
            report += "This is considered a very weak model. The current predictors have limited explanatory power.\n\n"
        
        if result.assumption_checks:
            report += "## Assumption Checks\n\n"
            report += self.interpreter.interpret_assumptions(result.assumption_checks) + "\n\n"
            
            for check in result.assumption_checks:
                status = "✓ Passed" if check.passed else "✗ Failed"
                report += f"**{check.test_name}:** {status}\n"
                report += f"- {check.interpretation}\n\n"
        
        if result.vif_values:
            report += "## Multicollinearity Check (VIF)\n\n"
            report += "| Predictor | VIF | Assessment |\n"
            report += "|-----------|-----|------------|\n"
            for name, vif in result.vif_values.items():
                if vif > 10:
                    assessment = "⚠️ High multicollinearity"
                elif vif > 5:
                    assessment = "⚠️ Moderate multicollinearity"
                else:
                    assessment = "✓ No multicollinearity"
                report += f"| {name} | {vif:.2f} | {assessment} |\n"
            report += "\n"
        
        if result.recommendations:
            report += "## Recommendations\n\n"
            for rec in result.recommendations:
                report += f"- {rec}\n"
            report += "\n"
        
        report += "## Recommended Visualizations\n\n"
        viz_suggestions = self.viz_suggester.suggest_for_regression(result.n_features)
        for viz in viz_suggestions:
            if viz["priority"] == "high":
                report += f"- **{viz['chart_type']}**: {viz['description']}\n"
        
        return report


# Utility class for effect size calculation
class EffectSizeCalculator:
    """Effect size calculation utilities."""
    
    @staticmethod
    def r_squared_interpretation(r_squared: float) -> str:
        """Interpret R-squared value."""
        if r_squared < 0.10:
            return "negligible"
        elif r_squared < 0.30:
            return "small"
        elif r_squared < 0.50:
            return "moderate"
        else:
            return "large"
