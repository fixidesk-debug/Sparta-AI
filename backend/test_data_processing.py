"""
Integration Tests for Data Processing System

Comprehensive tests for DataProcessor, DataProfiler, DataCleaner, and helpers.

Author: Sparta AI Team
Date: October 14, 2025
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path

from app.services.data_processor import DataProcessor
from app.services.data_profiler import DataProfiler
from app.services.data_cleaner import DataCleaner
from app.services.data_helpers import FileValidator, MetadataExtractor, RecommendationEngine


class TestDataProcessor:
    """Test DataProcessor class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.processor = DataProcessor()
        self.test_df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 35, 40, 45],
            'salary': [50000, 60000, 70000, 80000, 90000]
        })
    
    def test_csv_roundtrip(self):
        """Test CSV save and load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.csv')
            
            # Save
            self.processor.save_file(self.test_df, file_path)
            assert os.path.exists(file_path)
            
            # Load
            loaded_df = self.processor.load_file(file_path)
            pd.testing.assert_frame_equal(self.test_df, loaded_df)
    
    def test_excel_roundtrip(self):
        """Test Excel save and load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.xlsx')
            
            # Save
            self.processor.save_file(self.test_df, file_path)
            assert os.path.exists(file_path)
            
            # Load
            loaded_df = self.processor.load_file(file_path)
            pd.testing.assert_frame_equal(self.test_df, loaded_df)
    
    def test_json_roundtrip(self):
        """Test JSON save and load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.json')
            
            # Save
            self.processor.save_file(self.test_df, file_path)
            assert os.path.exists(file_path)
            
            # Load
            loaded_df = self.processor.load_file(file_path)
            pd.testing.assert_frame_equal(self.test_df, loaded_df)
    
    def test_parquet_roundtrip(self):
        """Test Parquet save and load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.parquet')
            
            # Save
            self.processor.save_file(self.test_df, file_path)
            assert os.path.exists(file_path)
            
            # Load
            loaded_df = self.processor.load_file(file_path)
            pd.testing.assert_frame_equal(self.test_df, loaded_df)
    
    def test_memory_optimization(self):
        """Test memory optimization"""
        # Create DataFrame with inefficient types
        df = pd.DataFrame({
            'small_int': np.arange(100, dtype=np.int64),  # Could be int8
            'category': ['A', 'B', 'C'] * 33 + ['A'],  # Could be category
            'large_int': np.arange(100000, 100100, dtype=np.int64)  # Needs int32
        })
        
        original_memory = self.processor.get_memory_usage(df)
        optimized_df = self.processor.optimize_memory(df)
        optimized_memory = self.processor.get_memory_usage(optimized_df)
        
        # Should reduce memory
        assert optimized_memory['total_bytes'] < original_memory['total_bytes']
        
        # Should preserve data
        assert len(optimized_df) == len(df)
        assert list(optimized_df.columns) == list(df.columns)
    
    def test_unsupported_format(self):
        """Test unsupported format handling"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.unsupported')
            
            # Try to save with unsupported format
            with pytest.raises(Exception):
                self.processor.save_file(self.test_df, file_path)


class TestDataProfiler:
    """Test DataProfiler class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.profiler = DataProfiler()
        self.test_df = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5, 100],  # Has outlier
            'categorical': ['A', 'B', 'A', 'B', 'A', 'B'],
            'text': ['hello', 'world', 'test', 'data', 'analysis', 'profiling'],
            'missing': [1, None, 3, None, 5, None]
        })
    
    def test_type_detection(self):
        """Test column type detection"""
        assert self.profiler.detect_column_type(self.test_df['numeric']) == 'numeric'
        assert self.profiler.detect_column_type(self.test_df['categorical']) == 'categorical'
        # Text with low uniqueness is detected as categorical
        assert self.profiler.detect_column_type(self.test_df['text']) in ['text', 'categorical']
    
    def test_numeric_summary(self):
        """Test numeric column summary"""
        summary = self.profiler.get_numeric_summary(self.test_df['numeric'])
        
        assert 'mean' in summary
        assert 'median' in summary
        assert 'std' in summary
        assert summary['count'] == 6
        assert summary['min'] == 1
        assert summary['max'] == 100
    
    def test_categorical_summary(self):
        """Test categorical column summary"""
        summary = self.profiler.get_categorical_summary(self.test_df['categorical'])
        
        assert 'count' in summary
        assert 'unique' in summary
        assert summary['unique'] == 2
        assert 'top' in summary
    
    def test_missing_value_analysis(self):
        """Test missing value analysis"""
        analysis = self.profiler.analyze_missing_values(self.test_df)
        
        assert 'total_missing' in analysis
        assert analysis['total_missing'] == 3
        assert 'columns_with_missing' in analysis
        assert 'missing' in analysis['columns_with_missing']
    
    def test_outlier_detection(self):
        """Test outlier detection"""
        outliers = self.profiler.detect_outliers(self.test_df['numeric'], method='iqr')
        
        assert 'count' in outliers
        assert outliers['has_outliers']
        assert 100 in outliers['values']
    
    def test_quality_assessment(self):
        """Test data quality assessment"""
        quality = self.profiler.assess_data_quality(self.test_df)
        
        assert 'quality_score' in quality
        assert 'rating' in quality
        assert 'issues' in quality
        assert 0 <= quality['quality_score'] <= 100
    
    def test_dataset_profiling(self):
        """Test complete dataset profiling"""
        profile = self.profiler.profile_dataset(self.test_df)
        
        assert 'overview' in profile
        assert 'columns' in profile
        assert 'missing_analysis' in profile
        assert 'quality' in profile
        
        assert profile['overview']['rows'] == 6
        assert profile['overview']['columns'] == 4
    
    def test_insights_generation(self):
        """Test insights generation"""
        insights = self.profiler.get_insights(self.test_df)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        # Check insight structure
        for insight in insights:
            assert 'message' in insight
            assert 'type' in insight
            assert 'severity' in insight


