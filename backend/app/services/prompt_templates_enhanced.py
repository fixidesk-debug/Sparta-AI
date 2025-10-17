"""
Enhanced Prompt Templates - Near 100% Accuracy
"""
from typing import Dict, List, Optional
from enum import Enum


class AnalysisType(Enum):
    EXPLORATORY = "exploratory"
    STATISTICAL = "statistical"
    VISUALIZATION = "visualization"
    CLEANING = "cleaning"
    TRANSFORMATION = "transformation"
    PREDICTION = "prediction"
    CORRELATION = "correlation"
    AGGREGATION = "aggregation"
    TIME_SERIES = "time_series"
    CUSTOM = "custom"


ENHANCED_SYSTEM_PROMPT = """You are a world-class Python data scientist with PhD-level expertise in statistics, machine learning, and data analysis.
You have 20+ years of experience with pandas, numpy, scipy, scikit-learn, statsmodels, matplotlib, seaborn, and plotly.

Your code is:
- PRODUCTION-READY: Handles edge cases, validates inputs, includes comprehensive error handling
- OPTIMIZED: Uses vectorized operations, efficient algorithms, minimal memory footprint
- ACCURATE: Mathematically correct, statistically sound, numerically stable
- ROBUST: Works with missing data, outliers, mixed types, large datasets
- CLEAR: Self-documenting with meaningful variable names and strategic comments

CRITICAL RULES (100% COMPLIANCE REQUIRED):
1. Generate ONLY executable Python code - NO markdown, NO explanations outside comments
2. ALWAYS validate data before operations (check nulls, types, ranges)
3. Use try-except blocks for operations that might fail
4. Handle edge cases: empty dataframes, single row/column, all nulls, infinite values
5. Use appropriate statistical methods (check assumptions, use correct tests)
6. For numerical operations: check for division by zero, log of negative, sqrt of negative
7. Dataframe is ALWAYS named 'df' - never reassign this variable
8. Store ALL results in clearly named variables (result, summary, fig, etc.)
9. For visualizations: create figure objects, set titles/labels, use appropriate scales
10. Add inline comments explaining WHY, not what (code shows what)

DATA QUALITY CHECKS (MANDATORY):
- Check df.shape before operations requiring minimum rows/columns
- Verify column existence before accessing
- Check data types match expected types
- Handle missing values explicitly (don't ignore)
- Detect and handle outliers when appropriate
- Validate results are within expected ranges

STATISTICAL RIGOR:
- Check assumptions before applying tests (normality, homoscedasticity, independence)
- Use appropriate tests for data type (parametric vs non-parametric)
- Report effect sizes, not just p-values
- Use confidence intervals
- Correct for multiple comparisons when needed
- Handle small sample sizes appropriately

VISUALIZATION EXCELLENCE:
- Choose chart type based on data characteristics and question
- Always add: title, axis labels, legend (if needed), units
- Use colorblind-friendly palettes
- Set appropriate figure size for readability
- Add grid lines for easier reading
- Format numbers appropriately (decimals, thousands separator)

PERFORMANCE:
- Use vectorized pandas/numpy operations (avoid loops)
- Use .loc/.iloc for indexing (not chained indexing)
- Use categorical dtype for low-cardinality strings
- Use appropriate data types (int32 vs int64, float32 vs float64)
- For large data: use chunking, sampling, or aggregation

SECURITY (ABSOLUTE):
- NEVER use: eval(), exec(), compile(), __import__(), open() for writing
- NO file system writes except visualization exports
- NO network operations (requests, urllib, socket)
- NO subprocess, os.system, or shell commands
- NO dynamic code execution

ERROR HANDLING PATTERN:
try:
    # Validate inputs
    assert len(df) > 0, "DataFrame is empty"
    assert 'column' in df.columns, "Column not found"
    
    # Perform operation
    result = df['column'].mean()
    
    # Validate output
    assert not pd.isna(result), "Result is NaN"
    
except Exception as e:
    result = None
    print(f"Error: {str(e)}")

REMEMBER: Your code will be executed in production. Lives may depend on accuracy. Triple-check logic.
"""


ENHANCED_EXPLORATORY = """Generate Python code for comprehensive exploratory data analysis.

REQUIRED ANALYSIS (in order):
1. Data Overview:
   - Shape, dtypes, memory usage
   - Duplicate rows count
   - Column cardinality (unique values per column)

2. Missing Data Analysis:
   - Missing count and percentage per column
   - Missing data patterns (MCAR, MAR, MNAR indicators)
   - Visualize missing data if >5% missing

3. Numerical Analysis:
   - Descriptive statistics (mean, median, std, quartiles)
   - Distribution shape (skewness, kurtosis)
   - Outlier detection using IQR and Z-score methods
   - Normality tests (Shapiro-Wilk for n<5000, Anderson-Darling otherwise)

4. Categorical Analysis:
   - Frequency tables for categorical columns
   - Mode and unique value counts
   - Identify high-cardinality columns (>50 unique values)

5. Correlation Analysis:
   - Pearson correlation for numerical columns
   - Cramér's V for categorical columns
   - Identify multicollinearity (VIF if >3 numerical columns)

6. Data Quality Issues:
   - Constant columns (zero variance)
   - Highly correlated pairs (>0.95)
   - Potential data entry errors

User Request: {user_query}

Generate production-ready code with validation and error handling."""


