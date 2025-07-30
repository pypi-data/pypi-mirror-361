"""
test_weights.py: Tests for balens.weights
"""

import pytest
import pandas as pd
import numpy as np
from balens.weights import compute_class_weights, get_sample_weights, get_sklearn_class_weights, ClassWeightsComputer, validate_weight_method


class TestClassWeightsComputer:
    """Test cases for ClassWeightsComputer."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        self.y_balanced = np.array([0] * 50 + [1] * 50)
        self.y_imbalanced = np.array([0] * 80 + [1] * 20)
    
    def test_balanced_weights(self):
        """Test weights computation for balanced data."""
        weights_info = compute_class_weights(self.y_balanced, method='balanced')
        
        assert weights_info['method'] == 'balanced'
        assert weights_info['n_classes'] == 2
        assert weights_info['total_samples'] == 100
        assert weights_info['weight_ratio'] == 1.0  # Should be balanced
        assert 0 in weights_info['class_weights']
        assert 1 in weights_info['class_weights']
    
    def test_imbalanced_weights(self):
        """Test weights computation for imbalanced data."""
        weights_info = compute_class_weights(self.y_imbalanced, method='balanced')
        
        assert weights_info['method'] == 'balanced'
        assert weights_info['n_classes'] == 2
        assert weights_info['total_samples'] == 100
        assert weights_info['weight_ratio'] > 1.0  # Should be imbalanced
        assert weights_info['class_weights'][1] > weights_info['class_weights'][0]  # Minority class should have higher weight
    
    def test_balanced_subsample_method(self):
        """Test balanced_subsample method."""
        weights_info = compute_class_weights(self.y_imbalanced, method='balanced_subsample')
        
        assert weights_info['method'] == 'balanced_subsample'
        assert weights_info['n_classes'] == 2
        assert weights_info['weight_ratio'] > 1.0
    
    def test_custom_weights(self):
        """Test custom weights dictionary."""
        custom_weights = {0: 1.0, 1: 2.5}
        weights_info = compute_class_weights(self.y_imbalanced, method=custom_weights)
        
        assert weights_info['method'] == custom_weights
        assert weights_info['class_weights'] == custom_weights
        assert weights_info['weight_ratio'] == 2.5
    
    def test_invalid_method(self):
        """Test handling of invalid weight method."""
        with pytest.raises(ValueError, match="Unknown weight method"):
            compute_class_weights(self.y_imbalanced, method='invalid_method')
    
    def test_pandas_series_input(self):
        """Test weights computation with pandas Series input."""
        y_series = pd.Series(self.y_imbalanced)
        weights_info = compute_class_weights(y_series, method='balanced')
        
        assert weights_info['method'] == 'balanced'
        assert weights_info['n_classes'] == 2
        assert weights_info['total_samples'] == 100
    
    def test_sample_weights_vector(self):
        """Test getting sample weights vector."""
        computer = ClassWeightsComputer()
        computer.compute_weights(self.y_imbalanced, method='balanced')
        sample_weights = computer.get_sample_weights(self.y_imbalanced)
        
        assert len(sample_weights) == len(self.y_imbalanced)
        assert isinstance(sample_weights, np.ndarray)
        assert np.all(sample_weights > 0)  # All weights should be positive
    
    def test_sklearn_weights(self):
        """Test getting sklearn-compatible weights."""
        computer = ClassWeightsComputer()
        computer.compute_weights(self.y_imbalanced, method='balanced')
        sklearn_weights = computer.get_sklearn_weights()
        
        assert isinstance(sklearn_weights, dict)
        assert 0 in sklearn_weights
        assert 1 in sklearn_weights
        assert all(isinstance(w, (int, float)) for w in sklearn_weights.values())


def test_get_sample_weights_function():
    """Test the convenience function for sample weights."""
    np.random.seed(42)
    y = np.array([0] * 70 + [1] * 30)
    
    sample_weights = get_sample_weights(y, method='balanced')
    
    assert len(sample_weights) == len(y)
    assert isinstance(sample_weights, np.ndarray)
    assert np.all(sample_weights > 0)


def test_get_sklearn_class_weights_function():
    """Test the convenience function for sklearn weights."""
    np.random.seed(42)
    y = np.array([0] * 60 + [1] * 40)
    
    sklearn_weights = get_sklearn_class_weights(y, method='balanced')
    
    assert isinstance(sklearn_weights, dict)
    assert 0 in sklearn_weights
    assert 1 in sklearn_weights


def test_validate_weight_method():
    """Test weight method validation."""
    assert validate_weight_method('balanced') == True
    assert validate_weight_method('balanced_subsample') == True
    assert validate_weight_method({0: 1.0, 1: 2.0}) == True
    assert validate_weight_method('invalid_method') == False


def test_multiclass_weights():
    """Test weights computation for multiclass data."""
    y_multiclass = np.array([0] * 50 + [1] * 30 + [2] * 20)
    
    weights_info = compute_class_weights(y_multiclass, method='balanced')
    
    assert weights_info['n_classes'] == 3
    assert weights_info['total_samples'] == 100
    assert len(weights_info['class_weights']) == 3
    assert 0 in weights_info['class_weights']
    assert 1 in weights_info['class_weights']
    assert 2 in weights_info['class_weights'] 