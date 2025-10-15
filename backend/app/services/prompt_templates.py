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
    
    SYSTEM_PROMPT = """You are an expert Python data analyst specializing in pandas, numpy, matplotlib, seaborn, and plotly.
Your task is to generate clean, efficient, and well-documented Python code for data analysis tasks.

IMPORTANT RULES:
1. Generate ONLY executable Python code with comments
2. Use pandas for data manipulation
3. Use matplotlib, seaborn, or plotly for visualizations
4. Include error handling for common issues
5. Add descriptive variable names
6. Include docstrings for complex operations
7. Never include markdown code fences (```) in your response
8. Always assume the dataframe is named 'df'
9. Store results in variables that can be easily accessed
10. For visualizations, save to files or return figure objects

SECURITY:
- Never use eval(), exec(), or __import__()
- No file system operations except reading the provided data
- No network operations
- No subprocess or os.system calls
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

    EXPLORATORY_TEMPLATE = """Generate Python code to perform exploratory data analysis on the dataset.

Include:
1. Basic dataset information (shape, dtypes, memory usage)
2. Statistical summary for numerical columns
3. Missing value analysis
4. Distribution analysis for key columns
5. Outlier detection
6. Correlation analysis (if applicable)

User Request: {user_query}

Return executable Python code with clear comments."""

    STATISTICAL_TEMPLATE = """Generate Python code to perform statistical analysis on the dataset.

Include:
1. Descriptive statistics
2. Hypothesis testing (if applicable)
3. Confidence intervals
4. Statistical tests (t-test, chi-square, ANOVA, etc.)
5. Effect size calculations

User Request: {user_query}

Return executable Python code with clear comments."""

    VISUALIZATION_TEMPLATE = """Generate Python code to create data visualizations.

Requirements:
1. Use appropriate chart types for the data
2. Add titles, labels, and legends
3. Use color schemes effectively
4. Make plots publication-ready
5. Save figures to variables for display

Available libraries: matplotlib, seaborn, plotly

User Request: {user_query}

Return executable Python code with clear comments."""

    CLEANING_TEMPLATE = """Generate Python code to clean and preprocess the dataset.

Include:
1. Handle missing values (appropriate strategy)
2. Remove duplicates
3. Fix data types
4. Handle outliers (if needed)
5. Standardize/normalize columns (if needed)
6. Create cleaned dataframe

User Request: {user_query}

Return executable Python code with clear comments."""

    TRANSFORMATION_TEMPLATE = """Generate Python code to transform the dataset.

Include:
1. Feature engineering
2. Data aggregation
3. Pivoting/reshaping
4. Encoding categorical variables
5. Scaling/normalization
6. Creating derived columns

User Request: {user_query}

Return executable Python code with clear comments."""

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

    CORRELATION_TEMPLATE = """Generate Python code to analyze correlations in the dataset.

Include:
1. Correlation matrix calculation
2. Correlation heatmap visualization
3. Identify strong correlations
4. Scatter plots for key relationships
5. Statistical significance testing

User Request: {user_query}

Return executable Python code with clear comments."""

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
        
        # Build prompt parts
        parts = []
        
        if data_context:
            parts.append(data_context)
        
        if conversation_history and previous_code:
            # This is a follow-up query
            template = cls.FOLLOW_UP_TEMPLATE
            prompt = template.format(
                conversation_history=conversation_history,
                previous_code=previous_code,
                previous_results=previous_results or "No results available",
                user_query=user_query
            )
        else:
            # First query
            prompt = template.format(user_query=user_query)
        
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