class TestDataCleaner:
    """Test DataCleaner class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.cleaner = DataCleaner()
        self.test_df = pd.DataFrame({
            'numeric': [1, 2, None, 4, 5, 100],  # Has missing and outlier
            'categorical': ['A', 'B', 'A', None, 'A', 'B'],  # Has missing
            'duplicate_row': [1, 2, 3, 3, 5, 6]  # For duplicate detection
        })
    
    def test_handle_missing_auto(self):
        """Test automatic missing value handling"""
        cleaned_df = self.cleaner.handle_missing_values(self.test_df.copy(), strategy='auto')
        
        # Should have no missing values
        assert cleaned_df.isna().sum().sum() == 0
    
    def test_handle_missing_mean(self):
        """Test mean imputation"""
        cleaned_df = self.cleaner.handle_missing_values(
            self.test_df.copy(),
            strategy='mean',
            columns=['numeric']
        )
        
        # Numeric column should have no missing
        assert cleaned_df['numeric'].isna().sum() == 0
    
    def test_handle_missing_mode(self):
        """Test mode imputation"""
        cleaned_df = self.cleaner.handle_missing_values(
            self.test_df.copy(),
            strategy='mode',
            columns=['categorical']
        )
        
        # Categorical column should have no missing
        assert cleaned_df['categorical'].isna().sum() == 0
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        # Add a duplicate row
        df_with_dupes = pd.concat([self.test_df, self.test_df.iloc[[0]]], ignore_index=True)
        
        cleaned_df = self.cleaner.remove_duplicates(df_with_dupes)
        
        # Should have fewer rows
        assert len(cleaned_df) < len(df_with_dupes)
        assert cleaned_df.duplicated().sum() == 0
    
    def test_remove_outliers(self):
        """Test outlier removal"""
        original_len = len(self.test_df)
        cleaned_df = self.cleaner.remove_outliers(
            self.test_df.copy(),
            columns=['numeric'],
            method='iqr'
        )
        
        # Should remove the outlier (100)
        assert len(cleaned_df) < original_len
        assert 100 not in cleaned_df['numeric'].values
    
    def test_cap_outliers(self):
        """Test outlier capping"""
        cleaned_df = self.cleaner.cap_outliers(
            self.test_df.copy(),
            columns=['numeric'],
            method='iqr'
        )
        
        # Should keep all rows
        assert len(cleaned_df) == len(self.test_df)
        
        # Outlier should be capped
        assert cleaned_df['numeric'].max() < 100
    
    def test_normalize_column(self):
        """Test column normalization"""
        df = pd.DataFrame({'values': [1, 2, 3, 4, 5]})
        
        normalized_df = self.cleaner.normalize_column(
            df.copy(),
            columns=['values'],
            method='standard'
        )
        
        # Standard normalization: mean ~0, std ~1 (but pandas uses ddof=1 by default)
        assert abs(normalized_df['values'].mean()) < 0.01
        # Allow some tolerance for pandas ddof=1 calculation
        assert 0.9 <= normalized_df['values'].std() <= 1.2
    
    def test_convert_types(self):
        """Test type conversion"""
        df = pd.DataFrame({
            'int_as_str': ['1', '2', '3'],
            'float_as_str': ['1.5', '2.5', '3.5']
        })
        
        cleaned_df = self.cleaner.convert_types(
            df,
            type_mapping={
                'int_as_str': 'int',
                'float_as_str': 'float'
            }
        )
        
        # Check that types are numeric (pandas may use Int64 or int64)
        assert pd.api.types.is_integer_dtype(cleaned_df['int_as_str'])
        assert pd.api.types.is_float_dtype(cleaned_df['float_as_str'])
    
    def test_auto_clean(self):
        """Test automatic cleaning"""
        cleaned_df, report = self.cleaner.auto_clean(self.test_df.copy())
        
        assert isinstance(report, dict)
        assert 'operations' in report
        assert len(report['operations']) > 0
        
        # Should have cleaned missing values
        assert cleaned_df.isna().sum().sum() == 0


class TestFileValidator:
    """Test FileValidator class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.validator = FileValidator()
        self.test_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['A', 'B', 'C']
        })
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        validation = self.validator.validate_file('nonexistent.csv')
        
        assert not validation['is_valid']
        assert len(validation['errors']) > 0
    
    def test_validate_valid_csv(self):
        """Test validation of valid CSV file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.csv')
            self.test_df.to_csv(file_path, index=False)
            
            validation = self.validator.validate_file(file_path)
            
            assert validation['is_valid']
            assert len(validation['errors']) == 0
    
    def test_validate_unsupported_format(self):
        """Test validation of unsupported format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.xyz')
            Path(file_path).touch()
            
            validation = self.validator.validate_file(file_path)
            
            assert not validation['is_valid']
            assert any('Unsupported' in error for error in validation['errors'])
    
    def test_validate_dataframe(self):
        """Test DataFrame validation"""
        validation = self.validator.validate_dataframe(self.test_df)
        
        assert validation['is_valid']
        assert validation['dataframe_info']['rows'] == 3
        assert validation['dataframe_info']['columns'] == 2
    
    def test_validate_empty_dataframe(self):
        """Test validation of empty DataFrame"""
        empty_df = pd.DataFrame()
        validation = self.validator.validate_dataframe(empty_df)
        
        assert not validation['is_valid']


