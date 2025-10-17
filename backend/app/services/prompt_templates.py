"""
Prompt Templates for AI Code Generation
Templates for different types of data analysis tasks
"""
from typing import Dict, List, Optional
from enum import Enum


class AnalysisType(Enum):
    """Types of data analysis"""
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


class PromptTemplates:
    """Templates for generating analysis code"""
    
    SYSTEM_PROMPT = """You are a friendly, expert Python data scientist who loves explaining things in plain English while providing rigorous analytical insights.

Think of yourself as a helpful colleague who:
- Explains complex concepts in simple, conversational language
- Provides both intuitive understanding AND technical precision
- Shares insights about what the data reveals, not just what the code does
- Uses analogies and real-world examples when helpful
- Maintains professional expertise while being approachable and warm

RESPONSE FORMAT - HYBRID APPROACH:
1. Start with a brief, conversational explanation (2-3 sentences in plain English about what you're doing and why)
2. Then provide the Python code
3. End with analytical insights (what the results mean, patterns you notice, recommendations)

Example structure:
"Let me help you explore the relationship between these variables. I'll create a correlation analysis that shows how strongly different columns are connected to each other.

[Python code here]

From this analysis, you'll be able to see which variables move together. Strong correlations (close to 1 or -1) suggest meaningful relationships worth investigating further."

TECHNICAL EXPERTISE:
You have 20+ years of experience with pandas, numpy, scipy, scikit-learn, statsmodels, matplotlib, and seaborn.

CRITICAL: For ALL visualizations, use ONLY matplotlib (plt) and seaborn (sns). NEVER use plotly, bokeh, or any interactive plotting libraries.

Your code is:
- PRODUCTION-READY: Handles edge cases, validates inputs, includes comprehensive error handling
- OPTIMIZED: Uses vectorized operations, efficient algorithms, minimal memory footprint
- ACCURATE: Mathematically correct, statistically sound, numerically stable
- ROBUST: Works with missing data, outliers, mixed types, large datasets
- CLEAR: Self-documenting with meaningful variable names and strategic comments

CRITICAL RULES (100% COMPLIANCE REQUIRED):
1. ALWAYS provide conversational context before and after code - explain in plain English
2. The dataframe 'df' is ALREADY LOADED - DO NOT use pd.read_csv() or any file reading operations
3. ALWAYS validate data before operations (check nulls, types, ranges)
4. Use try-except blocks for operations that might fail
5. Handle edge cases: empty dataframes, single row/column, all nulls, infinite values
6. Use appropriate statistical methods (check assumptions, use correct tests)
7. For numerical operations: check for division by zero, log of negative, sqrt of negative
8. Dataframe is ALWAYS named 'df' - never reassign this variable
9. Store ALL results in clearly named variables (result, summary, fig, etc.)
10. For visualizations: create figure objects, set titles/labels, use appropriate scales
11. Add inline comments explaining WHY, not what (code shows what)
12. After code, provide insights in conversational language about what the results reveal

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
    print(f"Error: {{str(e)}}")

REMEMBER: Your code will be executed in production. Lives may depend on accuracy. Triple-check logic.
"""

    DATA_CONTEXT_TEMPLATE = """
DATASET INFORMATION:
- Filename: {filename}
- Rows: {rows}
- Columns: {columns}
- Column Names: {column_names}
- Data Types: {dtypes}
- Missing Values: {missing_values}
- Sample Data:
{sample_data}

STATISTICAL SUMMARY:
{statistical_summary}
"""

    EXPLORATORY_TEMPLATE = """Let's dive into your data and discover what stories it has to tell! I'll perform a comprehensive exploratory analysis to help you understand the structure, patterns, and potential issues in your dataset.

Think of this as getting to know your data - we'll look at its shape, check for any missing pieces, understand the distribution of values, and spot any unusual patterns or outliers.

ANALYSIS COMPONENTS:
1. **Data Overview** - Understanding the basics: how many rows and columns, what types of data we have
2. **Missing Data Check** - Finding any gaps in the data and understanding their patterns
3. **Numerical Analysis** - Exploring statistics, distributions, and outliers in numeric columns
4. **Categorical Analysis** - Understanding categories and their frequencies
5. **Correlation Insights** - Discovering relationships between different variables
6. **Data Quality** - Identifying any potential issues that might affect analysis

User Request: {user_query}

Generate production-ready code with validation and error handling. Remember to explain what you find in plain English!"""

    STATISTICAL_TEMPLATE = """Let me help you perform a rigorous statistical analysis! I'll walk you through the process step-by-step, making sure we check all the assumptions and use the right tests for your data.

Think of statistical testing as asking questions about your data with mathematical precision. We'll validate our approach, check if the data meets the requirements, and interpret the results in a way that makes sense for real-world decisions.

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

    VISUALIZATION_TEMPLATE = """Let me create some beautiful visualizations to help you see the patterns in your data! I'll choose the best chart types and make sure everything is clear and easy to understand.

Think of visualizations as telling a story with your data - we want to make insights jump out at you while keeping everything accurate and professional.

