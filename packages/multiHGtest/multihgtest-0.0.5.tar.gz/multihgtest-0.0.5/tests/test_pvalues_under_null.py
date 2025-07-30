import numpy as np
from scipy.stats import poisson

import sys
sys.path.append("../src")
from multiHGtest import hypergeom_test
from matplotlib import pyplot as plt


def sample_survival_poisson(T, N1, N2, lam0, eps, r):
    """
    Sample :T: times from two survival populations with
    initial sizes :N1: and :N2:
    In each time t and group j, the reduction `Oj` is a Poisson RV.
    Usually, the Poisson rates are identical although in :eps:
    fraction the times the Poisson rate of O2 are elevated by an
    amount controlled by :mu:.

    Args:
    -----
    :T:    number of events
    :N1:   total in group 1 at t=0
    :N2:   total in group 2 at t=0
    :eps:  fraction of non-null events
    :lam0: baseline Poisson rate
    :r:   intensity of non-null events

    Note that since we sample from two Poisson distributions
    in each 'event', there is some possibility that we draw (O1,O2) = (0,0),
    hence there is no change in that event. This situation is different
    from standard notation.

    """

    Nt1 = np.zeros(T + 1)
    Nt2 = np.zeros(T + 1)

    lam1 = lam0  # `base` Poisson rates (does not have to be fixed)
    theta = np.random.rand(T) < eps

    lam2 = lam1.copy()
    tt = np.arange(T)
    nt = 2 * N1 * N2 / (N1 + N2) * np.exp(-lam0 * tt)
    mu = r / 2 * np.log(T)
    lam2[theta] = (np.sqrt(mu / nt[theta]) + np.sqrt(lam1[theta])) ** 2  # perturbed Poisson rates

    Nt1[0] = N1
    Nt2[0] = N2

    for t in np.arange(T):
        O1 = poisson.rvs(Nt1[t] * lam1[t] * (Nt1[t] > 0))
        O2 = poisson.rvs(Nt2[t] * lam2[t] * (Nt2[t] > 0))

        Nt1[t + 1] = np.maximum(Nt1[t] - O1, 0)
        Nt2[t + 1] = np.maximum(Nt2[t] - O2, 0)
    return Nt1, Nt2


def main():
    T = 1000
    N1 = 5000
    N2 = 5000
    lam0 = np.ones(T) / T

    # sample data
    Nt1, Nt2 = sample_survival_poisson(T, N1, N2, lam0, eps=0, r=0)


    Ot1 = -np.diff(Nt1)
    Ot2 = -np.diff(Nt2)

    # evaluate test statistics
    
    Nt1 = Nt1[:-1]
    Nt2 = Nt2[:-1]

    
    pvals_2s_rnd = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2,
                           randomize=True, alternative='two-sided')
    pvals_1sg_rnd = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2,
                           randomize=True, alternative='greater')
    pvals_1sl_rnd = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2,
                           randomize=True, alternative='less')
    
    pvals_2s = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2, alternative='two-sided')
    pvals_1sg = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2, alternative='greater')
    pvals_1sl = hypergeom_test(Ot2, Nt2 + Nt1, Nt2, Ot1 + Ot2, alternative='less')

    bins = np.linspace(0, 1, 27)

    fig1, (ax1, ax2, ax3) = plt.subplots(3,1)

    ax1.hist(pvals_2s_rnd, bins, density=True)
    ax1.hlines(1, 0,1)
    ax1.set_title('two-sided')
    
    ax2.hist(pvals_1sg_rnd, bins, density=True)
    ax2.hlines(1, 0,1)
    ax2.set_title('greater')

    ax3.hist(pvals_1sl_rnd, bins, density=True)
    ax3.hlines(1, 0,1)
    ax3.set_title('less')

    fig1.suptitle('Randomized P-values')


    fig2, (ax1, ax2, ax3) = plt.subplots(3,1)
    ax1.hist(pvals_2s, bins, density=True)
    ax1.hlines(1, 0,1)
    ax1.set_title('two-sided')
    ax2.hist(pvals_1sg, bins, density=True)
    ax2.hlines(1, 0,1)
    ax2.set_title('greater')
    ax3.hist(pvals_1sl, bins, density=True)
    ax3.hlines(1, 0,1)
    ax3.set_title('less')

    fig2.suptitle('P-values')
    
    # plt.hist(pvals_1sg)
    # plt.subplot(3)
    # plt.hist(pvals_1sl)
    plt.show()



if __name__ == '__main__':
    main()
