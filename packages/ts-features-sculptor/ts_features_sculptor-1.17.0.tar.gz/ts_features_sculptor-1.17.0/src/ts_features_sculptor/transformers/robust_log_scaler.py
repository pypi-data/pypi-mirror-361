from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


def _log1p_safe(s: pd.Series) -> pd.Series:
    return np.log1p(s.astype(float))


@dataclass
class RobustLogScaler(BaseEstimator, TransformerMixin):
    """
    Робастная медианная стандартизация:

        z = 0.6745 · (log1p(x) − med) / MAD

    Parameters
    ----------
    feature_col: str, default="tte"
        Имя столбца для нормализации.
    out_col: str | None, default = None
        Имя столбца для сохранения результата.
    transform_func: Callable[[pd.Series], pd.Series],
                    default = _log1p_safe
        Функция
    keep_params: bool = True
        Флаг сохранения значений `med` и `MAD`.

    Notes
    -----
    Обратное преобразование реализовано только для log1p.

    Examples
    --------
    >>> df = pd.DataFrame({"tte": [1, 2, 4]})
    >>> scaler = RobustLogScaler(
    ...    feature_col="tte", out_col="tte_z", keep_params=False)
    >>> df_z = scaler.fit_transform(df)
    >>> print(df_z.to_string(index=False))
     tte    tte_z
       1 -0.67450
       2  0.00000
       4  0.84977
    >>> scaler.inverse_transform(df_z["tte_z"])
    array([1., 2., 4.])
    """

    feature_col: str = "target"
    out_col: str | None = None
    transform_func: Callable[[pd.Series], pd.Series] = _log1p_safe
    keep_params: bool = True

    med_: float = field(init=False, default=np.nan, repr=False)
    mad_: float = field(init=False, default=np.nan, repr=False)

    def fit(self, X: pd.DataFrame, y=None):
        if self.feature_col not in X.columns:
            raise ValueError(
                f"RobustLogScaler: колонка '{self.feature_col}' "
                f"не найдена")

        tr = self.transform_func(X[self.feature_col])
        self.med_ = float(np.nanmedian(tr))
        self.mad_ = float(np.nanmedian(np.abs(tr - self.med_)))
        return self

    def transform(self, X: pd.DataFrame):
        if np.isnan(self.mad_):
            raise RuntimeError(
                "RobustLogScaler: необходимо вызвать fit()"
            )

        df = X.copy()
        tr = self.transform_func(df[self.feature_col])
        with np.errstate(divide="ignore", invalid="ignore"):
            z = 0.6745 * (tr - self.med_) / self.mad_

        dst_col = self.out_col or self.feature_col
        df[dst_col] = z

        if self.keep_params:
            df[f"{dst_col}_med"] = self.med_
            df[f"{dst_col}_mad"] = self.mad_

        return df

    def inverse_transform(self, z: np.ndarray | pd.Series) -> np.ndarray:
        """
        Восстанавливает значения из z-оценок для случая
        transform_func == log1p.
        """
        if np.isnan(self.mad_) or np.isnan(self.med_):
            raise RuntimeError(
                f"RobustLogScaler: {self.mad_=}, {self.med_}")

        z = np.asarray(z, dtype=float)
        if self.mad_ == 0:
            return np.full_like(z, np.nan)

        raw = z * self.mad_ / 0.6745 + self.med_

        if self.transform_func is _log1p_safe:
            return np.expm1(raw)

        raise NotImplementedError(
            "inverse_transform только для log1p"
        )
