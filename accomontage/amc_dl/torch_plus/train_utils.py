import numpy as np
from torch.distributions import Normal, kl_divergence
import torch


def epoch_time(start_time, end_time):
    elapsed_time = end_time - start_time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
    return elapsed_mins, elapsed_secs


def join_fn(*items, ext='pt'):
    return '.'.join(['_'.join(items), ext])


def scheduled_sampling(i, high=0.7, low=0.05):
    x = 10 * (i - 0.5)
    z = 1 / (1 + np.exp(x))
    y = (high - low) * z + low
    return y


def kl_anealing(i, high=0.1, low=0.):
    hh = 1 - low
    ll = 1 - high
    x = 10 * (i - 0.5)
    z = 1 / (1 + np.exp(x))
    y = (hh - ll) * z + ll
    return 1 - y


def get_zs_from_dists(dists, sample=False):
    return [dist.rsample() if sample else dist.mean for dist in dists]


def standard_normal(shape):
    N = Normal(torch.zeros(shape), torch.ones(shape))
    if torch.cuda.is_available():
        N.loc = N.loc.cuda()
        N.scale = N.scale.cuda()
    return N


def kl_with_normal(dist):
    shape = dist.mean.size(-1)
    normal = standard_normal(shape)
    kl = kl_divergence(dist, normal).mean()
    return kl
