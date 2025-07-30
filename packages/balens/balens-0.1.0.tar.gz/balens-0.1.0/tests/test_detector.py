"""
test_detector.py: Tests for balens.detector
"""

import pytest
import pandas as pd
import numpy as np
from balens.detector import detect_imbalance, ImbalanceDetector


class TestImbalanceDetector:
    """Test cases for ImbalanceDetector."""
    
    def test_balanced_data(self):
        """Test detection on balanced data."""
        # Create balanced dataset
        data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': [0] * 50 + [1] * 50
        })
        
        result = detect_imbalance(data, target='target')
        
        assert result['severity'] == 'balanced'
        assert result['imbalance_ratio'] == 1.0
        assert result['n_classes'] == 2
        assert result['total_samples'] == 100
    
    def test_imbalanced_data(self):
        """Test detection on imbalanced data."""
        # Create imbalanced dataset
        data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': [0] * 90 + [1] * 10
        })
        
        result = detect_imbalance(data, target='target')
        
        assert result['severity'] == 'moderate'
        assert result['imbalance_ratio'] == 0.1111111111111111
        assert result['n_classes'] == 2
        assert result['total_samples'] == 100
    
    def test_auto_target_detection(self):
        """Test automatic target detection."""
        data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'target': [0] * 50 + [1] * 50
        })
        
        result = detect_imbalance(data)
        
        assert result['target_column'] == 'target'
        assert result['n_classes'] == 2
    
    def test_array_input(self):
        """Test detection with numpy array input."""
        y = np.array([0] * 80 + [1] * 20)
        
        result = detect_imbalance(y)
        
        assert result['n_classes'] == 2
        assert result['total_samples'] == 100
        assert result['imbalance_ratio'] == 0.25
    
    def test_custom_thresholds(self):
        """Test detection with custom thresholds."""
        data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'target': [0] * 70 + [1] * 30
        })
        
        result = detect_imbalance(data, target='target', 
                                threshold_severe=0.2, threshold_moderate=0.5)
        
        assert result['severity'] == 'moderate'  # 0.3/0.7 = 0.43
        assert result['imbalance_ratio'] == 0.42857142857142855


def test_detect_imbalance_function():
    """Test the convenience function."""
    data = pd.DataFrame({
        'feature1': np.random.randn(50),
        'target': [0] * 40 + [1] * 10
    })
    
    result = detect_imbalance(data, target='target')
    
    assert isinstance(result, dict)
    assert 'severity' in result
    assert 'imbalance_ratio' in result
    assert 'class_counts' in result 