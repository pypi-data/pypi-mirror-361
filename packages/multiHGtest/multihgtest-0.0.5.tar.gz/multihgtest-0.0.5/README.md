# multiHGtest -- Testing for differences in survival using multiple hypergeometric P-values

This package implements the test for survival data described in 
[1] Kipnis, Galili, and Yakhini. Detecting rare and weak deviations of non-proportional hazard in survival analysis. arXiv:2310.00554. 2025.

## Overview

The multiHGtest package provides methods for comparing survival between two populations with sensitivity to rare hazard departures. The method uses exact hypergeometric tests at each time interval and combines the P-values using higher criticism or Fisher's combination test.

## Methods

- `hypergeom_test` - Exact hypergeometric test for comparing proportions
- `hchg_test` / `HCHGtest` - Higher criticism test of hypergeometric P-values 
- `fisher_hg_test` / `FisherHGtest` - Fisher combination test of hypergeometric P-values
- `hg_test_dashboard` / `testHG_dashboard` - Comprehensive dashboard with all test statistics

## Installation

```bash
pip install multiHGtest
```

## Quick Example

```python
import numpy as np
from multiHGtest import hchg_test, fisher_hg_test

# Example survival data (at-risk counts over time)
Nt1 = np.array([100, 95, 90, 85, 80])  # Group 1 at-risk counts
Nt2 = np.array([100, 92, 88, 82, 75])  # Group 2 at-risk counts

# Calculate events (if not provided)
Ot1 = -np.diff(Nt1)  # [5, 5, 5, 5]
Ot2 = -np.diff(Nt2)  # [8, 4, 6, 7]

# Run tests
hc_stat = hchg_test(Nt1[:-1], Nt2[:-1], Ot1, Ot2)
fisher_stat, fisher_pval = fisher_hg_test(Nt1[:-1], Nt2[:-1], Ot1, Ot2)

print(f"Higher Criticism statistic: {hc_stat:.4f}")
print(f"Fisher statistic: {fisher_stat:.4f}, p-value: {fisher_pval:.4f}")
```

