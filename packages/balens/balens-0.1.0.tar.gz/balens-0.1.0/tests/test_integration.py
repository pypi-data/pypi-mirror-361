"""
test_integration.py: Integration tests for balens
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from balens import auto_balance, detect_imbalance_only, resample_only, get_weights_only


class TestAutoBalance:
    """Integration tests for auto_balance function."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        
        # Create imbalanced classification dataset
        n_samples = 200
        X = np.random.randn(n_samples, 3)
        y = np.array([0] * 160 + [1] * 40)  # 80:20 imbalance
        
        self.df_classification = pd.DataFrame(X, columns=['feature1', 'feature2', 'feature3'])
        self.df_classification['target'] = y
        
        # Create regression dataset
        X_reg = np.random.randn(100, 2)
        y_reg = np.random.normal(50, 15, 100)
        
        self.df_regression = pd.DataFrame(X_reg, columns=['feature1', 'feature2'])
        self.df_regression['target'] = y_reg
    
    def test_auto_balance_classification(self):
        """Test auto_balance with classification data."""
        X_res, y_res, info = auto_balance(
            data=self.df_classification,
            target='target',
            method='smote',
            test_size=0.2,
            random_state=42
        )
        
        # Check return types
        assert isinstance(X_res, np.ndarray)
        assert isinstance(y_res, np.ndarray)
        assert isinstance(info, dict)
        
        # Check that resampling worked
        assert X_res.shape[0] > self.df_classification.shape[0] * 0.8  # Should have more samples
        assert X_res.shape[1] == 3  # Same number of features
        
        # Check info structure
        assert 'imbalance_info' in info
        assert 'resampling_info' in info
        assert 'weights_info' in info
        assert 'test_data' in info
        
        # Check test data
        assert 'X_test' in info['test_data']
        assert 'y_test' in info['test_data']
    
    def test_auto_balance_with_export(self):
        """Test auto_balance with export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            X_res, y_res, info = auto_balance(
                data=self.df_classification,
                target='target',
                method='smote',
                test_size=0.2,
                random_state=42,
                export=True,
                output_dir=temp_dir
            )
            
            # Check that files were created
            assert 'export_info' in info
            assert 'report_path' in info
            
            # Check that files exist
            assert os.path.exists(info['export_info']['train_file'])
            assert os.path.exists(info['report_path'])
    
    def test_auto_balance_regression_with_binning(self):
        """Test auto_balance with regression data and binning."""
        X_res, y_res, info = auto_balance(
            data=self.df_regression,
            target='target',
            method='smote',
            auto_bin=True,
            bin_method='quantile',
            n_bins=3,
            test_size=0.2,
            random_state=42
        )
        
        # Check that binning was applied
        assert info['binning_info'] is not None
        assert info['binning_info']['method'] == 'quantile'
        assert info['binning_info']['n_bins'] == 3
        
        # Check that target was converted to categorical
        unique_values = np.unique(y_res)
        assert len(unique_values) <= 3  # Should be binned into 3 categories
    
    def test_auto_balance_file_path(self):
        """Test auto_balance with file path input."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.df_classification.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            X_res, y_res, info = auto_balance(
                data=temp_file,
                target='target',
                method='smote',
                test_size=0.2,
                random_state=42
            )
            
            assert isinstance(X_res, np.ndarray)
            assert isinstance(y_res, np.ndarray)
            assert info['imbalance_info']['target_column'] == 'target'
            
        finally:
            os.unlink(temp_file)
    
    def test_auto_balance_auto_target_detection(self):
        """Test auto_balance with automatic target detection."""
        X_res, y_res, info = auto_balance(
            data=self.df_classification,
            method='smote',
            test_size=0.2,
            random_state=42
        )
        
        # Should auto-detect 'target' column
        assert info['imbalance_info']['target_column'] == 'target'
    
    def test_different_resampling_methods(self):
        """Test auto_balance with different resampling methods."""
        methods = ['smote', 'adasyn', 'random_oversample']
        
        for method in methods:
            X_res, y_res, info = auto_balance(
                data=self.df_classification,
                target='target',
                method=method,
                test_size=0.2,
                random_state=42
            )
            
            assert info['resampling_info']['method'] == method
            assert X_res.shape[1] == 3  # Same number of features


def test_detect_imbalance_only():
    """Test the detect_imbalance_only function."""
    np.random.seed(42)
    df = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'target': [0] * 80 + [1] * 20
    })
    
    info = detect_imbalance_only(df, target='target')
    
    assert isinstance(info, dict)
    assert info['target_column'] == 'target'
    assert info['total_samples'] == 100
    assert info['n_classes'] == 2
    assert 'imbalance_ratio' in info
    assert 'severity' in info


def test_resample_only():
    """Test the resample_only function."""
    np.random.seed(42)
    X = np.random.randn(100, 3)
    y = np.array([0] * 80 + [1] * 20)
    
    X_res, y_res, info = resample_only(X, y, method='smote', random_state=42)
    
    assert isinstance(X_res, np.ndarray)
    assert isinstance(y_res, np.ndarray)
    assert isinstance(info, dict)
    assert info['method'] == 'smote'


def test_get_weights_only():
    """Test the get_weights_only function."""
    np.random.seed(42)
    y = np.array([0] * 70 + [1] * 30)
    
    info = get_weights_only(y, method='balanced')
    
    assert isinstance(info, dict)
    assert info['method'] == 'balanced'
    assert info['n_classes'] == 2
    assert 'class_weights' in info 