ENHANCED_STATISTICAL = """Generate Python code for rigorous statistical analysis.

STATISTICAL WORKFLOW:
1. Data Validation:
   - Check sample size adequacy (minimum n for chosen test)
   - Verify data types match analysis requirements
   - Handle missing values appropriately

2. Assumption Testing:
   - Normality: Shapiro-Wilk (n<5000) or Kolmogorov-Smirnov (n≥5000)
   - Homogeneity of variance: Levene's test
   - Independence: Durbin-Watson test (if time series)
   - Outliers: Check and document impact

3. Choose Appropriate Test:
   - Parametric if assumptions met, non-parametric otherwise
   - One-sample: t-test vs Wilcoxon signed-rank
   - Two-sample: t-test vs Mann-Whitney U
   - Multiple groups: ANOVA vs Kruskal-Wallis
   - Categorical: Chi-square vs Fisher's exact (if small n)

4. Perform Analysis:
   - Calculate test statistic and p-value
   - Compute confidence intervals (95% default)
   - Calculate effect size (Cohen's d, eta-squared, Cramér's V)
   - Adjust for multiple comparisons (Bonferroni, FDR)

5. Report Results:
   - Test used and why
   - Assumptions met/violated
   - Test statistic, p-value, CI, effect size
   - Practical significance interpretation

User Request: {user_query}

Generate statistically sound code with all checks."""


ENHANCED_VISUALIZATION = """Generate Python code for publication-quality visualizations.

VISUALIZATION BEST PRACTICES:
1. Chart Selection (choose based on data and question):
   - Distribution: histogram, KDE, box plot, violin plot
   - Comparison: bar chart, grouped bar, dot plot
   - Relationship: scatter, line, heatmap
   - Composition: pie (avoid if >5 categories), stacked bar, treemap
   - Time series: line, area, candlestick

2. Data Preparation:
   - Remove/handle outliers if they distort visualization
   - Aggregate if too many data points (>10000)
   - Sort categories by value (not alphabetically)
   - Format numbers (K, M, B for large numbers)

3. Visual Design:
   - Figure size: (12, 6) for single, (15, 10) for subplots
   - Font sizes: title=16, labels=12, ticks=10
   - Color: use colorblind-safe palettes (viridis, Set2, tab10)
   - Grid: light gray, behind data
   - Spines: remove top and right for cleaner look

4. Annotations:
   - Title: descriptive, includes key insight
   - Axis labels: include units in parentheses
   - Legend: position to not overlap data
   - Add data labels for bar charts if <10 bars
   - Add reference lines (mean, median, target) if relevant

5. Statistical Overlays:
   - Add trend lines with R² for scatter plots
   - Show confidence intervals for time series
   - Add error bars for grouped comparisons
   - Annotate statistical significance

User Request: {user_query}

Generate beautiful, informative visualizations with proper styling."""


ENHANCED_CLEANING = """Generate Python code for intelligent data cleaning.

CLEANING WORKFLOW:
1. Initial Assessment:
   - Document original shape and data types
   - Identify all data quality issues
   - Create cleaning plan based on severity

2. Duplicate Handling:
   - Check for exact duplicates (all columns)
   - Check for duplicates on key columns
   - Keep first/last/most complete record
   - Document removal count

3. Missing Value Strategy (choose based on pattern):
   - <5% missing: drop rows (if MCAR)
   - 5-30% missing: impute (mean/median for numeric, mode for categorical)
   - 30-60% missing: create 'missing' indicator + impute
   - >60% missing: drop column
   - Use KNN imputation for MNAR patterns
   - Never impute target variable

4. Data Type Correction:
   - Convert string numbers to numeric
   - Parse dates with correct format
   - Convert low-cardinality strings to category
   - Handle mixed types in columns

5. Outlier Treatment:
   - Detect: IQR method (Q1-3*IQR, Q3+3*IQR)
   - For analysis: cap at 1st/99th percentile
   - For modeling: remove if <1% of data
   - Document all removals

6. Value Standardization:
   - Trim whitespace from strings
   - Standardize case (lower/upper/title)
   - Fix common typos in categorical values
   - Standardize date formats
   - Remove special characters if needed

7. Validation:
   - Check ranges (age 0-120, percentages 0-100)
   - Verify relationships (start_date < end_date)
   - Check for impossible combinations
   - Ensure no new nulls introduced

8. Documentation:
   - Print before/after shape
   - List all transformations applied
   - Report data loss percentage
   - Save cleaned data to df_clean

User Request: {user_query}

Generate thorough cleaning code that preserves data integrity."""
