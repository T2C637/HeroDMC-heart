"""Metric and leakage tests for the encoding and brute-force oracle."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allows running this file directly

from knn import data as D
from knn.brute import brute_force_knn, l1


@pytest.fixture(scope="module")
def setup():
    df = D.load()
    idx, val, test = D.split_patients(df, seed=0)
    enc = D.Encoder().fit(df.iloc[idx])
    return df, idx, val, test, enc


def test_split_has_no_patient_overlap(setup):
    df, idx, val, test, _ = setup
    p = [set(df["patient_nbr"].iloc[x]) for x in (idx, val, test)]
    assert not (p[0] & p[1]) and not (p[0] & p[2]) and not (p[1] & p[2])


def test_metric_axioms_on_sampled_triples(setup):
    df, idx, val, _, enc = setup
    rng = np.random.default_rng(1)
    X = enc.transform(df.iloc[rng.choice(np.r_[idx[:2000], val[:200]], 300, replace=False)])
    d = l1(X, X)
    assert np.allclose(np.diag(d), 0)
    assert np.allclose(d, d.T, atol=1e-6)
    assert d.max() <= 1 + 1e-5
    for _ in range(2000):
        i, j, k = rng.integers(0, len(X), 3)
        assert d[i, k] <= d[i, j] + d[j, k] + 1e-6


def test_brute_force_self_neighbor_first(setup):
    df, idx, _, _, enc = setup
    sub = idx[:1000]
    X = enc.transform(df.iloc[sub])
    ids = df["encounter_id"].astype(int).to_numpy()[sub]
    rows, dist = brute_force_knn(X[:20], X, ids, k=5)
    assert np.allclose(dist[:, 0], 0, atol=1e-6)
    assert (np.diff(dist, axis=1) >= -1e-6).all()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
