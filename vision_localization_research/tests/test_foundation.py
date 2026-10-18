"""
Foundation and Environment Verification Unit Tests.
"""
import sys
import numpy as np
import cv2

def test_python_version():
    """Verify that Python runtime is at least version 3.10."""
    assert sys.version_info >= (3, 10), f"Python version {sys.version} is older than required 3.10"

def test_numpy_operations():
    """Verify basic NumPy array operations and memory layout."""
    arr = np.zeros((100, 100), dtype=np.uint8)
    arr[25:75, 25:75] = 255
    assert arr.shape == (100, 100)
    assert np.mean(arr) > 0.0

def test_opencv_feature_detectors_available():
    """Verify that CPU-based SIFT and ORB detectors can be instantiated."""
    orb = cv2.ORB_create(nfeatures=500)
    assert orb is not None

    sift = cv2.SIFT_create(nfeatures=500)
    assert sift is not None

def test_opencv_synthetic_feature_detection():
    """Verify feature detection on a synthetic checkerboard image."""
    img = np.zeros((200, 200), dtype=np.uint8)
    # Create distinct visual corners
    img[0:100, 0:100] = 255
    img[100:200, 100:200] = 255
    
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(img, None)
    
    assert keypoints is not None
    assert len(keypoints) > 0
    assert descriptors is not None
