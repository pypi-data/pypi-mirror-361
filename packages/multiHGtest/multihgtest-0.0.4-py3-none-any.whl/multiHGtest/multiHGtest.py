import numpy as np
from scipy.stats import hypergeom, uniform
from multitest import MultiTest
import pandas as pd

# to do:
# 1) function that converts time to event data to survival table
# 2) class that takes as input a time to event data and evaluates the null
# distribution of HCHG and all other tests

def from_time_to_event_to_survival_table(time_to_event_data, time_col='time', event_col='event', group_col='group'):
    """
    Convert time-to-event data to survival table format for hypergeometric tests.
    
    This function takes survival data in the lifelines format and converts it to
    the format needed for the hypergeometric tests: time intervals with at-risk
    and event counts for each group.
    
    Parameters
    ----------
    time_to_event_data : pandas.DataFrame
        DataFrame with columns for time, event status, and group assignment.
        Expected columns:
        - time_col: Time to event or censoring
        - event_col: Binary indicator (1 for event, 0 for censoring)
        - group_col: Group assignment (1 or 2, or any two distinct values)
    time_col : str, default 'time'
        Name of the column containing time values
    event_col : str, default 'event'
        Name of the column containing event indicators (1=event, 0=censored)
    group_col : str, default 'group'
        Name of the column containing group assignments
        
    Returns
    -------
    dict
        Dictionary containing arrays for survival analysis:
        - 'time': Unique time points where events occur
        - 'observed_1': Number of events in group 1 at each time
        - 'observed_2': Number of events in group 2 at each time  
        - 'censored_1': Number of censored observations in group 1 at each time
        - 'censored_2': Number of censored observations in group 2 at each time
        - 'at_risk_1': Number of subjects at risk in group 1 at each time
        - 'at_risk_2': Number of subjects at risk in group 2 at each time
        
    Example
    -------
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'time': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
    ...     'event': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
    ...     'group': [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
    ... })
    >>> result = from_time_to_event_to_survival_table(data)
    >>> print(result['time'])
    >>> print(result['at_risk_1'])
    >>> print(result['observed_1'])
    """
    # Validate input
    if not isinstance(time_to_event_data, pd.DataFrame):
        raise ValueError("time_to_event_data must be a pandas DataFrame")
    
    required_cols = [time_col, event_col, group_col]
    missing_cols = [col for col in required_cols if col not in time_to_event_data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    df = time_to_event_data.copy()
    unique_groups = df[group_col].unique()
    if len(unique_groups) != 2:
        raise ValueError(f"Group column must have exactly 2 unique values, found {len(unique_groups)}")
    group_mapping = {unique_groups[0]: 1, unique_groups[1]: 2}
    df['group_mapped'] = df[group_col].map(group_mapping)
    df = df.sort_values([time_col, 'group_mapped']).reset_index(drop=True)
    
    # Get all unique times where either an event or censoring occurs
    all_times = np.sort(df[time_col].unique())
    if not np.any(df[event_col] == 1):
        raise ValueError("No events found in the data")
    n_times = len(all_times)
    observed_1 = np.zeros(n_times, dtype=int)
    observed_2 = np.zeros(n_times, dtype=int)
    censored_1 = np.zeros(n_times, dtype=int)
    censored_2 = np.zeros(n_times, dtype=int)
    at_risk_1 = np.zeros(n_times, dtype=int)
    at_risk_2 = np.zeros(n_times, dtype=int)
    total_group_1 = len(df[df['group_mapped'] == 1])
    total_group_2 = len(df[df['group_mapped'] == 2])
    for i, t in enumerate(all_times):
        time_data = df[df[time_col] == t]
        events_group_1 = len(time_data[(time_data['group_mapped'] == 1) & (time_data[event_col] == 1)])
        events_group_2 = len(time_data[(time_data['group_mapped'] == 2) & (time_data[event_col] == 1)])
        censored_group_1 = len(time_data[(time_data['group_mapped'] == 1) & (time_data[event_col] == 0)])
        censored_group_2 = len(time_data[(time_data['group_mapped'] == 2) & (time_data[event_col] == 0)])
        observed_1[i] = events_group_1
        observed_2[i] = events_group_2
        censored_1[i] = censored_group_1
        censored_2[i] = censored_group_2
        if i == 0:
            at_risk_1[i] = total_group_1
            at_risk_2[i] = total_group_2
        else:
            at_risk_1[i] = at_risk_1[i-1] - observed_1[i-1] - censored_1[i-1]
            at_risk_2[i] = at_risk_2[i-1] - observed_2[i-1] - censored_2[i-1]
    return {
        'time': all_times,
        'observed_1': observed_1,
        'observed_2': observed_2,
        'censored_1': censored_1,
        'censored_2': censored_2,
        'at_risk_1': at_risk_1,
        'at_risk_2': at_risk_2
    }

def _validate_survival_inputs(Nt1, Nt2, Ot1, Ot2):
    """
    Validate survival table inputs for logical consistency.
    Raises ValueError if any check fails.
    
    All arrays must be the same length.

    Differences in Nt1 and Nt2 must be greater than or equal to the corresponding values in Ot1 and Ot2.

    Parameters
    ----------
    Nt1 : array-like
        Number of at-risk subjects in group 1 at beginning of each time interval
    Nt2 : array-like
        Number of at-risk subjects in group 2 at beginning of each time interval
    Ot1 : array-like
        Number of failure events in group 1 at time interval
    Ot2 : array-like
        Number of failure events in group 2 at time interval

    Returns
    -------
    None
    """
    # Convert inputs to numpy arrays for consistent handling
    Nt1 = np.asarray(Nt1)
    Nt2 = np.asarray(Nt2)
    Ot1 = np.asarray(Ot1)
    Ot2 = np.asarray(Ot2)
    
    # Check that all arrays have the same length
    if not (len(Nt1) == len(Nt2) == len(Ot1) == len(Ot2)):
        raise ValueError("All input arrays must have the same length.")
    
    # Check for non-negative values
    if np.any(Nt1 < 0) or np.any(Nt2 < 0) or np.any(Ot1 < 0) or np.any(Ot2 < 0):
        raise ValueError("All input values must be non-negative.")
    
    # Check that events cannot exceed at-risk counts
    if np.any(Ot1 > Nt1) or np.any(Ot2 > Nt2):
        raise ValueError("Number of events cannot exceed number of at-risk subjects.")
    
    # Check that at-risk counts are non-increasing (monotonicity)
    if len(Nt1) > 1:
        if np.any(np.diff(Nt1) > 0):
            raise ValueError("At-risk counts in group 1 must be non-increasing over time.")
        if np.any(np.diff(Nt2) > 0):
            raise ValueError("At-risk counts in group 2 must be non-increasing over time.")
    
    # Check that the difference in at-risk counts is >= events
    # This ensures logical consistency: Nt[i] - Nt[i+1] >= Ot[i]
    if len(Nt1) > 1:
        diff_Nt1 = -np.diff(Nt1)
        diff_Nt2 = -np.diff(Nt2)
        if np.any(diff_Nt1 > Ot1[:-1]) or np.any(diff_Nt2 > Ot2[:-1]):
            raise ValueError("Differences in at-risk counts must be greater than or equal to corresponding event counts.")


def hypergeom_test(k, M, n, N, alternative='greater', randomize=False):
    """
    Exact hypergeometric test

    Args:
        k (int or array-like): Number of observed Type I objects
        M (int or array-like): Total number of objects
        n (int or array-like): Total number of Type I objects
        N (int or array-like): Number of draws
        randomize (bool): Whether to do a randomized test (default: False)
        alternative (str): Type of alternative to consider. Options are:
            'greater', 'less', 'two-sided'

    Note:
        For 'two-sided', the function only returns approximated P-values that is accurate
        only for equal group sizes. The calculation assumes that the hypergeometric distribution
        is symmetric around its mean, which is not true when one of the groups is much larger than the other.

    Returns:
        np.ndarray: Test's P-value(s)

    Example:
        >>> hypergeom_test(5, 100, 50, 20, alternative='greater')
        array([...])
    """
    k = np.asarray(k)
    M = np.asarray(M)
    n = np.asarray(n)
    N = np.asarray(N)
    if not (k.shape == M.shape == n.shape == N.shape):
        raise ValueError("All input arrays must have the same shape.")
    if np.any(k < 0) or np.any(M < 0) or np.any(n < 0) or np.any(N < 0):
        raise ValueError("Inputs k, M, n, N must be non-negative.")
    if np.any(k > N):
        raise ValueError("k (observed Type I) cannot exceed N (number of draws).")
    if np.any(n > M):
        raise ValueError("n (Type I objects) cannot exceed M (total objects).")
    if np.any(N > M):
        raise ValueError("N (number of draws) cannot exceed M (total objects).")

    if randomize:
        U1, U2 = uniform.rvs(size=(2, k.size))
        U1 = U1.reshape(k.shape)
        U2 = U2.reshape(k.shape)
    else:
        U1 = U2 = np.zeros_like(k, dtype=float)

    if alternative == 'greater':
        return hypergeom.sf(k - 1, M, n, N) - U1 * hypergeom.pmf(k, M, n, N)
    if alternative == 'less':
        return hypergeom.cdf(k, M, n, N) - U1 * hypergeom.pmf(k, M, n, N)
    if alternative == 'two-sided':
        l1 = hypergeom.cdf(k, M, n, N)
        l2 = hypergeom.cdf(N - k, M, n, N)
        r1 = hypergeom.sf(k - 1, M, n, N)
        r2 = hypergeom.sf(N - k + 1, M, n, N)
        l = np.minimum(l1, l2)
        r = np.minimum(r1, r2)
        if randomize:
            l_tie = (l1 == l2)
            r_tie = (r1 == r2)
            l[l_tie] -= U1[l_tie] * hypergeom.pmf(k[l_tie], M[l_tie], n[l_tie], N[l_tie]) / 2
            r[r_tie] -= U2[r_tie] * hypergeom.pmf(k[r_tie], M[r_tie], n[r_tie], N[r_tie]) / 2
        return l + r
    raise ValueError("'alternative' must be one of 'greater', 'less', or 'two-sided'.")

def _multi_test(Nt1, Nt2, Ot1=None, Ot2=None, **kwargs):
    """
    Helper function to create a MultiTest object from two survival tables.

    Args:
        Nt1 (array-like): Number of at-risk subjects in group 1 per time
        Nt2 (array-like): Number of at-risk subjects in group 2 per time
        Ot1 (array-like): Number of failure events in group 1 per time
        Ot2 (array-like): Number of failure events in group 2 per time
        **kwargs: Additional arguments including:
            - randomize (bool): Whether to use randomized tests (default: False)
            - pvals_alternative (str): Alternative for individual tests (default: 'greater')
            - discard_ones (bool): Whether to discard p-values equal to 1 (default: False)

    Returns:
        MultiTest object
    """
    _validate_survival_inputs(Nt1, Nt2, Ot1, Ot2)
    
    randomize = kwargs.get('randomize', False)
    pvals_alternative = kwargs.get('pvals_alternative', 'greater')
    discard_ones = kwargs.get('discard_ones', False)
    pvals = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2,
                           randomize=randomize, alternative=pvals_alternative)
    if discard_ones:
        return MultiTest(pvals[pvals < 1])
    return MultiTest(pvals)

