"""Loading, patient-grouped splitting and the weighted-L1 encoding of the mixed-type distance."""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "uci-diabetes-130-data" / "diabetic_data.csv"

MEDS = ["metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
        "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
        "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide", "examide",
        "citoglipton", "insulin", "glyburide-metformin", "glipizide-metformin",
        "glimepiride-pioglitazone", "metformin-rosiglitazone", "metformin-pioglitazone",
        "change", "diabetesMed"]

# Six equal-weight groups: (numeric/ordinal columns, nominal columns).
GROUPS = {
    "age": (["age"], []),
    "utilization": (["time_in_hospital", "num_lab_procedures", "num_procedures",
                     "num_medications", "number_outpatient", "number_emergency",
                     "number_inpatient", "number_diagnoses"], []),
    "admission": ([], ["admission_type_id", "discharge_disposition_id",
                       "admission_source_id", "medical_specialty", "payer_code"]),
    "diagnoses": ([], ["diag_1", "diag_2", "diag_3"]),
    "labs": ([], ["max_glu_serum", "A1Cresult"]),
    "medications": ([], MEDS),
}

_CHAPTERS = [(139, "infect"), (239, "neoplasm"), (279, "endocrine"), (289, "blood"),
             (319, "mental"), (389, "nervous"), (459, "circulatory"), (519, "respiratory"),
             (579, "digestive"), (629, "genitourinary"), (679, "pregnancy"), (709, "skin"),
             (739, "musculoskeletal"), (759, "congenital"), (779, "perinatal"),
             (799, "symptoms"), (999, "injury")]


def icd9_chapter(code: str) -> str:
    if code in ("?", "", "nan"):
        return "UNKNOWN"
    if code[0] in "VE":
        return code[0]
    try:
        value = float(code)
    except ValueError:
        return "OTHER"
    for upper, name in _CHAPTERS:
        if value < upper + 1:
            return name
    return "OTHER"


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA, dtype=str, keep_default_na=False)
    df["age"] = df["age"].str.extract(r"\[(\d+)-")[0].astype(float) // 10
    for col in GROUPS["utilization"][0]:
        df[col] = df[col].astype(float)
    for col in ("diag_1", "diag_2", "diag_3"):
        df[col] = df[col].map(icd9_chapter)
    for col in ("medical_specialty", "payer_code"):
        df[col] = df[col].replace("?", "UNKNOWN")
    return df


def split_patients(df: pd.DataFrame, seed: int = 0, fractions=(0.90, 0.05, 0.05)):
    """Patient-grouped index/validation/test split; returns three arrays of row positions."""
    rng = np.random.default_rng(seed)
    patients = np.sort(df["patient_nbr"].unique().to_numpy(dtype=object))
    rng.shuffle(patients)
    n_idx = int(fractions[0] * len(patients))
    n_val = int(fractions[1] * len(patients))
    parts = (patients[:n_idx], patients[n_idx:n_idx + n_val], patients[n_idx + n_val:])
    return tuple(np.flatnonzero(df["patient_nbr"].isin(p).to_numpy()) for p in parts)


def sample_queries(df: pd.DataFrame, rows: np.ndarray, n: int, seed: int = 0) -> np.ndarray:
    """One random encounter per patient among `rows`, then n of those; returns row positions."""
    rng = np.random.default_rng(seed)
    shuffled = rows[rng.permutation(len(rows))]
    first = pd.Series(shuffled).groupby(df["patient_nbr"].to_numpy()[shuffled]).first()
    picks = first.to_numpy()
    return np.sort(rng.choice(picks, size=min(n, len(picks)), replace=False))


class Encoder:
    """Maps rows to vectors whose plain L1 distance equals the mixed-type distance.

    Numeric/ordinal: |x-y| / range (range fit on the index; queries are not clipped).
    Nominal: 0/1 mismatch via one-hot coordinates scaled by half the feature weight, plus an
    "unseen" level so that categories absent from the index still differ from every seen one.
    Distance = sum over groups of (1/6) * mean over the group's features. It lies in [0, 1]
    when numeric values fall within the fitted ranges; out-of-range values are not clipped.
    Zero-range numeric features are dropped.
    """

    def fit(self, df: pd.DataFrame) -> "Encoder":
        self.numeric, self.nominal, self.weights = [], [], {}
        group_w = 1.0 / len(GROUPS)
        for nums, noms in GROUPS.values():
            nums = [c for c in nums if df[c].max() > df[c].min()]
            for c in nums + noms:
                self.weights[c] = group_w / (len(nums) + len(noms))
            self.numeric += nums
            self.nominal += noms
        self.lo = df[self.numeric].min().to_numpy(float)
        self.range = df[self.numeric].max().to_numpy(float) - self.lo
        self.levels = {c: np.array(sorted(df[c].unique())) for c in self.nominal}
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        num = df[self.numeric].to_numpy(float)
        w_num = np.array([self.weights[c] for c in self.numeric])
        blocks = [(num - self.lo) / self.range * w_num]
        for c in self.nominal:
            onehot = df[c].to_numpy()[:, None] == self.levels[c][None, :]
            unseen = ~onehot.any(axis=1, keepdims=True)
            blocks.append(np.hstack([onehot, unseen]) * (self.weights[c] / 2.0))
        return np.hstack(blocks).astype(np.float32)
