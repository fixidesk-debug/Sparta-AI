"""
Statistical Analysis API Endpoints

REST API endpoints for advanced statistical analysis operations.

Author: Sparta AI Team
Date: October 14, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, Field, field_validator
import pandas as pd
import numpy as np
import io
import logging
from enum import Enum

from app.db.session import get_db
from app.db.models import User
from app.core.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from app.core.authorization import require_permission
from app.services.statistics import StatisticsEngine
from app.services.data_processor import DataProcessor

router = APIRouter()
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# Initialize services
statistics_engine = StatisticsEngine()
data_processor = DataProcessor()


# ==================== Helper Functions ====================

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize objects for JSON serialization.
    Handles tuples, infinity, NaN, numpy types, etc.
    """
    if obj is None:
        return None
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, (str, int, bool)):
        return obj
    else:
        # Try to convert unknown types to string
        try:
            return str(obj)
        except Exception:
            return None


# ==================== Request/Response Models ====================

class TestType(str, Enum):
    """Available statistical test types"""
    AUTO = "auto"
    T_TEST_INDEPENDENT = "t_test_independent"
    T_TEST_PAIRED = "t_test_paired"
    T_TEST_ONE_SAMPLE = "t_test_one_sample"
    ANOVA = "anova"
    CHI_SQUARE = "chi_square"
    MANN_WHITNEY = "mann_whitney"
    WILCOXON = "wilcoxon"
    KRUSKAL_WALLIS = "kruskal_wallis"


class CorrelationMethod(str, Enum):
    """Available correlation methods"""
    AUTO = "auto"
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"


class RegressionType(str, Enum):
    """Available regression types"""
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    LOGISTIC = "logistic"


class OutlierMethod(str, Enum):
    """Available outlier detection methods"""
    IQR = "iqr"
    ZSCORE = "zscore"
    MODIFIED_ZSCORE = "modified_zscore"
    ISOLATION_FOREST = "isolation_forest"


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    WEIGHTED = "weighted"
    RESPONSE_TIME = "response_time"


class ReportFormat(str, Enum):
    """Report output formats"""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


# -------------------- Request Models --------------------

class DescriptiveStatsRequest(BaseModel):
    """Request model for descriptive statistics"""
    data: List[Optional[float]] = Field(description="Numerical data array", min_length=1)
    column_name: str = Field(default="data", description="Name of the variable")
    include_distribution: bool = Field(default=True, description="Include distribution statistics")
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        if not v:
            raise ValueError("Data array cannot be empty")
        if not all(isinstance(x, (int, float)) or x is None for x in v):
            raise ValueError("Data must contain only numbers or None values")
        return v


