"""
imputing.py - imputation utilities for the neatprep library.

These functions provide basic imputation techniques and also visuals to imputation results.

"""

import pandas as pd
import numpy as np


def smart_imputer(df: pd.DataFrame, missing_threshold: float = 0.8, verbose: bool = True):
    """
    Intelligently imputes missing values based on column type and data distribution.

    Parameters:
        df (pd.DataFrame): Input DataFrame
        missing_threshold (float): Columns with missing % > threshold will be skipped/warned
        verbose (bool): Print summary report

    Returns:
        pd.DataFrame: Imputed DataFrame
        pd.DataFrame: Imputation report summary
    """
    df = df.copy()
    report = []

    for col in df.columns:
        missing_ratio = df[col].isnull().mean()
        dtype = df[col].dtype

        if missing_ratio == 0:
            report.append((col, dtype.name, 'none', 0.0))
            continue

        if missing_ratio > missing_threshold:
            report.append((col, dtype.name, 'too_missing', missing_ratio))
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            if abs(df[col].skew(skipna=True)) < 1:
                strategy = 'mean'
                value = df[col].mean()
            else:
                strategy = 'median'
                value = df[col].median()
            df[col] = df[col].fillna(value)

        elif pd.api.types.is_categorical_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
            strategy = 'mode'
            value = df[col].mode(dropna=True).iloc[0] if not df[col].mode(dropna=True).empty else 'missing'
            df[col] = df[col].fillna(value)

        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            strategy = 'median_date'
            value = df[col].median()
            df[col] = df[col].fillna(value)

        else:
            strategy = 'unknown'
            value = None

        report.append((col, dtype.name, strategy, missing_ratio))

    report_df = pd.DataFrame(report, columns=["column", "dtype", "strategy", "missing_ratio"])

    if verbose:
        print("🧠 Smart Imputation Report")
        print(report_df.to_string(index=False))

    return df, report_df


import pandas as pd
import numpy as np
import random

def impute_synthetic(df: pd.DataFrame, missing_threshold: float = 0.8, seed: int = 42, verbose: bool = True):
    """
    Imputes missing values by generating synthetic values that mimic the column's distribution.

    Parameters:
        df (pd.DataFrame): Input DataFrame
        missing_threshold (float): Columns with > this % missing are skipped
        seed (int): Random seed for reproducibility
        verbose (bool): Print imputation summary

    Returns:
        pd.DataFrame: DataFrame with synthetic imputation
        pd.DataFrame: Summary report
    """
    np.random.seed(seed)
    random.seed(seed)

    df = df.copy()
    report = []

    for col in df.columns:
        missing_ratio = df[col].isnull().mean()
        dtype = df[col].dtype

        if missing_ratio == 0:
            report.append((col, dtype.name, 'none', 0.0))
            continue

        if missing_ratio > missing_threshold:
            report.append((col, dtype.name, 'too_missing', missing_ratio))
            continue

        non_null = df[col].dropna()

        if pd.api.types.is_numeric_dtype(df[col]):
            strategy = 'random_sample'
            imputed_values = np.random.choice(non_null.values, size=df[col].isnull().sum())
            df.loc[df[col].isnull(), col] = imputed_values

        elif pd.api.types.is_categorical_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
            strategy = 'random_category'
            probs = non_null.value_counts(normalize=True)
            sampled = np.random.choice(probs.index, size=df[col].isnull().sum(), p=probs.values)
            df.loc[df[col].isnull(), col] = sampled

        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            strategy = 'random_date'
            sampled = np.random.choice(non_null.values, size=df[col].isnull().sum())
            df.loc[df[col].isnull(), col] = sampled

        else:
            strategy = 'unknown'

        report.append((col, dtype.name, strategy, missing_ratio))

    report_df = pd.DataFrame(report, columns=["column", "dtype", "strategy", "missing_ratio"])

    if verbose:
        print("🧪 Synthetic Imputation Report")
        print(report_df.to_string(index=False))

    return df, report_df


import pandas as pd
import numpy as np

def impute_whatif(df: pd.DataFrame, col: str, sample: bool = True, n: int = 5, seed: int = 42):
    """
    Apply multiple imputation strategies to a column and return the modified DataFrames for comparison.

    Parameters:
        df (pd.DataFrame): Input dataframe
        col (str): Column name to impute
        sample (bool): Whether to show sample values for each strategy
        n (int): Number of sample rows to display
        seed (int): Random seed for reproducibility

    Returns:
        dict: A dictionary of DataFrames, each with one strategy applied
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in dataframe.")

    if df[col].isnull().sum() == 0:
        print(f"Column '{col}' has no missing values.")
        return {}

    np.random.seed(seed)
    results = {}
    non_null = df[col].dropna()
    is_numeric = pd.api.types.is_numeric_dtype(df[col])
    is_categorical = pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == object

    # Base
    base = df.copy()
    base[col] = df[col]
    results["original"] = base

    # Mean
    if is_numeric:
        mean_val = non_null.mean()
        df_mean = df.copy()
        df_mean[col] = df[col].fillna(mean_val)
        results["mean"] = df_mean

    # Median
    if is_numeric or pd.api.types.is_datetime64_any_dtype(df[col]):
        median_val = non_null.median()
        df_median = df.copy()
        df_median[col] = df[col].fillna(median_val)
        results["median"] = df_median

    # Mode
    mode_val = non_null.mode().iloc[0] if not non_null.mode().empty else None
    if mode_val is not None:
        df_mode = df.copy()
        df_mode[col] = df[col].fillna(mode_val)
        results["mode"] = df_mode

    # Random
    sampled_vals = np.random.choice(non_null, size=df[col].isnull().sum())
    df_random = df.copy()
    df_random.loc[df[col].isnull(), col] = sampled_vals
    results["random"] = df_random

    # Print sample values
    if sample:
        print(f"\n🧪 Imputation strategies preview for column: '{col}'\n")
        for name, frame in results.items():
            print(f"🔹 Strategy: {name}")
            print(frame[[col]].head(n), "\n")

    return results
