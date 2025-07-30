"""
test_resampler.py: Tests for balens.resampler
"""

import pytest
import pandas as pd
import numpy as np
from balens.resampler import resample_data, DataResampler, get_available_methods, validate_method


class TestDataResampler:
    """Test cases for DataResampler."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        self.X = np.random.randn(100, 3)
        self.y = np.array([0] * 80 + [1] * 20)  # 80:20 imbalance
    
    def test_smote_resampling(self):
        """Test SMOTE resampling."""
        X_res, y_res, info = resample_data(self.X, self.y, method='smote', random_state=42)
        
        assert X_res.shape[0] > self.X.shape[0]  # Should add samples
        assert X_res.shape[1] == self.X.shape[1]  # Features should remain same
        assert len(y_res) == X_res.shape[0]
        assert info['method'] == 'smote'
        assert info['samples_added'] > 0
    
    def test_adasyn_resampling(self):
        """Test ADASYN resampling."""
        X_res, y_res, info = resample_data(self.X, self.y, method='adasyn', random_state=42)
        
        assert X_res.shape[0] > self.X.shape[0]
        assert X_res.shape[1] == self.X.shape[1]
        assert info['method'] == 'adasyn'
    
    def test_random_oversample(self):
        """Test random oversampling."""
        X_res, y_res, info = resample_data(self.X, self.y, method='random_oversample', random_state=42)
        
        assert X_res.shape[0] > self.X.shape[0]
        assert X_res.shape[1] == self.X.shape[1]
        assert info['method'] == 'random_oversample'
    
    def test_random_undersample(self):
        """Test random undersampling."""
        X_res, y_res, info = resample_data(self.X, self.y, method='random_undersample', random_state=42)
        
        assert X_res.shape[0] < self.X.shape[0]  # Should remove samples
        assert X_res.shape[1] == self.X.shape[1]
        assert info['method'] == 'random_undersample'
        assert info['samples_removed'] > 0
    
    def test_invalid_method(self):
        """Test handling of invalid resampling method."""
        with pytest.raises(ValueError, match="Unknown resampling method"):
            resample_data(self.X, self.y, method='invalid_method')
    
    def test_dataframe_input(self):
        """Test resampling with DataFrame input."""
        X_df = pd.DataFrame(self.X, columns=['f1', 'f2', 'f3'])
        y_series = pd.Series(self.y)
        
        X_res, y_res, info = resample_data(X_df, y_series, method='smote', random_state=42)
        
        assert isinstance(X_res, np.ndarray)
        assert isinstance(y_res, np.ndarray)
        assert info['method'] == 'smote'


def test_get_available_methods():
    """Test getting available resampling methods."""
    methods = get_available_methods()
    
    assert isinstance(methods, dict)
    assert 'smote' in methods
    assert 'adasyn' in methods
    assert 'random_oversample' in methods
    assert 'random_undersample' in methods
    assert len(methods) >= 4


def test_validate_method():
    """Test method validation."""
    assert validate_method('smote') == True
    assert validate_method('adasyn') == True
    assert validate_method('random_oversample') == True
    assert validate_method('invalid_method') == False


def test_resampling_consistency():
    """Test that resampling is consistent with same random state."""
    np.random.seed(42)
    X = np.random.randn(50, 2)
    y = np.array([0] * 40 + [1] * 10)
    
    # First run
    X_res1, y_res1, _ = resample_data(X, y, method='smote', random_state=42)
    
    # Second run with same random state
    X_res2, y_res2, _ = resample_data(X, y, method='smote', random_state=42)
    
    # Should be identical
    np.testing.assert_array_equal(X_res1, X_res2)
    np.testing.assert_array_equal(y_res1, y_res2) 