"""Exact brute-force kNN under L1, ties broken by (distance, encounter id)."""
import numpy as np
from sklearn.metrics import pairwise_distances


def l1(queries: np.ndarray, data: np.ndarray) -> np.ndarray:
    return pairwise_distances(queries, data, metric="manhattan", n_jobs=1)


def brute_force_knn(queries: np.ndarray, data: np.ndarray, ids: np.ndarray, k: int,
                    chunk: int = 50):
    """Returns (neighbor row indices, distances), each of shape (n_queries, k)."""
    order = np.argsort(ids, kind="stable")  # makes stable sorts break ties by id
    rows, dists = [], []
    for start in range(0, len(queries), chunk):
        d = l1(queries[start:start + chunk], data[order])
        top = np.argsort(d, axis=1, kind="stable")[:, :k]
        rows.append(order[top])
        dists.append(np.take_along_axis(d, top, axis=1))
    return np.vstack(rows), np.vstack(dists)
