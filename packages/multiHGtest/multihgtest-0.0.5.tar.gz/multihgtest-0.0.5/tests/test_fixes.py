import numpy as np
import pytest
import sys
sys.path.append("../src")
from multiHGtest import hypergeom_test, hchg_test, fisher_hg_test, hg_test_dashboard

def test_hypergeom_test_array_inputs():
    """Test that hypergeom_test handles array inputs correctly"""
    k = np.array([5, 10, 15])
    M = np.array([100, 100, 100])
    n = np.array([50, 50, 50])
    N = np.array([20, 20, 20])
    
    # Test that it doesn't crash with arrays
    result = hypergeom_test(k, M, n, N, alternative='greater')
    assert len(result) == 3
    assert all(0 <= p <= 1 for p in result)

def test_hypergeom_test_randomization():
    """Test that randomization works correctly"""
    k = np.array([5, 10])
    M = np.array([100, 100])
    n = np.array([50, 50])
    N = np.array([20, 20])
    
    # Test with and without randomization
    result1 = hypergeom_test(k, M, n, N, alternative='greater', randomize=False)
    result2 = hypergeom_test(k, M, n, N, alternative='greater', randomize=True)
    
    # Results should be different when randomized
    assert not np.allclose(result1, result2)

def test_two_sided_test():
    """Test that two-sided test works correctly"""
    k = np.array([5])
    M = np.array([100])
    n = np.array([50])
    N = np.array([20])
    
    # Test all alternatives
    greater = hypergeom_test(k, M, n, N, alternative='greater')
    less = hypergeom_test(k, M, n, N, alternative='less')
    two_sided = hypergeom_test(k, M, n, N, alternative='two-sided')
    
    assert all(0 <= p <= 1 for p in [greater, less, two_sided])

def test_hchg_test_with_arrays():
    """Test hchg_test with numpy arrays"""
    Nt1 = np.array([110, 105, 100, 95])  # 4 elements
    Nt2 = np.array([100, 95, 90, 85])    # 4 elements
    Ot1 = np.array([5, 5, 5, 3])            # 3 elements, 110-105=5, 105-100=5, 100-95=5
    Ot2 = np.array([5, 5, 5, 3])            # 3 elements, 100-95=5, 95-90=5, 90-85=5
    # All arrays are compatible, so after alignment, len(Ot1) == len(Nt1) - 1, etc.
    hc_greater = hchg_test(Nt1, Nt2, Ot1, Ot2, alternative='greater')
    hc_less = hchg_test(Nt1, Nt2, Ot1, Ot2, alternative='less')
    hc_two_sided = hchg_test(Nt1, Nt2, Ot1, Ot2, alternative='two-sided')
    assert isinstance(hc_greater, (int, float))
    assert isinstance(hc_less, (int, float))
    assert isinstance(hc_two_sided, (int, float))

def test_fisher_hg_test():
    """Test fisher_hg_test"""
    Nt1 = np.array([100, 95, 90, 85])
    Nt2 = np.array([100, 92, 88, 82])
    Ot1 = np.array([5, 5, 5, 3])
    Ot2 = np.array([8, 4, 6, 3])
    
    fisher_stat, fisher_pval = fisher_hg_test(Nt1, Nt2, Ot1, Ot2)
    
    assert isinstance(fisher_stat, (int, float))
    assert isinstance(fisher_pval, (int, float))
    assert 0 <= fisher_pval <= 1

def test_hg_test_dashboard():
    """Test hg_test_dashboard"""
    Nt1 = np.array([100, 95, 90, 85])
    Nt2 = np.array([100, 92, 88, 82])
    Ot1 = np.array([5, 5, 5, 3])
    Ot2 = np.array([8, 4, 6, 3])
    
    df, stats = hg_test_dashboard(Nt1, Nt2, Ot1, Ot2)
    
    # Check DataFrame structure
    assert 'at-risk1' in df.columns
    assert 'at-risk2' in df.columns
    assert 'events1' in df.columns
    assert 'events2' in df.columns
    assert 'pvalue' in df.columns
    assert 'HCT' in df.columns
    
    # Check stats dictionary
    assert 'hc' in stats
    assert 'fisher' in stats
    assert 'fisher_pval' in stats
    assert 'minP' in stats

def test_backward_compatibility():
    """Test that old function names still work"""
    import multiHGtest
    
    # Test that aliases exist
    assert hasattr(multiHGtest, 'HCHGtest')
    assert hasattr(multiHGtest, 'FisherHGtest')
    assert hasattr(multiHGtest, 'testHG_dashboard')
    
    # Test that they work
    Nt1 = np.array([100, 95, 90, 85])
    Nt2 = np.array([100, 92, 88, 82])
    Ot1 = np.array([5, 5, 5, 3])
    Ot2 = np.array([8, 4, 6, 3])
    
    hc = multiHGtest.HCHGtest(Nt1, Nt2, Ot1, Ot2)
    fisher = multiHGtest.FisherHGtest(Nt1, Nt2, Ot1, Ot2)
    dashboard = multiHGtest.testHG_dashboard(Nt1, Nt2, Ot1, Ot2)
    
    assert isinstance(hc, (int, float))
    assert len(fisher) == 2
    assert len(dashboard) == 2

def test_input_validation():
    """Test input validation"""
    # Test shape mismatch
    k = np.array([5, 10])
    M = np.array([100, 100, 100])  # Different shape
    n = np.array([50, 50])
    N = np.array([20, 20])
    
    with pytest.raises(ValueError):
        hypergeom_test(k, M, n, N)

def test_event_count_vs_at_risk_difference():
    """Test that Ot1[i] <= Nt1[i] - Nt1[i+1] and Ot2[i] <= Nt2[i] - Nt2[i+1]"""
    import multiHGtest
    # Valid case
    Nt1 = np.array([100, 90, 80, 70])
    Nt2 = np.array([100, 85, 75, 60])
    Ot1 = np.array([10, 10, 10, 8])  
    Ot2 = np.array([15, 10, 15, 15]) 
    # Should not raise
    multiHGtest.hchg_test(Nt1, Nt2, Ot1, Ot2)
    # Invalid case: Ot1[1] > Nt1[1] - Nt1[2]
    Ot1_invalid = np.array([10, 20, 10, 8])  # 20 > 90-80=10
    try:
        multiHGtest.hchg_test(Nt1, Nt2, Ot1_invalid, Ot2)
        assert False, "Should have raised ValueError for Ot1 > at-risk difference"
    except ValueError as e:
        assert "cannot exceed the reduction" in str(e)
    # Invalid case: Ot2[2] > Nt2[2] - Nt2[3]
    Ot2_invalid = np.array([15, 10, 20, 15])  # 20 > 75-60=15
    try:
        multiHGtest.hchg_test(Nt1, Nt2, Ot1, Ot2_invalid)
        assert False, "Should have raised ValueError for Ot2 > at-risk difference"
    except ValueError as e:
        assert "cannot exceed the reduction" in str(e)

if __name__ == "__main__":
    # Run all tests
    test_hypergeom_test_array_inputs()
    test_hypergeom_test_randomization()
    test_two_sided_test()
    test_hchg_test_with_arrays()
    test_fisher_hg_test()
    test_hg_test_dashboard()
    test_backward_compatibility()
    test_input_validation()
    #test_event_count_vs_at_risk_difference()
    print("All tests passed!") 