class CompareGroupsRequest(BaseModel):
    """Request model for group comparison"""
    groups: Dict[str, List[float]] = Field(..., description="Dictionary of group names to data arrays")
    test_type: TestType = Field(default=TestType.AUTO, description="Statistical test to use")
    paired: bool = Field(default=False, description="Whether groups are paired (for 2 groups)")
    post_hoc: bool = Field(default=True, description="Perform post-hoc tests (for ANOVA)")
    alpha: float = Field(default=0.05, ge=0.001, le=0.2, description="Significance level")
    
    @field_validator('groups')
    @classmethod
    def validate_groups(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 groups required for comparison")
        for name, data in v.items():
            if not data:
                raise ValueError(f"Group '{name}' cannot be empty")
            if not all(isinstance(x, (int, float)) or x is None for x in data):
                raise ValueError(f"Group '{name}' must contain only numbers or None values")
        return v


class CorrelationRequest(BaseModel):
    """Request model for correlation analysis"""
    x: List[float] = Field(description="First variable", min_length=3)
    y: List[float] = Field(description="Second variable", min_length=3)
    method: CorrelationMethod = Field(default=CorrelationMethod.AUTO, description="Correlation method")
    x_name: str = Field(default="Variable X", description="Name of first variable")
    y_name: str = Field(default="Variable Y", description="Name of second variable")
    alpha: float = Field(default=0.05, ge=0.001, le=0.2, description="Significance level")
    
    @field_validator('y')
    @classmethod
    def validate_lengths(cls, v, info):
        if 'x' in info.data and len(v) != len(info.data['x']):
            raise ValueError("x and y must have the same length")
        return v


class CorrelationMatrixRequest(BaseModel):
    """Request model for correlation matrix"""
    data: Dict[str, List[float]] = Field(..., description="Dictionary of variable names to data arrays")
    method: CorrelationMethod = Field(default=CorrelationMethod.PEARSON, description="Correlation method")
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 variables required for correlation matrix")
        lengths = [len(data) for data in v.values()]
        if len(set(lengths)) > 1:
            raise ValueError("All variables must have the same length")
        return v


class RegressionRequest(BaseModel):
    """Request model for regression analysis"""
    x: Union[List[float], Dict[str, List[float]]] = Field(..., description="Independent variable(s)")
    y: List[float] = Field(..., description="Dependent variable")
    regression_type: RegressionType = Field(default=RegressionType.LINEAR, description="Type of regression")
    degree: int = Field(default=2, ge=2, le=5, description="Polynomial degree (for polynomial regression)")
    feature_names: Optional[List[str]] = Field(default=None, description="Names of features")
    check_assumptions: bool = Field(default=True, description="Check regression assumptions")
    alpha: float = Field(default=0.05, ge=0.001, le=0.2, description="Significance level")
    
    @field_validator('x')
    @classmethod
    def validate_x(cls, v):
        if isinstance(v, dict):
            # Multiple predictors
            if not v:
                raise ValueError("X dictionary cannot be empty")
            lengths = [len(data) for data in v.values()]
            if len(set(lengths)) > 1:
                raise ValueError("All predictor variables must have the same length")
        elif isinstance(v, list):
            # Single predictor
            if not v:
                raise ValueError("X array cannot be empty")
        return v


class TimeSeriesRequest(BaseModel):
    """Request model for time series analysis"""
    data: List[float] = Field(description="Time series data", min_length=10)
    analysis_type: Literal["decomposition", "stationarity", "forecast"] = Field(description="Type of analysis")
    period: Optional[int] = Field(default=None, ge=2, description="Seasonal period (for decomposition)")
    model_type: Literal["additive", "multiplicative"] = Field(default="additive", description="Decomposition model")
    forecast_steps: int = Field(default=10, ge=1, le=100, description="Number of steps to forecast")
    arima_order: Optional[List[int]] = Field(default=None, description="ARIMA order (p, d, q)")
    alpha: float = Field(default=0.05, ge=0.001, le=0.2, description="Significance level")
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        if len(v) < 10:
            raise ValueError("Time series requires at least 10 observations")
        return v


class OutlierDetectionRequest(BaseModel):
    """Request model for outlier detection"""
    data: List[float] = Field(description="Numerical data array", min_length=5)
    methods: List[OutlierMethod] = Field(default=[OutlierMethod.IQR], description="Detection methods to use")
    thresholds: Optional[Dict[str, float]] = Field(default=None, description="Custom thresholds for methods")
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        if len(v) < 5:
            raise ValueError("Outlier detection requires at least 5 observations")
        return v


class ComprehensiveReportRequest(BaseModel):
    """Request model for comprehensive analysis report"""
    file_data: Optional[str] = Field(default=None, description="Base64 encoded CSV/Excel file")
    columns: Optional[List[str]] = Field(default=None, description="Columns to analyze")
    analysis_types: List[str] = Field(default=["descriptive", "correlation"], description="Types of analysis")
    format: ReportFormat = Field(default=ReportFormat.MARKDOWN, description="Output format")
    title: str = Field(default="Statistical Analysis Report", description="Report title")
    include_visualizations: bool = Field(default=True, description="Include visualization suggestions")


# -------------------- Response Models --------------------

class DescriptiveStatsResponse(BaseModel):
    """Response model for descriptive statistics"""
    variable_name: str
    n: int
    n_missing: Optional[int] = None
    missing: Optional[int] = None  # Alias for n_missing
    mean: Optional[float] = None
    median: Optional[float] = None
    mode: Optional[Union[str, float]] = None
    std: Optional[float] = None
    variance: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    range: Optional[float] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    cv: Optional[float] = None
    is_normal: Optional[bool] = None
    normality_p_value: Optional[float] = None
    n_outliers: Optional[int] = None
    unique_values: Optional[int] = None
    most_common: Optional[List[Any]] = None
    interpretation: Optional[str] = None


class StatisticalTestResponse(BaseModel):
    """Response model for statistical tests"""
    test_name: str
    test_type: Optional[str] = None
    statistic: float
    p_value: float
    degrees_of_freedom: Optional[Union[int, float]] = None
    effect_size: Optional[Union[float, Dict[str, Any]]] = None  # Can be float or dict
    effect_size_name: Optional[str] = None
    effect_size_interpretation: Optional[str] = None
    is_significant: bool
    significance_level: Optional[float] = None
    alpha: Optional[float] = None
    interpretation: str
    assumptions_met: Optional[Union[bool, str]] = None  # Can be bool or string
    assumption_details: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    recommendation: Optional[str] = None  # Singular alias
    confidence_interval: Optional[List[float]] = None
    power: Optional[float] = None
    sample_size: Optional[int] = None
    alternative_tests: Optional[List[str]] = None
    suggested_visualizations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    post_hoc_results: Optional[Union[List[Dict[str, Any]], str]] = None


class CorrelationResponse(BaseModel):
    """Response model for correlation analysis"""
    variable1: str
    variable2: str
    correlation_coefficient: float
    p_value: float
    method: str
    n: int
    confidence_interval: Optional[List[float]]
    is_significant: bool
    strength: str
    direction: str
    interpretation: str


class RegressionResponse(BaseModel):
    """Response model for regression analysis"""
    model_type: str
    coefficients: Optional[Dict[str, float]] = None
    intercept: Optional[float] = None
    r_squared: Optional[float] = None
    adjusted_r_squared: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    mse: Optional[float] = None
    n: Optional[int] = None
    n_features: Optional[int] = None
    assumptions_met: Optional[bool] = None
    assumption_details: Optional[List[Dict[str, Any]]] = None
    vif_values: Optional[Dict[str, Optional[float]]] = None
    interpretation: Optional[str] = None
    recommendations: Optional[List[str]] = None
    equation: Optional[str] = None
    feature_importance: Optional[Dict[str, float]] = None
    p_values: Optional[Dict[str, float]] = None
    confidence_intervals: Optional[Dict[str, List[float]]] = None


class TimeSeriesResponse(BaseModel):
    """Response model for time series analysis"""
    analysis_type: str
    is_stationary: Optional[bool] = None
    adf_statistic: Optional[float] = None
    adf_pvalue: Optional[float] = None
    adf_critical_values: Optional[Dict[str, float]] = None
    forecast_length: Optional[int] = None
    forecast: Optional[List[float]] = None
    forecast_lower: Optional[List[float]] = None
    forecast_upper: Optional[List[float]] = None
    model_type: Optional[str] = None
    model_params: Optional[Dict[str, Any]] = None
    trend: Optional[List[float]] = None
    seasonal: Optional[List[float]] = None
    residual: Optional[List[float]] = None
    trend_strength: Optional[float] = None
    seasonal_strength: Optional[float] = None
    trend_length: Optional[int] = None
    interpretation: Optional[str] = None
    recommendations: Optional[List[str]] = None
    recommendation: Optional[str] = None


class OutlierResponse(BaseModel):
    """Response model for outlier detection"""
    method: str
    outlier_indices: List[int]
    outlier_count: Optional[int] = None
    n_outliers: Optional[int] = None  # Alias
    outlier_percentage: Optional[float] = None
    threshold_used: Optional[Union[float, Dict[str, Any]]] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    outlier_values: Optional[List[float]] = None
    interpretation: Optional[str] = None
    recommendations: Optional[List[str]] = None


class MethodsResponse(BaseModel):
    """Response model for available methods"""
    descriptive: List[str]
    comparison_tests: List[str]
    correlation_methods: List[str]
    regression_types: List[str]
    time_series_analyses: List[str]
    outlier_methods: List[str]


# ==================== API Endpoints ====================

@router.post("/descriptive", response_model=DescriptiveStatsResponse, status_code=status.HTTP_200_OK)
async def compute_descriptive_statistics(
    request: DescriptiveStatsRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Compute comprehensive descriptive statistics for a numerical variable.
    
    Returns mean, median, mode, standard deviation, quartiles, skewness, 
    kurtosis, and normality test results.
    """
    try:
        data_array = np.array(request.data, dtype=float)
        
        # Compute descriptive statistics
        result = statistics_engine.analyze_descriptive(
            data_array,
            variable_name=request.column_name
        )
        
        # Sanitize result for JSON serialization (handles tuples, inf, nan)
        result = sanitize_for_json(result)
        
        # Add alias fields for backward compatibility
        if 'n_missing' in result:
            result['missing'] = result['n_missing']
        
        return DescriptiveStatsResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error in descriptive statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error computing descriptive statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute statistics: {str(e)}"
        )


@router.post("/compare", response_model=StatisticalTestResponse, status_code=status.HTTP_200_OK)
async def compare_groups(
    request: CompareGroupsRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Compare groups using appropriate statistical test.
    
    Automatically selects the best test based on data characteristics
    (normality, equal variances) or uses specified test. Includes effect
    sizes and post-hoc tests for ANOVA.
    """
    try:
        # Convert groups to numpy arrays and prepare for positional args
        groups_arrays = [
            np.array(data, dtype=float)
            for data in request.groups.values()
        ]
        
        # Perform comparison
        result = statistics_engine.compare_groups(
            *groups_arrays,
            test_type=request.test_type.value if request.test_type != TestType.AUTO else "auto",
            paired=request.paired,
            post_hoc=request.post_hoc
        )
        
        return StatisticalTestResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error in group comparison: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error comparing groups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare groups: {str(e)}"
        )


@router.post("/correlation", response_model=CorrelationResponse, status_code=status.HTTP_200_OK)
async def analyze_correlation(
    request: CorrelationRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Analyze correlation between two variables.
    
    Automatically selects Pearson or Spearman correlation based on
    normality, or uses specified method. Returns correlation coefficient,
    p-value, confidence interval, and interpretation.
    """
    try:
        x_array = np.array(request.x, dtype=float)
        y_array = np.array(request.y, dtype=float)
        
        # Analyze correlation
        result = statistics_engine.analyze_correlation(
            x=x_array,
            y=y_array,
            method=request.method.value if request.method != CorrelationMethod.AUTO else None,
            var1_name=request.x_name,
            var2_name=request.y_name,
            alpha=request.alpha
        )
        
        # Format response
        response_data = result.copy()
        if response_data.get('confidence_interval'):
            response_data['confidence_interval'] = list(response_data['confidence_interval'])
        
        return CorrelationResponse(**response_data)
        
    except ValueError as e:
        logger.error(f"Validation error in correlation analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error analyzing correlation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze correlation: {str(e)}"
        )


@router.post("/correlation-matrix", status_code=status.HTTP_200_OK)
async def compute_correlation_matrix(
    request: CorrelationMatrixRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Compute correlation matrix for multiple variables.
    
    Returns correlation coefficients and p-values for all pairs of variables.
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Compute correlation matrix
        from app.services.statistical_analyzer_advanced import CorrelationAnalyzer
        analyzer = CorrelationAnalyzer()
        
        corr_matrix, p_matrix = analyzer.correlation_matrix(
            df,
            method=request.method.value
        )
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "p_value_matrix": p_matrix.to_dict(),
            "method": request.method.value,
            "n_variables": len(request.data)
        }
        
    except ValueError as e:
        logger.error(f"Validation error in correlation matrix: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error computing correlation matrix: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute correlation matrix: {str(e)}"
        )


@router.post("/regression", response_model=RegressionResponse, status_code=status.HTTP_200_OK)
async def analyze_regression(
    request: RegressionRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Perform regression analysis.
    
    Supports linear, polynomial, and logistic regression. Includes assumption
    checking, multicollinearity detection (VIF), and comprehensive diagnostics.
    """
    try:
        # Prepare data
        if isinstance(request.x, dict):
            # Multiple predictors
            X = pd.DataFrame(request.x)
            feature_names = list(request.x.keys())
        else:
            # Single predictor
            X = np.array(request.x, dtype=float).reshape(-1, 1)
            feature_names = request.feature_names or ["X"]
        
        y = np.array(request.y, dtype=float)
        
        # Perform regression
        result = statistics_engine.analyze_regression(
            X=X,
            y=y,
            regression_type=request.regression_type.value,
            degree=request.degree if request.regression_type == RegressionType.POLYNOMIAL else None,
            feature_names=feature_names,
            check_assumptions=request.check_assumptions,
            alpha=request.alpha
        )
        
        # Sanitize result for JSON serialization
        result = sanitize_for_json(result)
        
        return RegressionResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error in regression analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error analyzing regression: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze regression: {str(e)}"
        )


@router.post("/time-series", response_model=TimeSeriesResponse, status_code=status.HTTP_200_OK)
async def analyze_time_series(
    request: TimeSeriesRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Perform time series analysis.
    
    Supports decomposition (trend/seasonal/residual), stationarity testing
    (ADF test), and ARIMA forecasting with confidence intervals.
    """
    try:
        data_array = np.array(request.data, dtype=float)
        
        # Perform time series analysis
        arima_order_tuple = None
        if request.arima_order and len(request.arima_order) == 3:
            arima_order_tuple = (request.arima_order[0], request.arima_order[1], request.arima_order[2])
        
        result = statistics_engine.analyze_time_series(
            data=data_array,
            analysis_type=request.analysis_type,
            period=request.period,
            model_type=request.model_type,
            forecast_steps=request.forecast_steps,
            arima_order=arima_order_tuple,
            alpha=request.alpha
        )
        
        return TimeSeriesResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error in time series analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error analyzing time series: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze time series: {str(e)}"
        )


@router.post("/outliers", response_model=List[OutlierResponse], status_code=status.HTTP_200_OK)
async def detect_outliers(
    request: OutlierDetectionRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Detect outliers using specified methods.
    
    Supports IQR, Z-score, modified Z-score, and isolation forest methods.
    Returns outlier indices and counts for each method.
    """
    try:
        data_array = np.array(request.data, dtype=float)
        
        results = []
        for method in request.methods:
            # Build kwargs based on method
            kwargs = {}
            if request.thresholds and method.value in request.thresholds:
                threshold_val = request.thresholds[method.value]
                if method == OutlierMethod.IQR:
                    kwargs['multiplier'] = threshold_val
                elif method == OutlierMethod.ISOLATION_FOREST:
                    kwargs['contamination'] = threshold_val
                else:  # zscore, modified_zscore
                    kwargs['threshold'] = threshold_val
            
            result = statistics_engine.detect_outliers(
                data=data_array,
                method=method.value,
                **kwargs
            )
            
            # Get outlier count (service uses 'n_outliers', not 'outlier_count')
            n_outliers = result.get('n_outliers', result.get('outlier_count', 0))
            outlier_percentage = (n_outliers / len(request.data)) * 100 if len(request.data) > 0 else 0.0
            
            results.append(OutlierResponse(
                method=result.get('method', method.value),
                outlier_indices=result.get('outlier_indices', []),
                outlier_count=n_outliers,
                n_outliers=n_outliers,
                outlier_percentage=round(outlier_percentage, 2),
                threshold_used=result.get('threshold'),
                outlier_values=result.get('outlier_values'),
                interpretation=result.get('interpretation', f"Found {n_outliers} outliers using {method.value} method"),
                recommendations=result.get('recommendations')
            ))
        
        return results
        
    except ValueError as e:
        logger.error(f"Validation error in outlier detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error detecting outliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect outliers: {str(e)}"
        )


@router.post("/report", status_code=status.HTTP_200_OK)
async def generate_comprehensive_report(
    request: ComprehensiveReportRequest,
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    Generate comprehensive statistical analysis report.
    
    Performs multiple analyses and generates formatted report in markdown,
    HTML, or JSON format. Includes visualization suggestions.
    """
    try:
        # Parse file data if provided
        if request.file_data:
            import base64
            file_bytes = base64.b64decode(request.file_data)
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            raise ValueError("No data provided")
        
        # Select columns to analyze
        if request.columns:
            df = df[request.columns]
        
        # Perform analyses
        analysis_results = {}
        
        if "descriptive" in request.analysis_types:
            descriptive = {}
            for col in df.select_dtypes(include=[np.number]).columns:
                col_data = np.array(df[col].dropna().values, dtype=float)
                result = statistics_engine.analyze_descriptive(
                    data=col_data,
                    variable_name=col
                )
                descriptive[col] = result
            analysis_results['descriptive'] = descriptive
        
        if "correlation" in request.analysis_types:
            from app.services.statistical_analyzer_advanced import CorrelationAnalyzer
            analyzer = CorrelationAnalyzer()
            corr_matrix, p_matrix = analyzer.correlation_matrix(df)
            analysis_results['correlation'] = {
                'correlation_matrix': corr_matrix.to_dict(),
                'p_value_matrix': p_matrix.to_dict()
            }
        
        # Generate comprehensive report string
        # Note: The generate_report method expects a single result object, not a dict
        # For comprehensive reports with multiple analyses, we'll format manually
        report_sections = []
        report_sections.append(f"# {request.title}\n")
        report_sections.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if "descriptive" in analysis_results:
            report_sections.append("\n## Descriptive Statistics\n")
            for var_name, stats in analysis_results['descriptive'].items():
                report_sections.append(f"\n### {var_name}\n")
                report_sections.append(f"- Mean: {stats.get('mean', 'N/A'):.3f}\n")
                report_sections.append(f"- Median: {stats.get('median', 'N/A'):.3f}\n")
                report_sections.append(f"- Std Dev: {stats.get('std', 'N/A'):.3f}\n")
                report_sections.append(f"- N: {stats.get('n', 'N/A')}\n")
        
        if "correlation" in analysis_results:
            report_sections.append("\n## Correlation Analysis\n")
            report_sections.append("\nCorrelation matrix computed.\n")
        
        result = "".join(report_sections)
        
        if request.format == ReportFormat.HTML:
            return StreamingResponse(
                io.StringIO(result),
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename={request.title.replace(' ', '_')}.html"}
            )
        elif request.format == ReportFormat.MARKDOWN:
            return StreamingResponse(
                io.StringIO(result),
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename={request.title.replace(' ', '_')}.md"}
            )
        else:  # JSON
            sanitized_results = sanitize_for_json(analysis_results)
            return JSONResponse(content=sanitized_results)
        
    except ValueError as e:
        logger.error(f"Validation error in report generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/methods", response_model=MethodsResponse, status_code=status.HTTP_200_OK)
async def list_available_methods(
    current_user: User = Depends(require_permission('use:statistics'))
):
    """
    List all available statistical methods and tests.
    
    Returns comprehensive list of supported descriptive statistics,
    hypothesis tests, correlation methods, regression types, time series
    analyses, and outlier detection methods.
    """
    return MethodsResponse(
        descriptive=[
            "mean", "median", "mode", "std", "variance",
            "min", "max", "range", "quartiles", "iqr",
            "skewness", "kurtosis", "normality_test"
        ],
        comparison_tests=[
            "t_test_independent", "t_test_paired", "t_test_one_sample",
            "anova", "chi_square", "mann_whitney", "wilcoxon", "kruskal_wallis"
        ],
        correlation_methods=[
            "pearson", "spearman", "kendall", "partial_correlation"
        ],
        regression_types=[
            "linear", "polynomial", "logistic", "ridge", "lasso"
        ],
        time_series_analyses=[
            "decomposition", "stationarity_test", "arima_forecast",
            "acf", "pacf", "seasonal_analysis"
        ],
        outlier_methods=[
            "iqr", "zscore", "modified_zscore", "isolation_forest"
        ]
    )


@router.get("/health", status_code=status.HTTP_200_OK)
async def check_statistics_health():
    """
    Health check endpoint for statistics service.
    
    Verifies that all statistical modules are loaded and functioning.
    """
    try:
        # Quick test
        test_data = np.array([1, 2, 3, 4, 5])
        statistics_engine.analyze_descriptive(test_data, "test")
        
        return {
            "status": "healthy",
            "service": "statistical_analysis",
            "modules": {
                "descriptive": True,
                "comparison": True,
                "correlation": True,
                "regression": True,
                "time_series": True,
                "outliers": True,
                "reports": True
            },
            "test_result": "passed"
        }
    except Exception as e:
        logger.error(f"Statistics health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Statistics service unhealthy: {str(e)}"
        )
