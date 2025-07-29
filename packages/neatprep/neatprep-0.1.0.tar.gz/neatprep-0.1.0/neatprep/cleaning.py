"""
cleaning.py - Core preprocessing utilities for the neatprep library.

These functions provide basic exploratory data inspection,
summary statistics, and generic cleaning tools.
"""

import numpy as np
import pandas as pd
import re

DEFAULT_NULL_THRESHOLD = 0.5
Z_THRESHOLD_DEFAULT = 3


def summarize(df : pd.DataFrame) -> pd.DataFrame :

  summary = pd.DataFrame(index=df.columns)
  summary["dtype"] = df.dtypes.astype(str)
  summary["missing"] = df.isnull.sum.astype(int)
  summary["% missing"] = (df.isnull().mean() * 100).round(2)
  summary["unique"] = df.nunique().astype(int)
  summary["sample"] = df.apply(lambda x : x.dropna().iloc[0] if x.dropna().shape[0]> 0 else np.nan)
  summary["dtype"] = df.dtypes.astype(str)

  return  summary



def clean_text_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z\s]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
    )
    return df

def smart_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform smart and automatic data cleaning on a DataFrame.

    Steps performed:
    - Clean column names (snake_case, remove special chars)
    - Replace dirty nulls like "N/A", "?", "--" with np.nan
    - Strip leading/trailing whitespace in string columns
    - Automatically fix datatypes (numeric, datetime, category)
    - Convert yes/no, true/false, 1/0 to proper boolean dtype
    - Remove constant (single-value) columns
    - Remove empty (all null) columns

    Parameters:
        df (pd.DataFrame): Input dataframe to clean

    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    df = df.copy()


    def clean_column_name(name):
        name = name.strip()
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", "_", name)
        return name.lower()

    df.columns = [clean_column_name(col) for col in df.columns]


    null_values = ["?", "n/a", "na", "--", "none", "", "null"]
    df.replace(to_replace=null_values, value=np.nan, inplace=True)


    for col in df.select_dtypes(include="object"):
        df[col] = df[col].astype(str).str.strip()


    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='ignore')
        except:
            pass

        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass

        if df[col].dtype == object and df[col].nunique() < df.shape[0] * 0.1:
            df[col] = df[col].astype('category')


    boolean_map = {
        "yes": True, "no": False,
        "true": True, "false": False,
        "1": True, "0": False
    }
    for col in df.select_dtypes(include="object"):
        lowered = df[col].astype(str).str.lower().map(boolean_map)
        if lowered.isin([True, False]).all():
            df[col] = lowered.astype(bool)


    constant_cols = [col for col in df.columns if df[col].nunique(dropna=False) <= 1]
    df.drop(columns=constant_cols, inplace=True)


    empty_cols = [col for col in df.columns if df[col].isnull().all()]
    df.drop(columns=empty_cols, inplace=True)

    return df

def remove_outliers(df: pd.DataFrame, method: str = 'zscore', threshold: float = 3.0) -> pd.DataFrame:
    """
    Remove rows that are outliers based on numeric features.

    Parameters:
        df (pd.DataFrame): The input dataframe.
        method (str): 'zscore' or 'iqr'
        threshold (float): Threshold for Z or IQR (3.0 or 1.5)

    Returns:
        pd.DataFrame: Dataframe with outliers removed.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include='number').columns

    if method == 'zscore':
        from scipy.stats import zscore
        z_scores = df[numeric_cols].apply(zscore)
        mask = (z_scores.abs() < threshold).all(axis=1)
        return df[mask]

    elif method == 'iqr':
        mask = pd.Series(True, index=df.index)
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            col_mask = (df[col] >= (Q1 - threshold * IQR)) & (df[col] <= (Q3 + threshold * IQR))
            mask &= col_mask
        return df[mask]

    else:
        raise ValueError("Method must be either 'zscore' or 'iqr'")


def report_cleaning(df_before: pd.DataFrame, df_after: pd.DataFrame) -> None:
    """
    Print a summary of changes made to the DataFrame after cleaning.
    Includes dropped/added columns, row/column count changes, and type changes.
    """
    print("🧼 Cleaning Summary Report")
    print("=" * 40)


    print(f"Rows:    {df_before.shape[0]} → {df_after.shape[0]}")
    print(f"Columns: {df_before.shape[1]} → {df_after.shape[1]}")
    print()


    dropped_cols = set(df_before.columns) - set(df_after.columns)
    if dropped_cols:
        print("🗑️ Dropped Columns:")
        for col in sorted(dropped_cols):
            print(f" - {col}")
        print()


    added_cols = set(df_after.columns) - set(df_before.columns)
    if added_cols:
        print("➕ New Columns:")
        for col in sorted(added_cols):
            print(f" + {col}")
        print()

    # Changed dtypes
    changed_dtypes = []
    for col in df_before.columns:
        if col in df_after.columns:
            before_type = df_before[col].dtype
            after_type = df_after[col].dtype
            if before_type != after_type:
                changed_dtypes.append((col, before_type, after_type))

    if changed_dtypes:
        print("🔁 Changed Data Types:")
        for col, before, after in changed_dtypes:
            print(f" - {col}: {before} → {after}")
        print()

    if not dropped_cols and not added_cols and not changed_dtypes:
        print("✅ No structural changes detected.")