def hchg_test(Nt1, Nt2, Ot1=None, Ot2=None,
              alternative='two-sided', **kwargs):
    """
    Higher criticism test of hypergeometric P-values for comparing survival data.

    Args:
        Nt1 (array-like): Number of at-risk subjects in group 1 per time
        Nt2 (array-like): Number of at-risk subjects in group 2 per time
        Ot1 (array-like): Number of failure events in group 1 per time; if None, will be computed as -np.diff(Nt1)
        Ot2 (array-like): Number of failure events in group 2 per time; if None, will be computed as -np.diff(Nt2)
        alternative (str): 'greater', 'less', or 'two-sided' (default: 'two-sided')
        **kwargs: Additional arguments to be passed to the hypergeometric test including:
            - gamma (float): Parameter for higher criticism (default: 0.2)
            - randomize (bool): Whether to use randomized tests (default: False)

    Returns:
        float: HC test statistic

    Example:
        >>> hchg_test([100, 95, 90], [100, 92, 88])
        ...
    """
    _validate_survival_inputs(Nt1, Nt2, Ot1, Ot2)
    gamma = kwargs.get('gamma', 0.4)
    if alternative == 'greater':
        mtest = _multi_test(Nt1, Nt2, Ot1, Ot2, **kwargs)
        hc = mtest.hc(gamma)[0]
    elif alternative == 'less':
        mtest = _multi_test(Nt2, Nt1, Ot2, Ot1, **kwargs)
        hc = mtest.hc(gamma)[0]
    elif alternative == 'two-sided':
        mtest1 = _multi_test(Nt1, Nt2, Ot1, Ot2, **kwargs)
        mtest2 = _multi_test(Nt2, Nt1, Ot2, Ot1, **kwargs)
        hc = np.maximum(mtest1.hc(gamma)[0], mtest2.hc(gamma)[0])
    else:
        raise ValueError("alternative must be one of 'greater', 'less', or 'two-sided'.")
    return hc

