import numpy as np
import pandas as pd
import pytest
import sys
sys.path.append("../src")
from multiHGtest import from_time_to_event_to_survival_table, HCHGtest

# Try to import lifelines for the real dataset test
try:
    from lifelines.datasets import load_rossi
    LIFELINES_AVAILABLE = True
except ImportError:
    LIFELINES_AVAILABLE = False


class TestTimeToEventConversion:
    """Test cases for the from_time_to_event_to_survival_table function."""
    
    def test_basic_conversion(self):
        """Test basic conversion with simple data."""
        # Create simple test data
        data = pd.DataFrame({
            'time': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            'event': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
            'group': [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
        })
        
        result = from_time_to_event_to_survival_table(data)
        
        # Check structure
        expected_keys = ['time', 'observed_1', 'observed_2', 'censored_1', 'censored_2', 'at_risk_1', 'at_risk_2']
        assert all(key in result for key in expected_keys)
        
        # Check time points (should be [1, 2, 3, 4, 5] - all unique times)
        assert np.array_equal(result['time'], np.array([1, 2, 3, 4, 5]))
        
        # Check initial at-risk counts
        assert result['at_risk_1'][0] == 5  # 5 subjects in group 1
        assert result['at_risk_2'][0] == 5  # 5 subjects in group 2
        
        # Check events at time 1
        assert result['observed_1'][0] == 1  # 1 event in group 1 at time 1
        assert result['observed_2'][0] == 1  # 1 event in group 2 at time 1
        
        # Check at-risk counts decrease properly
        assert result['at_risk_1'][1] == 4  # 5 - 1 event = 4
        assert result['at_risk_2'][1] == 4  # 5 - 1 event = 4
    
    def test_censoring_handling(self):
        """Test that censoring is handled correctly."""
        data = pd.DataFrame({
            'time': [1, 2, 3, 1, 2, 3],
            'event': [1, 0, 1, 1, 0, 1],  # 0 = censored
            'group': [1, 1, 1, 2, 2, 2]
        })
        
        result = from_time_to_event_to_survival_table(data)
        
        # Should have 3 time points (1, 2, 3)
        assert len(result['time']) == 3
        
        # At time 2, there should be censoring
        assert result['censored_1'][1] == 1  # 1 censored in group 1 at time 2
        assert result['censored_2'][1] == 1  # 1 censored in group 2 at time 2
        
        # At-risk counts should account for both events and censoring
        assert result['at_risk_1'][2] == 1  # 3 - 1 event - 1 censored = 1
        assert result['at_risk_2'][2] == 1  # 3 - 1 event - 1 censored = 1
    
    def test_multiple_events_same_time(self):
        """Test handling of multiple events at the same time."""
        data = pd.DataFrame({
            'time': [1, 1, 2, 2, 2, 1, 1, 2, 2],
            'event': [1, 1, 1, 1, 0, 1, 1, 1, 0],
            'group': [1, 1, 1, 1, 1, 2, 2, 2, 2]
        })
        
        result = from_time_to_event_to_survival_table(data)
        
        # Should have 2 time points
        assert len(result['time']) == 2
        
        # At time 1: 2 events in group 1, 2 events in group 2
        assert result['observed_1'][0] == 2
        assert result['observed_2'][0] == 2
        
        # At time 2: 2 events in group 1, 1 event in group 2, 1 censored in group 2
        assert result['observed_1'][1] == 2
        assert result['observed_2'][1] == 1
        assert result['censored_2'][1] == 1
    
    def test_custom_column_names(self):
        """Test function with custom column names."""
        data = pd.DataFrame({
            'survival_time': [1, 2, 1, 2],
            'death': [1, 1, 1, 0],
            'treatment': ['A', 'A', 'B', 'B']
        })
        
        result = from_time_to_event_to_survival_table(
            data, 
            time_col='survival_time', 
            event_col='death', 
            group_col='treatment'
        )
        
        # Should work with custom names
        assert len(result['time']) == 2
        assert result['at_risk_1'][0] == 2  # 2 subjects in group A
        assert result['at_risk_2'][0] == 2  # 2 subjects in group B
    
    def test_no_events(self):
        """Test error handling when no events occur."""
        data = pd.DataFrame({
            'time': [1, 2, 3, 1, 2, 3],
            'event': [0, 0, 0, 0, 0, 0],  # All censored
            'group': [1, 1, 1, 2, 2, 2]
        })
        
        with pytest.raises(ValueError, match="No events found in the data"):
            from_time_to_event_to_survival_table(data)
    
    def test_invalid_input_type(self):
        """Test error handling for invalid input type."""
        with pytest.raises(ValueError, match="time_to_event_data must be a pandas DataFrame"):
            from_time_to_event_to_survival_table("not a dataframe")
    
    def test_missing_columns(self):
        """Test error handling for missing columns."""
        data = pd.DataFrame({
            'time': [1, 2, 3],
            'event': [1, 1, 1]
            # Missing group column
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            from_time_to_event_to_survival_table(data)
    
    def test_wrong_number_of_groups(self):
        """Test error handling for wrong number of groups."""
        data = pd.DataFrame({
            'time': [1, 2, 3, 1, 2, 3, 1, 2, 3],
            'event': [1, 1, 1, 1, 1, 1, 1, 1, 1],
            'group': [1, 1, 1, 2, 2, 2, 3, 3, 3]  # 3 groups instead of 2
        })
        
        with pytest.raises(ValueError, match="Group column must have exactly 2 unique values"):
            from_time_to_event_to_survival_table(data)
    
    def test_string_group_labels(self):
        """Test handling of string group labels."""
        data = pd.DataFrame({
            'time': [1, 2, 1, 2],
            'event': [1, 1, 1, 1],
            'group': ['control', 'control', 'treatment', 'treatment']
        })
        
        result = from_time_to_event_to_survival_table(data)
        
        # Should work with string labels
        assert len(result['time']) == 2
        assert result['at_risk_1'][0] == 2  # 2 control subjects
        assert result['at_risk_2'][0] == 2  # 2 treatment subjects
    
    def test_float_time_values(self):
        """Test handling of float time values."""
        data = pd.DataFrame({
            'time': [1.5, 2.3, 1.5, 2.3],
            'event': [1, 1, 1, 1],
            'group': [1, 1, 2, 2]
        })
        
        result = from_time_to_event_to_survival_table(data)
        
        # Should work with float times
        assert len(result['time']) == 2
        assert np.array_equal(result['time'], np.array([1.5, 2.3]))
    
    def test_consistency_with_existing_functions(self):
        """Test that the output is compatible with existing test functions."""
        data = pd.DataFrame({
            'time': [1, 2, 3, 4, 1, 2, 3, 4],
            'event': [1, 1, 1, 1, 1, 1, 1, 1],
            'group': [1, 1, 1, 1, 2, 2, 2, 2]
        })
        
        result = from_time_to_event_to_survival_table(data)
        
        # The output should be compatible with existing functions
        # that expect Nt1, Nt2, Ot1, Ot2 format
        Nt1 = result['at_risk_1']
        Nt2 = result['at_risk_2']
        Ot1 = result['observed_1']
        Ot2 = result['observed_2']
        
        # Basic consistency checks
        assert len(Nt1) == len(Nt2) == len(Ot1) == len(Ot2)
        assert all(n >= 0 for n in Nt1)
        assert all(n >= 0 for n in Nt2)
        assert all(o >= 0 for o in Ot1)
        assert all(o >= 0 for o in Ot2)
        
        # At-risk counts should be non-increasing
        if len(Nt1) > 1:
            assert all(Nt1[i] >= Nt1[i+1] for i in range(len(Nt1)-1))
            assert all(Nt2[i] >= Nt2[i+1] for i in range(len(Nt2)-1))
    
    @pytest.mark.skipif(not LIFELINES_AVAILABLE, reason="lifelines not available")
    def test_rossi_dataset_integration(self):
        """Test integration with real lifelines dataset and HCHG test."""
        # Load the rossi dataset from lifelines
        rossi_data = load_rossi()
        
        # Create a binary group variable based on financial aid (fin)
        # fin = 1 means they received financial aid, fin = 0 means they didn't
        rossi_data['group'] = rossi_data['fin']
        
        # Prepare data for our function
        # week = time to event, arrest = event indicator (1 = arrested, 0 = censored)
        survival_data = rossi_data[['week', 'arrest', 'group']].copy()
        survival_data.columns = ['time', 'event', 'group']
        
        # Convert to survival table format
        result = from_time_to_event_to_survival_table(survival_data)
        
        # total counts before conversion:
        total_counts_before = survival_data['event'].sum()
        total_counts_after = result['observed_1'].sum() + result['observed_2'].sum()
        assert total_counts_before == total_counts_after

        # total censored before conversion:
        total_censored_before = np.sum(survival_data['event'] == 0)
        total_censored_after = result['censored_1'].sum() + result['censored_2'].sum()
        assert total_censored_before == total_censored_after

        # Basic checks on the result
        assert len(result['time']) > 0
        assert len(result['at_risk_1']) > 0
        assert len(result['at_risk_2']) > 0
        assert len(result['observed_1']) > 0
        assert len(result['observed_2']) > 0
        
        # Check that we have data for both groups
        assert np.any(result['at_risk_1'] > 0)
        assert np.any(result['at_risk_2'] > 0)
        
        # Apply HCHG test to the converted data
        Nt1 = result['at_risk_1']
        Nt2 = result['at_risk_2']
        Ot1 = result['observed_1']
        Ot2 = result['observed_2']
        
        # Run the HCHG test
        hc_statistic = HCHGtest(Nt1, Nt2, Ot1, Ot2, alternative='two-sided')
        
        # Check that we get a valid test statistic
        assert isinstance(hc_statistic, (int, float))
        assert not np.isnan(hc_statistic)
        assert not np.isinf(hc_statistic)
        
        # Print some summary statistics for verification
        print(f"Rossi dataset analysis:")
        print(f"Total time points: {len(result['time'])}")
        print(f"Initial at-risk counts - Group 1 (no financial aid): {result['at_risk_1'][0]}")
        print(f"Initial at-risk counts - Group 2 (financial aid): {result['at_risk_2'][0]}")
        print(f"Total events - Group 1: {np.sum(result['observed_1'])}")
        print(f"Total events - Group 2: {np.sum(result['observed_2'])}")
        print(f"HCHG test statistic: {hc_statistic:.4f}")
        
        # check that total counts before conversion are the same as after conversion


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__]) 