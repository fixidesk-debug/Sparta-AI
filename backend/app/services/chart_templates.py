"""
Chart Templates - Pre-built Visualization Templates
Library of chart templates for common analysis patterns
"""
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class ChartTemplates:
    """Pre-built chart templates"""
    
    TEMPLATES = {
        "distribution": {
            "name": "Distribution Analysis",
            "description": "Histogram with KDE overlay",
            "use_case": "Understand data distribution"
        },
        "comparison": {
            "name": "Category Comparison",
            "description": "Bar chart with error bars",
            "use_case": "Compare values across categories"
        },
        "trend": {
            "name": "Trend Analysis",
            "description": "Line chart with moving average",
            "use_case": "Analyze trends over time"
        },
        "correlation": {
            "name": "Correlation Matrix",
            "description": "Heatmap of correlations",
            "use_case": "Find relationships between variables"
        },
        "scatter": {
            "name": "Scatter with Regression",
            "description": "Scatter plot with trend line",
            "use_case": "Analyze relationship between two variables"
        },
        "box": {
            "name": "Box Plot Comparison",
            "description": "Box plots for distribution comparison",
            "use_case": "Compare distributions across groups"
        },
        "pie": {
            "name": "Composition Analysis",
            "description": "Pie chart with percentages",
            "use_case": "Show part-to-whole relationships"
        },
        "funnel": {
            "name": "Funnel Analysis",
            "description": "Funnel chart for conversion",
            "use_case": "Analyze conversion or process flow"
        }
    }
    
    @staticmethod
    def create_distribution_chart(df: pd.DataFrame, column: str) -> go.Figure:
        """Create distribution chart"""
        fig = px.histogram(
            df, x=column,
            marginal="box",
            title=f"Distribution of {column}",
            template="plotly_white"
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title=column,
            yaxis_title="Count"
        )
        return fig
    
    @staticmethod
    def create_comparison_chart(df: pd.DataFrame, category: str, value: str) -> go.Figure:
        """Create comparison bar chart"""
        fig = px.bar(
            df, x=category, y=value,
            title=f"{value} by {category}",
            template="plotly_white",
            color=value,
            color_continuous_scale="Blues"
        )
        fig.update_layout(
            xaxis_title=category,
            yaxis_title=value
        )
        return fig
    
    @staticmethod
    def create_trend_chart(df: pd.DataFrame, x: str, y: str) -> go.Figure:
        """Create trend line chart"""
        fig = px.line(
            df, x=x, y=y,
            title=f"{y} Trend Over {x}",
            template="plotly_white",
            markers=True
        )
        
        # Add moving average
        if len(df) > 7:
            df['ma'] = df[y].rolling(window=7).mean()
            fig.add_scatter(
                x=df[x], y=df['ma'],
                mode='lines',
                name='7-day MA',
                line=dict(dash='dash', color='red')
            )
        
        fig.update_layout(
            xaxis_title=x,
            yaxis_title=y
        )
        return fig
    
    @staticmethod
    def create_correlation_chart(df: pd.DataFrame) -> go.Figure:
        """Create correlation heatmap"""
        numeric_df = df.select_dtypes(include=['number'])
        corr = numeric_df.corr()
        
        fig = px.imshow(
            corr,
            title="Correlation Matrix",
            template="plotly_white",
            color_continuous_scale="RdBu",
            aspect="auto",
            text_auto=".2f"
        )
        return fig
    
    @staticmethod
    def create_scatter_chart(df: pd.DataFrame, x: str, y: str, color: str = None) -> go.Figure:
        """Create scatter plot with regression"""
        fig = px.scatter(
            df, x=x, y=y, color=color,
            title=f"{y} vs {x}",
            template="plotly_white",
            trendline="ols"
        )
        fig.update_layout(
            xaxis_title=x,
            yaxis_title=y
        )
        return fig
    
    @staticmethod
    def create_box_chart(df: pd.DataFrame, category: str, value: str) -> go.Figure:
        """Create box plot"""
        fig = px.box(
            df, x=category, y=value,
            title=f"{value} Distribution by {category}",
            template="plotly_white",
            color=category
        )
        fig.update_layout(
            xaxis_title=category,
            yaxis_title=value
        )
        return fig
    
    @staticmethod
    def create_pie_chart(df: pd.DataFrame, names: str, values: str) -> go.Figure:
        """Create pie chart"""
        fig = px.pie(
            df, names=names, values=values,
            title=f"{values} by {names}",
            template="plotly_white",
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    @staticmethod
    def get_template_suggestions(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Suggest appropriate templates based on data"""
        suggestions = []
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Distribution for numeric columns
        for col in numeric_cols[:3]:
            suggestions.append({
                "template": "distribution",
                "params": {"column": col},
                "reason": f"Analyze distribution of {col}"
            })
        
        # Comparison if we have categorical and numeric
        if categorical_cols and numeric_cols:
            suggestions.append({
                "template": "comparison",
                "params": {"category": categorical_cols[0], "value": numeric_cols[0]},
                "reason": f"Compare {numeric_cols[0]} across {categorical_cols[0]}"
            })
        
        # Correlation if multiple numeric columns
        if len(numeric_cols) >= 2:
            suggestions.append({
                "template": "correlation",
                "params": {},
                "reason": "Explore relationships between numeric variables"
            })
        
        # Scatter for pairs of numeric columns
        if len(numeric_cols) >= 2:
            suggestions.append({
                "template": "scatter",
                "params": {"x": numeric_cols[0], "y": numeric_cols[1]},
                "reason": f"Analyze relationship between {numeric_cols[0]} and {numeric_cols[1]}"
            })
        
        return suggestions