VISUALIZATION APPROACH:
1. **Choose the right chart** - Match the visualization type to your data and question
2. **Make it clear** - Add descriptive titles, labels, and legends
3. **Use color wisely** - Apply colorblind-friendly palettes that highlight key patterns
4. **Polish it** - Create publication-ready plots with proper formatting

IMPORTANT: I'll use matplotlib and seaborn to create static visualizations that are perfect for reports and presentations.

User Request: {user_query}

I'll explain what the visualization reveals and what patterns to look for!"""

    CLEANING_TEMPLATE = """Let me help you clean up your data and get it ready for analysis! Data cleaning is like tidying up before guests arrive - we want everything in its right place and looking good.

I'll tackle common issues like missing values, duplicates, and inconsistent formatting. Think of this as giving your data a fresh start so you can trust your analysis results.

CLEANING STEPS:
1. **Handle missing values** - Fill gaps or remove them strategically
2. **Remove duplicates** - Keep your data unique and accurate
3. **Fix data types** - Make sure numbers are numbers and dates are dates
4. **Deal with outliers** - Identify unusual values that might skew results
5. **Standardize formats** - Ensure consistency across your dataset

User Request: {user_query}

I'll explain what I'm cleaning and why each step matters for your analysis!"""

    TRANSFORMATION_TEMPLATE = """Let me help you transform your data into exactly the format you need! Data transformation is like reshaping clay - we're molding your data into the perfect form for your specific analysis.

Whether you need to create new features, reshape your data, or prepare it for machine learning, I'll guide you through each transformation and explain why it's useful.

TRANSFORMATION OPTIONS:
1. **Feature engineering** - Create new, more informative columns from existing data
2. **Aggregation** - Summarize data at different levels
3. **Reshaping** - Pivot or melt data into different structures
4. **Encoding** - Convert categories into numbers for analysis
5. **Scaling** - Normalize values to comparable ranges

User Request: {user_query}

I'll explain how each transformation enhances your data and what new insights it enables!"""

    PREDICTION_TEMPLATE = """Generate Python code for predictive modeling.

Include:
1. Feature selection
2. Train-test split
3. Model training (appropriate algorithm)
4. Model evaluation
5. Predictions
6. Performance metrics

Use scikit-learn for modeling.

User Request: {user_query}

Return executable Python code with clear comments."""

    CORRELATION_TEMPLATE = """Let me help you discover how different variables in your data relate to each other! Correlation analysis is like finding which friends tend to hang out together - we're looking for variables that move in sync.

I'll create visualizations and statistics that show you both the strength and direction of relationships in your data. This is super useful for understanding what drives what in your dataset.

CORRELATION ANALYSIS:
1. **Calculate correlations** - Measure how strongly variables are related
2. **Visualize patterns** - Create heatmaps that make relationships obvious
3. **Identify key relationships** - Highlight the strongest connections
4. **Explore details** - Scatter plots for interesting pairs
5. **Test significance** - Determine if relationships are real or just chance

User Request: {user_query}

I'll point out the most interesting relationships and what they might mean for your analysis!"""

    AGGREGATION_TEMPLATE = """Generate Python code to aggregate and summarize data.

Include:
1. Group by operations
2. Aggregate functions (sum, mean, count, etc.)
3. Multi-level aggregations
4. Pivot tables
5. Summary statistics by group

User Request: {user_query}

Return executable Python code with clear comments."""

    TIME_SERIES_TEMPLATE = """Generate Python code for time series analysis.

Include:
1. Parse datetime columns
2. Set datetime index
3. Resample data
4. Calculate rolling statistics
5. Trend analysis
6. Seasonality detection
7. Time series visualization

User Request: {user_query}

Return executable Python code with clear comments."""

    CUSTOM_TEMPLATE = """Generate Python code for the following data analysis task.

User Request: {user_query}

Return executable Python code with clear comments."""

    FOLLOW_UP_TEMPLATE = """Based on the previous conversation and analysis:

Previous Context:
{conversation_history}

Previous Code Generated:
{previous_code}

Previous Results:
{previous_results}

New User Request: {user_query}

Generate Python code that builds upon the previous analysis. Reference previous variables and results."""

    @classmethod
    def get_template(cls, analysis_type: AnalysisType) -> str:
        """
        Get prompt template for analysis type
        
        Args:
            analysis_type: Type of analysis
            
        Returns:
            Prompt template string
        """
        templates = {
            AnalysisType.EXPLORATORY: cls.EXPLORATORY_TEMPLATE,
            AnalysisType.STATISTICAL: cls.STATISTICAL_TEMPLATE,
            AnalysisType.VISUALIZATION: cls.VISUALIZATION_TEMPLATE,
            AnalysisType.CLEANING: cls.CLEANING_TEMPLATE,
            AnalysisType.TRANSFORMATION: cls.TRANSFORMATION_TEMPLATE,
            AnalysisType.PREDICTION: cls.PREDICTION_TEMPLATE,
            AnalysisType.CORRELATION: cls.CORRELATION_TEMPLATE,
            AnalysisType.AGGREGATION: cls.AGGREGATION_TEMPLATE,
            AnalysisType.TIME_SERIES: cls.TIME_SERIES_TEMPLATE,
            AnalysisType.CUSTOM: cls.CUSTOM_TEMPLATE
        }
        return templates.get(analysis_type, cls.CUSTOM_TEMPLATE)
    
    @classmethod
    def build_data_context(
        cls,
        filename: str,
        rows: int,
        columns: int,
        column_names: List[str],
        dtypes: Dict[str, str],
        missing_values: Dict[str, int],
        sample_data: str,
        statistical_summary: str
    ) -> str:
        """
        Build data context string
        
        Args:
            filename: Name of the data file
            rows: Number of rows
            columns: Number of columns
            column_names: List of column names
            dtypes: Dictionary of column data types
            missing_values: Dictionary of missing value counts
            sample_data: String representation of sample data
            statistical_summary: Statistical summary string
            
        Returns:
            Formatted data context string
        """
        return cls.DATA_CONTEXT_TEMPLATE.format(
            filename=filename,
            rows=rows,
            columns=columns,
            column_names=", ".join(column_names),
            dtypes="\n".join([f"  - {col}: {dtype}" for col, dtype in dtypes.items()]),
            missing_values="\n".join([f"  - {col}: {count}" for col, count in missing_values.items()]) or "  None",
            sample_data=sample_data,
            statistical_summary=statistical_summary
        )
    
    @staticmethod
    def _sanitize_input(text: Optional[str]) -> Optional[str]:
        """
        Sanitize user-provided strings to prevent format-string injection by escaping braces
        and removing non-printable characters; also enforce a reasonable maximum length.
        """
        if text is None:
            return None
        # Escape braces so that str.format cannot interpret user input as format fields
        sanitized = text.replace("{", "{{").replace("}", "}}")
        # Remove non-printable/control characters to avoid malformed prompts
        sanitized = "".join(ch for ch in sanitized if ch.isprintable())
        # Limit length to avoid excessively large inputs
        max_len = 10000
        if len(sanitized) > max_len:
            return sanitized[:max_len] + "..."
        return sanitized

    @classmethod
    def build_prompt(
        cls,
        analysis_type: AnalysisType,
        user_query: str,
        data_context: Optional[str] = None,
        conversation_history: Optional[str] = None,
        previous_code: Optional[str] = None,
        previous_results: Optional[str] = None
    ) -> str:
        """
        Build complete prompt for code generation
        
        Args:
            analysis_type: Type of analysis
            user_query: User's natural language query
            data_context: Optional data context information
            conversation_history: Optional conversation history
            previous_code: Optional previously generated code
            previous_results: Optional previous results
            
        Returns:
            Complete prompt string
        """
        template = cls.get_template(analysis_type)

        # Sanitize inputs used in formatting to prevent format-string injection
        safe_user_query = cls._sanitize_input(user_query) or ""
        safe_data_context = cls._sanitize_input(data_context)
        safe_conversation_history = cls._sanitize_input(conversation_history)
        safe_previous_code = cls._sanitize_input(previous_code)
        safe_previous_results = cls._sanitize_input(previous_results)

        # Build prompt parts
        parts = []

        if safe_data_context:
            parts.append(safe_data_context)

        if safe_conversation_history and safe_previous_code:
            # This is a follow-up query
            template = cls.FOLLOW_UP_TEMPLATE
            prompt = template.format(
                conversation_history=safe_conversation_history,
                previous_code=safe_previous_code,
                previous_results=safe_previous_results or "No results available",
                user_query=safe_user_query
            )
        else:
            # First query
            prompt = template.format(user_query=safe_user_query)

        parts.append(prompt)

        return "\n\n".join(parts)
    
    @classmethod
    def detect_analysis_type(cls, user_query: str) -> AnalysisType:
        """
        Detect analysis type from user query
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Detected AnalysisType
        """
        query_lower = user_query.lower()
        
        # Keywords for each analysis type
        keywords = {
            AnalysisType.EXPLORATORY: ["explore", "overview", "summary", "describe", "eda"],
            AnalysisType.STATISTICAL: ["test", "hypothesis", "significance", "p-value", "distribution"],
            AnalysisType.VISUALIZATION: ["plot", "chart", "graph", "visualize", "show", "display"],
            AnalysisType.CLEANING: ["clean", "missing", "duplicates", "outliers", "preprocess"],
            AnalysisType.TRANSFORMATION: ["transform", "encode", "normalize", "scale", "feature"],
            AnalysisType.PREDICTION: ["predict", "model", "forecast", "machine learning", "classify"],
            AnalysisType.CORRELATION: ["correlation", "relationship", "correlate", "association"],
            AnalysisType.AGGREGATION: ["group", "aggregate", "sum", "average", "count by"],
            AnalysisType.TIME_SERIES: ["time series", "trend", "seasonal", "temporal", "over time"]
        }
        
        # Check for keyword matches
        for analysis_type, words in keywords.items():
            if any(word in query_lower for word in words):
                return analysis_type
        
        # Default to custom
        return AnalysisType.CUSTOM
