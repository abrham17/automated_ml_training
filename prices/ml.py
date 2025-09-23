from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
from django.conf import settings
from joblib import dump, load
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


MODEL_FILENAME = "price_model.joblib"
DATA_FILENAME = "prices.csv"


FEATURE_NAMES: List[str] = [
    "size",        # square meters
    "bedrooms",    # count
    "bathrooms",   # count
    "age"          # years
]


@dataclass
class PredictionInput:
    size: float
    bedrooms: int
    bathrooms: int
    age: float

    def to_row(self) -> List[float]:
        return [self.size, self.bedrooms, self.bathrooms, self.age]


def _ensure_dirs() -> None:
    os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)


def _model_path() -> str:
    return str(settings.ARTIFACTS_DIR / MODEL_FILENAME)


def _data_path() -> str:
    return str(settings.DATA_DIR / DATA_FILENAME)


def _generate_synthetic_rows(num_rows: int) -> pd.DataFrame:
    rng = np.random.default_rng()
    size = rng.normal(loc=120.0, scale=40.0, size=num_rows).clip(min=20)
    bedrooms = rng.integers(low=1, high=6, size=num_rows)
    bathrooms = rng.integers(low=1, high=5, size=num_rows)
    age = rng.normal(loc=20.0, scale=15.0, size=num_rows).clip(min=0)

    # True underlying relationship (unknown in practice)
    price = (
        1500.0 * size
        + 10000.0 * bedrooms
        + 8000.0 * bathrooms
        - 500.0 * age
        + rng.normal(0, 50000.0, size=num_rows)
    )

    df = pd.DataFrame(
        {
            "size": size,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "age": age,
            "price": price,
        }
    )
    return df


def _load_or_create_dataset(initial_rows: int = 1000) -> pd.DataFrame:
    _ensure_dirs()
    path = _data_path()
    if os.path.exists(path):
        return pd.read_csv(path)
    df = _generate_synthetic_rows(initial_rows)
    df.to_csv(path, index=False)
    return df


def augment_dataset_with_synthetic(num_new_rows: int = 200) -> pd.DataFrame:
    df_existing = _load_or_create_dataset()
    df_new = _generate_synthetic_rows(num_new_rows)
    df_all = pd.concat([df_existing, df_new], ignore_index=True)
    df_all.to_csv(_data_path(), index=False)
    return df_all


def train_and_save_model(df: pd.DataFrame | None = None) -> str:
    _ensure_dirs()
    if df is None:
        df = _load_or_create_dataset()

    X = df[FEATURE_NAMES]
    y = df["price"]

    numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])
    preprocessor = ColumnTransformer(
        transformers=[("num", numeric_transformer, FEATURE_NAMES)],
        remainder="drop",
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("regressor", LinearRegression()),
        ]
    )

    model.fit(X, y)
    model_path = _model_path()
    dump(model, model_path)
    return model_path


def load_model_or_train() -> Pipeline:
    _ensure_dirs()
    model_path = _model_path()
    if os.path.exists(model_path):
        return load(model_path)
    train_and_save_model()
    return load(model_path)


def predict_price(feature_dict: Dict[str, float]) -> float:
    model = load_model_or_train()
    row = [[feature_dict[name] for name in FEATURE_NAMES]]
    pred = model.predict(row)[0]
    return float(pred)

