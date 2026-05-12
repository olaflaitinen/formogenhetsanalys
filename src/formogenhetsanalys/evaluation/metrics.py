"""Evaluation metrics for wealth-estimation and link-prediction tasks."""

from __future__ import annotations

from typing import Any

import numpy as np


def reconstruction_mae(
    true: np.ndarray[Any, np.dtype[np.float64]],
    pred: np.ndarray[Any, np.dtype[np.float64]],
) -> float:
    """Mean absolute error of wealth reconstruction.

    Args:
        true: 1-D array of true wealth values.
        pred: 1-D array of predicted wealth values.

    Returns:
        Mean absolute error (non-negative scalar).

    Examples:
        >>> import numpy as np
        >>> reconstruction_mae(np.array([1.0, 2.0, 3.0]), np.array([1.5, 2.0, 2.5]))
        0.3333333333333333
    """
    t = np.asarray(true, dtype=np.float64)
    p = np.asarray(pred, dtype=np.float64)
    return float(np.mean(np.abs(t - p)))


def kendall_tau_ranking(
    true: np.ndarray[Any, np.dtype[np.float64]],
    pred: np.ndarray[Any, np.dtype[np.float64]],
) -> float:
    """Kendall tau rank-correlation between true and predicted wealth rankings.

    Args:
        true: 1-D array of true wealth values.
        pred: 1-D array of predicted wealth values.

    Returns:
        Kendall tau in [-1, 1].

    Examples:
        >>> import numpy as np
        >>> kendall_tau_ranking(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]))
        1.0
    """
    from scipy.stats import kendalltau

    result = kendalltau(true, pred)
    return float(result.statistic)


def roc_auc_link_prediction(
    labels: np.ndarray[Any, np.dtype[np.int64]],
    scores: np.ndarray[Any, np.dtype[np.float64]],
) -> float:
    """ROC-AUC for binary link-prediction (1 = positive edge, 0 = negative).

    Args:
        labels: 1-D integer array of true labels (0 or 1).
        scores: 1-D float array of predicted probabilities or scores.

    Returns:
        ROC-AUC score in [0, 1].

    Examples:
        >>> import numpy as np
        >>> labels = np.array([1, 1, 0, 0])
        >>> scores = np.array([0.9, 0.8, 0.2, 0.1])
        >>> roc_auc_link_prediction(labels, scores)
        1.0
    """
    from sklearn.metrics import roc_auc_score

    return float(roc_auc_score(labels, scores))


def coverage(
    true: np.ndarray[Any, np.dtype[np.float64]],
    lo: np.ndarray[Any, np.dtype[np.float64]],
    hi: np.ndarray[Any, np.dtype[np.float64]],
) -> float:
    """Empirical coverage of prediction intervals.

    Args:
        true: 1-D array of true values.
        lo: 1-D array of lower interval bounds.
        hi: 1-D array of upper interval bounds.

    Returns:
        Fraction of true values inside [lo, hi].

    Examples:
        >>> import numpy as np
        >>> coverage(np.array([1.0, 2.0, 3.0]),
        ...          np.array([0.5, 1.5, 2.0]),
        ...          np.array([1.5, 2.5, 4.0]))
        1.0
    """
    t = np.asarray(true, dtype=np.float64)
    lo_arr = np.asarray(lo, dtype=np.float64)
    h = np.asarray(hi, dtype=np.float64)
    return float(np.mean((t >= lo_arr) & (t <= h)))


def interval_width(
    lo: np.ndarray[Any, np.dtype[np.float64]],
    hi: np.ndarray[Any, np.dtype[np.float64]],
) -> float:
    """Mean width of prediction intervals.

    Args:
        lo: 1-D array of lower bounds.
        hi: 1-D array of upper bounds.

    Returns:
        Mean interval width.

    Examples:
        >>> import numpy as np
        >>> interval_width(np.array([0.0, 1.0]), np.array([1.0, 3.0]))
        1.5
    """
    return float(np.mean(np.asarray(hi, dtype=np.float64) - np.asarray(lo, dtype=np.float64)))