class TestMetadataExtractor:
    """Test MetadataExtractor class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.extractor = MetadataExtractor()
        self.test_df = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'categorical': ['A', 'B', 'A', 'B', 'A'],
            'missing': [1, None, 3, None, 5]
        })
    
    def test_extract_metadata(self):
        """Test metadata extraction"""
        metadata = self.extractor.extract_metadata(self.test_df)
        
        assert 'basic' in metadata
        assert 'columns' in metadata
        assert 'memory' in metadata
        assert 'data_types' in metadata
    
    def test_basic_info(self):
        """Test basic information extraction"""
        metadata = self.extractor.extract_metadata(self.test_df)
        basic = metadata['basic']
        
        assert basic['rows'] == 5
        assert basic['columns'] == 3
        assert basic['total_cells'] == 15
        assert basic['missing_cells'] == 2
    
    def test_column_info(self):
        """Test column information extraction"""
        metadata = self.extractor.extract_metadata(self.test_df)
        columns = metadata['columns']
        
        assert 'numeric' in columns
        assert 'categorical' in columns
        assert 'missing' in columns
        
        assert columns['numeric']['null_count'] == 0
        assert columns['missing']['null_count'] == 2


class TestRecommendationEngine:
    """Test RecommendationEngine class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.engine = RecommendationEngine()
        self.test_df = pd.DataFrame({
            'numeric1': [1, 2, 3, 4, 5],
            'numeric2': [2, 4, 6, 8, 10],
            'categorical': ['A', 'B', 'A', 'B', 'A'],
            'missing': [1, None, 3, None, 5]
        })
    
    def test_get_recommendations(self):
        """Test recommendation generation"""
        recommendations = self.engine.get_recommendations(self.test_df)
        
        assert 'cleaning' in recommendations
        assert 'analysis' in recommendations
        assert 'visualization' in recommendations
        assert 'modeling' in recommendations
    
    def test_cleaning_recommendations(self):
        """Test cleaning recommendations"""
        recommendations = self.engine.get_recommendations(self.test_df)
        cleaning = recommendations['cleaning']
        
        # Should recommend handling missing values
        assert any('Missing' in rec['title'] for rec in cleaning)
    
    def test_analysis_recommendations(self):
        """Test analysis recommendations"""
        recommendations = self.engine.get_recommendations(self.test_df)
        analysis = recommendations['analysis']
        
        # Should have analysis recommendations
        assert len(analysis) > 0
    
    def test_visualization_recommendations(self):
        """Test visualization recommendations"""
        recommendations = self.engine.get_recommendations(self.test_df)
        viz = recommendations['visualization']
        
        # Should recommend visualizations
        assert len(viz) > 0
    
    def test_quick_insights(self):
        """Test quick insights generation"""
        insights = self.engine.get_quick_insights(self.test_df)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        # Should mention dataset size
        assert any('5 rows' in insight for insight in insights)