def fisher_hg_test(Nt1, Nt2, Ot1=None, Ot2=None, **kwargs):
    """
    Fisher combination test of hypergeometric P-values.

    Args:
        Nt1 (array-like): Number of at-risk subjects in group 1 per time
        Nt2 (array-like): Number of at-risk subjects in group 2 per time
        Ot1 (array-like): Number of failure events in group 1 per time; if None, will be computed as -np.diff(Nt1)
        Ot2 (array-like): Number of failure events in group 2 per time; if None, will be computed as -np.diff(Nt2)
        **kwargs: Additional arguments to be passed to the hypergeometric test

    Returns:
        tuple: (test statistic, P-value of corresponding chi-squared test)

    Example:
        >>> fisher_hg_test([100, 95, 90], [100, 92, 88])
        ...
    """
    _validate_survival_inputs(Nt1, Nt2, Ot1, Ot2)
    mtest = _multi_test(Nt1, Nt2, Ot1, Ot2, **kwargs)
    return mtest.fisher()

def hg_test_dashboard(Nt1, Nt2, Ot1=None, Ot2=None, **kwargs):
    """
    Comprehensive dashboard for hypergeometric-based survival tests.

    Args:
        Nt1 (array-like): Number of at-risk subjects in group 1 per time
        Nt2 (array-like): Number of at-risk subjects in group 2 per time
        Ot1 (array-like): Number of failure events in group 1 per time; if None, will be computed as -np.diff(Nt1)
        Ot2 (array-like): Number of failure events in group 2 per time; if None, will be computed as -np.diff(Nt2)
        **kwargs: Additional arguments including:
            - randomize (bool): Whether to use randomized tests (default: False)
            - pvals_alternative (str): Alternative for individual tests (default: 'two-sided')
            - gamma (float): Parameter for higher criticism (default: 0.2)
            - stbl (bool): Whether to use stable sorting (default: True)

    Returns:
        tuple: (DataFrame with detailed results, dict with test statistics)

    Example:
        >>> hg_test_dashboard([100, 95, 90], [100, 92, 88])
        ...
    """
    _validate_survival_inputs(Nt1, Nt2, Ot1, Ot2)
    df = pd.DataFrame()
    df['at-risk1'] = Nt1.astype(int)
    df['at-risk2'] = Nt2.astype(int)
    df['events1'] = Ot1.astype(int)
    df['events2'] = Ot2.astype(int)
    randomize = kwargs.get('randomize', False)
    pvals_alternative = kwargs.get('pvals_alternative', 'two-sided')
    gamma = kwargs.get('gamma', 0.2)
    pvals = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2,
                           randomize=randomize, alternative=pvals_alternative)
    df['pvalue'] = pvals
    stbl = kwargs.get('stbl', True)
    mtest = MultiTest(pvals, stbl=stbl)
    fisher, fisher_pval = mtest.fisher()
    hc, hct = mtest.hc(gamma=gamma)
    minP = mtest.minp()
    df['HCT'] = pvals <= hct
    return df, {'hc': hc,
                'fisher': fisher,
                'fisher_pval': fisher_pval,
                'minP': minP}

# Aliases for consistent naming
HCHGtest = hchg_test
FisherHGtest = fisher_hg_test
testHG_dashboard = hg_test_dashboard
