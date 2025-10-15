"""
Unit Tests for Statistical Analysis API Endpoints

Tests for all statistical analysis endpoints with various scenarios.

Author: Sparta AI Team
Date: October 14, 2025
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
import base64
import io

from app.main import app
from app.db.session import get_db
from app.db.models import User, Base
from app.core.security import create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_statistics.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(setup_database):
    """Create test user and return authentication token"""
    db = TestingSessionLocal()
    
    # Create test user
    from app.core.security import get_password_hash
    user = User(
        email="test@spartaai.com",
        hashed_password=get_password_hash("test_password_123"),
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    token = create_access_token({"sub": user.email})
    
    yield {"user": user, "token": token}
    
    db.delete(user)
    db.commit()
    db.close()


@pytest.fixture
def auth_headers(test_user):
    """Return authentication headers"""
    return {"Authorization": f"Bearer {test_user['token']}"}


# ==================== Test Descriptive Statistics ====================

def test_descriptive_statistics_success(auth_headers):
    """Test successful descriptive statistics computation"""
    data = {
        "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "column_name": "test_data",
        "include_distribution": True
    }
    
    response = client.post(
        "/api/v1/statistics/descriptive",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["variable_name"] == "test_data"
    assert result["n"] == 10
    assert result["mean"] == pytest.approx(5.5, abs=0.01)
    assert result["median"] == pytest.approx(5.5, abs=0.01)
    assert result["std"] > 0
    assert "interpretation" in result


def test_descriptive_statistics_with_missing_values(auth_headers):
    """Test descriptive statistics with None values"""
    data = {
        "data": [1, 2, None, 4, 5, None, 7, 8, 9, 10],
        "column_name": "test_data"
    }
    
    response = client.post(
        "/api/v1/statistics/descriptive",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["missing"] == 2
    assert result["n"] == 8  # Only non-missing values


def test_descriptive_statistics_empty_data(auth_headers):
    """Test descriptive statistics with empty data"""
    data = {
        "data": [],
        "column_name": "test_data"
    }
    
    response = client.post(
        "/api/v1/statistics/descriptive",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


def test_descriptive_statistics_unauthorized():
    """Test descriptive statistics without authentication"""
    data = {
        "data": [1, 2, 3, 4, 5],
        "column_name": "test_data"
    }
    
    response = client.post(
        "/api/v1/statistics/descriptive",
        json=data
    )
    
    assert response.status_code == 401


# ==================== Test Group Comparison ====================

def test_compare_groups_t_test(auth_headers):
    """Test independent t-test for group comparison"""
    data = {
        "groups": {
            "group1": [1, 2, 3, 4, 5],
            "group2": [6, 7, 8, 9, 10]
        },
        "test_type": "t_test_independent",
        "alpha": 0.05
    }
    
    response = client.post(
        "/api/v1/statistics/compare",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["test_name"] == "Independent t-test"
    assert "statistic" in result
    assert "p_value" in result
    assert "effect_size" in result
    assert "interpretation" in result


def test_compare_groups_anova(auth_headers):
    """Test ANOVA for multiple group comparison"""
    data = {
        "groups": {
            "group1": [1, 2, 3, 4, 5],
            "group2": [6, 7, 8, 9, 10],
            "group3": [11, 12, 13, 14, 15]
        },
        "test_type": "anova",
        "post_hoc": True,
        "alpha": 0.05
    }
    
    response = client.post(
        "/api/v1/statistics/compare",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["test_name"] == "One-way ANOVA"
    assert "post_hoc_results" in result
    assert result["post_hoc_results"] is not None


def test_compare_groups_auto_selection(auth_headers):
    """Test automatic test selection"""
    data = {
        "groups": {
            "group1": [1, 2, 3, 4, 5],
            "group2": [6, 7, 8, 9, 10]
        },
        "test_type": "auto",
        "alpha": 0.05
    }
    
    response = client.post(
        "/api/v1/statistics/compare",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["test_name"] in [
        "Independent t-test",
        "Mann-Whitney U test"
    ]


def test_compare_groups_invalid_groups(auth_headers):
    """Test group comparison with only one group"""
    data = {
        "groups": {
            "group1": [1, 2, 3, 4, 5]
        },
        "test_type": "auto"
    }
    
    response = client.post(
        "/api/v1/statistics/compare",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


# ==================== Test Correlation Analysis ====================

def test_correlation_analysis_pearson(auth_headers):
    """Test Pearson correlation"""
    # Create correlated data
    x = list(range(1, 11))
    y = [val * 2 + np.random.normal(0, 0.5) for val in x]
    
    data = {
        "x": x,
        "y": y,
        "method": "pearson",
        "x_name": "Variable X",
        "y_name": "Variable Y",
        "alpha": 0.05
    }
    
    response = client.post(
        "/api/v1/statistics/correlation",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["method"] == "pearson"
    assert "correlation_coefficient" in result
    assert "p_value" in result
    assert "strength" in result
    assert "direction" in result
    assert result["direction"] == "positive"


def test_correlation_analysis_spearman(auth_headers):
    """Test Spearman correlation"""
    data = {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "method": "spearman",
        "alpha": 0.05
    }
    
    response = client.post(
        "/api/v1/statistics/correlation",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["method"] == "spearman"
    assert abs(result["correlation_coefficient"]) == pytest.approx(1.0, abs=0.01)


def test_correlation_analysis_mismatched_lengths(auth_headers):
    """Test correlation with mismatched array lengths"""
    data = {
        "x": [1, 2, 3, 4, 5],
        "y": [1, 2, 3],
        "method": "pearson"
    }
    
    response = client.post(
        "/api/v1/statistics/correlation",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


def test_correlation_matrix(auth_headers):
    """Test correlation matrix computation"""
    data = {
        "data": {
            "var1": [1, 2, 3, 4, 5],
            "var2": [2, 4, 6, 8, 10],
            "var3": [5, 4, 3, 2, 1]
        },
        "method": "pearson"
    }
    
    response = client.post(
        "/api/v1/statistics/correlation-matrix",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert "correlation_matrix" in result
    assert "p_value_matrix" in result
    assert result["n_variables"] == 3


# ==================== Test Regression Analysis ====================

def test_linear_regression(auth_headers):
    """Test simple linear regression"""
    x = list(range(1, 11))
    y = [val * 2 + 1 for val in x]  # y = 2x + 1
    
    data = {
        "x": x,
        "y": y,
        "regression_type": "linear",
        "check_assumptions": True
    }
    
    response = client.post(
        "/api/v1/statistics/regression",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["model_type"] == "linear"
    assert result["r_squared"] > 0.95  # Should be nearly perfect fit
    assert "coefficients" in result
    assert "intercept" in result


def test_polynomial_regression(auth_headers):
    """Test polynomial regression"""
    x = list(range(1, 11))
    y = [val ** 2 for val in x]  # Quadratic relationship
    
    data = {
        "x": x,
        "y": y,
        "regression_type": "polynomial",
        "degree": 2,
        "check_assumptions": True
    }
    
    response = client.post(
        "/api/v1/statistics/regression",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["model_type"] == "polynomial"
    assert result["r_squared"] > 0.95


def test_multiple_regression(auth_headers):
    """Test multiple linear regression"""
    data = {
        "x": {
            "x1": [1, 2, 3, 4, 5],
            "x2": [2, 4, 6, 8, 10]
        },
        "y": [3, 6, 9, 12, 15],  # y = x1 + x2
        "regression_type": "linear",
        "check_assumptions": True
    }
    
    response = client.post(
        "/api/v1/statistics/regression",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["model_type"] == "linear"
    assert result["n_features"] == 2
    assert "vif_values" in result


# ==================== Test Time Series Analysis ====================

def test_time_series_stationarity(auth_headers):
    """Test stationarity testing"""
    # Create stationary data
    data_vals = list(np.random.normal(0, 1, 100))
    
    data = {
        "data": data_vals,
        "analysis_type": "stationarity",
        "alpha": 0.05
    }
    
    response = client.post(
        "/api/v1/statistics/time-series",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["analysis_type"] == "stationarity"
    assert "is_stationary" in result
    assert "adf_statistic" in result
    assert "adf_pvalue" in result


def test_time_series_decomposition(auth_headers):
    """Test time series decomposition"""
    # Create data with trend and seasonality
    t = np.arange(100)
    trend = t * 0.5
    seasonal = 10 * np.sin(2 * np.pi * t / 12)
    data_vals = list(trend + seasonal + np.random.normal(0, 1, 100))
    
    data = {
        "data": data_vals,
        "analysis_type": "decomposition",
        "period": 12,
        "model_type": "additive"
    }
    
    response = client.post(
        "/api/v1/statistics/time-series",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["analysis_type"] == "decomposition"


def test_time_series_insufficient_data(auth_headers):
    """Test time series with insufficient data"""
    data = {
        "data": [1, 2, 3, 4, 5],  # Too few observations
        "analysis_type": "forecast",
        "forecast_steps": 5
    }
    
    response = client.post(
        "/api/v1/statistics/time-series",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


# ==================== Test Outlier Detection ====================

def test_outlier_detection_iqr(auth_headers):
    """Test IQR method for outlier detection"""
    # Create data with outliers
    data_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 is outlier
    
    data = {
        "data": data_vals,
        "methods": ["iqr"]
    }
    
    response = client.post(
        "/api/v1/statistics/outliers",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    results = response.json()
    
    assert len(results) == 1
    assert results[0]["method"] == "iqr"
    assert results[0]["outlier_count"] > 0
    assert 9 in results[0]["outlier_indices"]  # Index of value 100


def test_outlier_detection_multiple_methods(auth_headers):
    """Test multiple outlier detection methods"""
    data_vals = list(range(1, 20)) + [100, 200]  # Two outliers
    
    data = {
        "data": data_vals,
        "methods": ["iqr", "zscore", "isolation_forest"]
    }
    
    response = client.post(
        "/api/v1/statistics/outliers",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    results = response.json()
    
    assert len(results) == 3
    methods = [r["method"] for r in results]
    assert "iqr" in methods
    assert "zscore" in methods
    assert "isolation_forest" in methods


# ==================== Test Report Generation ====================

def test_generate_comprehensive_report(auth_headers):
    """Test comprehensive report generation"""
    # Create sample CSV data
    df = pd.DataFrame({
        "age": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        "income": [30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000],
        "satisfaction": [3, 4, 4, 5, 5, 4, 5, 5, 4, 5]
    })
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode()
    file_data = base64.b64encode(csv_bytes).decode()
    
    data = {
        "file_data": file_data,
        "columns": ["age", "income"],
        "analysis_types": ["descriptive", "correlation"],
        "format": "json",
        "title": "Test Report",
        "include_visualizations": True
    }
    
    response = client.post(
        "/api/v1/statistics/report",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200


# ==================== Test Methods Endpoint ====================

def test_list_available_methods(auth_headers):
    """Test listing available statistical methods"""
    response = client.get(
        "/api/v1/statistics/methods",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert "descriptive" in result
    assert "comparison_tests" in result
    assert "correlation_methods" in result
    assert "regression_types" in result
    assert "time_series_analyses" in result
    assert "outlier_methods" in result
    
    # Check specific methods
    assert "mean" in result["descriptive"]
    assert "t_test_independent" in result["comparison_tests"]
    assert "pearson" in result["correlation_methods"]
    assert "linear" in result["regression_types"]


# ==================== Test Health Endpoint ====================

def test_statistics_health():
    """Test statistics service health check"""
    response = client.get("/api/v1/statistics/health")
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["status"] == "healthy"
    assert result["service"] == "statistical_analysis"
    assert "modules" in result
    assert result["modules"]["descriptive"] == True
    assert result["test_result"] == "passed"


# ==================== Performance Tests ====================

def test_large_dataset_descriptive(auth_headers):
    """Test descriptive statistics with large dataset"""
    data_vals = list(np.random.normal(100, 15, 10000))
    
    data = {
        "data": data_vals,
        "column_name": "large_dataset"
    }
    
    response = client.post(
        "/api/v1/statistics/descriptive",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["n"] == 10000


def test_large_correlation_matrix(auth_headers):
    """Test correlation matrix with many variables"""
    n_vars = 10
    n_obs = 100
    
    data_dict = {
        f"var{i}": list(np.random.normal(0, 1, n_obs))
        for i in range(n_vars)
    }
    
    data = {
        "data": data_dict,
        "method": "pearson"
    }
    
    response = client.post(
        "/api/v1/statistics/correlation-matrix",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["n_variables"] == n_vars


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