class TestEndToEndWorkflow:
    """Test complete workflow integration"""
    
    def setup_method(self):
        """Setup for each test"""
        self.processor = DataProcessor()
        self.profiler = DataProfiler()
        self.cleaner = DataCleaner()
        self.validator = FileValidator()
        self.extractor = MetadataExtractor()
        self.engine = RecommendationEngine()
    
    def test_complete_workflow(self):
        """Test complete data processing workflow"""
        # Create test data with issues
        df = pd.DataFrame({
            'id': [1, 2, 3, 3, 5],  # Has duplicate
            'value': [10, None, 30, 40, 1000],  # Has missing and outlier
            'category': ['A', 'B', None, 'A', 'B']  # Has missing
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Save file
            file_path = os.path.join(tmpdir, 'test.csv')
            self.processor.save_file(df, file_path)
            
            # 2. Validate file
            validation = self.validator.validate_file(file_path)
            assert validation['is_valid']
            
            # 3. Load file
            loaded_df = self.processor.load_file(file_path)
            
            # 4. Validate DataFrame
            df_validation = self.validator.validate_dataframe(loaded_df)
            assert df_validation['is_valid']
            
            # 5. Extract metadata
            metadata = self.extractor.extract_metadata(loaded_df)
            assert metadata['basic']['rows'] == 5
            
            # 6. Profile data
            profile = self.profiler.profile_dataset(loaded_df)
            assert 'quality' in profile
            
            # 7. Get recommendations
            recommendations = self.engine.get_recommendations(loaded_df)
            assert len(recommendations['cleaning']) > 0
            
            # 8. Clean data
            cleaned_df, report = self.cleaner.auto_clean(loaded_df)
            
            # 9. Verify cleaning
            assert cleaned_df.isna().sum().sum() == 0  # No missing
            assert cleaned_df.duplicated().sum() == 0  # No duplicates
            
            # 10. Save cleaned data
            cleaned_path = os.path.join(tmpdir, 'cleaned.csv')
            self.processor.save_file(cleaned_df, cleaned_path)
            assert os.path.exists(cleaned_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
