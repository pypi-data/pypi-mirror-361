"""
test_binning.py: Tests for balens.binning
"""

import pytest
import pandas as pd
import numpy as np
from balens.binning import bin_regression_target, SmartBinner


class TestSmartBinner:
    """Test cases for SmartBinner."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        self.y_regression = np.random.normal(50, 15, 100)
    
    def test_quantile_binning(self):
        """Test quantile-based binning."""
        binned, info = bin_regression_target(self.y_regression, method='quantile', n_bins=3)
        
        assert len(binned) == len(self.y_regression)
        assert info['method'] == 'quantile'
        assert info['n_bins'] == 3
        assert info['bin_labels'] == ['Low', 'Medium', 'High']
        assert len(info['bin_counts']) == 3
    
    def test_uniform_binning(self):
        """Test uniform binning."""
        binned, info = bin_regression_target(self.y_regression, method='uniform', n_bins=4)
        
        assert len(binned) == len(self.y_regression)
        assert info['method'] == 'uniform'
        assert info['n_bins'] == 4
        assert info['bin_labels'] == ['Low', 'Medium', 'High', 'Very_High']
    
    def test_custom_thresholds(self):
        """Test custom threshold binning."""
        thresholds = [30, 60]
        binned, info = bin_regression_target(self.y_regression, custom_thresholds=thresholds)
        
        assert len(binned) == len(self.y_regression)
        assert info['method'] == 'custom'
        assert info['n_bins'] == 3  # 2 thresholds create 3 bins
        assert len(info['bin_edges']) == 4  # min, 30, 60, max
    
    def test_custom_labels(self):
        """Test binning with custom labels."""
        custom_labels = ['Small', 'Medium', 'Large']
        binned, info = bin_regression_target(self.y_regression, method='quantile', n_bins=3, labels=custom_labels)
        
        assert info['bin_labels'] == custom_labels
        assert set(binned) == set(custom_labels)
    
    def test_invalid_method(self):
        """Test handling of invalid binning method."""
        with pytest.raises(ValueError, match="Method must be 'quantile' or 'uniform'"):
            bin_regression_target(self.y_regression, method='invalid_method')
    
    def test_label_count_mismatch(self):
        """Test handling of label count mismatch."""
        with pytest.raises(ValueError, match="Number of labels"):
            bin_regression_target(self.y_regression, method='quantile', n_bins=3, labels=['A', 'B'])
    
    def test_pandas_series_input(self):
        """Test binning with pandas Series input."""
        y_series = pd.Series(self.y_regression)
        binned, info = bin_regression_target(y_series, method='quantile', n_bins=3)
        
        assert len(binned) == len(y_series)
        assert info['method'] == 'quantile'
    
    def test_bin_statistics(self):
        """Test getting bin statistics."""
        binner = SmartBinner()
        binned, _ = binner.bin_regression_target(self.y_regression, method='quantile', n_bins=3)
        stats = binner.get_bin_statistics(self.y_regression)
        
        assert isinstance(stats, dict)
        assert len(stats) == 3  # 3 bins
        for bin_name, bin_stats in stats.items():
            assert 'count' in bin_stats
            assert 'mean' in bin_stats
            assert 'std' in bin_stats
            assert 'min' in bin_stats
            assert 'max' in bin_stats


def test_bin_regression_target_function():
    """Test the convenience function."""
    np.random.seed(42)
    y = np.random.normal(0, 1, 50)
    
    binned, info = bin_regression_target(y, method='quantile', n_bins=3)
    
    assert isinstance(binned, np.ndarray)
    assert isinstance(info, dict)
    assert 'method' in info
    assert 'n_bins' in info
    assert 'bin_labels' in info 