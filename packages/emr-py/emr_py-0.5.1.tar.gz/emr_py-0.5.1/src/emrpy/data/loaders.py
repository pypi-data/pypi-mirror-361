"""
Data Loading Utilities

Functions for loading CSV and Parquet files with support for both pandas and polars,
lazy loading, and sampling options.
"""

import pandas as pd
from typing import Union, Optional
from pathlib import Path

# Optional polars import
try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


def load_csv(
    file_path: Union[str, Path],
    engine: str = "pandas",
    lazy: bool = False,
    sample_frac: Optional[float] = None,
    sample_n: Optional[int] = None,
    **kwargs,
) -> Union[pd.DataFrame, "pl.DataFrame", "pl.LazyFrame"]:
    """
    Load CSV files with pandas or polars backend.

    Parameters:
    -----------
    file_path : str or Path
        Path to the CSV file
    engine : str, default "pandas"
        Backend to use: "pandas" or "polars"
    lazy : bool, default False
        Whether to use lazy loading (polars only, ignored for pandas)
    sample_frac : float, optional
        Fraction of data to sample (0.0 to 1.0)
    sample_n : int, optional
        Number of rows to sample (takes precedence over sample_frac)
    **kwargs
        Additional arguments passed to pandas.read_csv() or polars.read_csv()

    Returns:
    --------
    DataFrame or LazyFrame depending on engine and lazy parameter

    Examples:
    ---------
    >>> # Load with pandas
    >>> df = load_csv("data.csv")

    >>> # Load with polars (lazy)
    >>> df = load_csv("data.csv", engine="polars", lazy=True)

    >>> # Sample 10% of data
    >>> df = load_csv("data.csv", sample_frac=0.1)

    >>> # Sample 1000 rows
    >>> df = load_csv("data.csv", sample_n=1000)
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if engine == "pandas":
        return _load_csv_pandas(file_path, sample_frac, sample_n, **kwargs)
    elif engine == "polars":
        return _load_csv_polars(file_path, lazy, sample_frac, sample_n, **kwargs)
    else:
        raise ValueError(f"Unsupported engine: {engine}. Use 'pandas' or 'polars'")


def load_parquet(
    file_path: Union[str, Path],
    engine: str = "pandas",
    lazy: bool = False,
    sample_frac: Optional[float] = None,
    sample_n: Optional[int] = None,
    **kwargs,
) -> Union[pd.DataFrame, "pl.DataFrame", "pl.LazyFrame"]:
    """
    Load Parquet files with pandas or polars backend.

    Parameters:
    -----------
    file_path : str or Path
        Path to the Parquet file
    engine : str, default "pandas"
        Backend to use: "pandas" or "polars"
    lazy : bool, default False
        Whether to use lazy loading (polars only, ignored for pandas)
    sample_frac : float, optional
        Fraction of data to sample (0.0 to 1.0)
    sample_n : int, optional
        Number of rows to sample (takes precedence over sample_frac)
    **kwargs
        Additional arguments passed to pandas.read_parquet() or polars.read_parquet()

    Returns:
    --------
    DataFrame or LazyFrame depending on engine and lazy parameter

    Examples:
    ---------
    >>> # Load with pandas
    >>> df = load_parquet("data.parquet")

    >>> # Load with polars (lazy)
    >>> df = load_parquet("data.parquet", engine="polars", lazy=True)

    >>> # Sample 5% of data
    >>> df = load_parquet("data.parquet", sample_frac=0.05)
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if engine == "pandas":
        return _load_parquet_pandas(file_path, sample_frac, sample_n, **kwargs)
    elif engine == "polars":
        return _load_parquet_polars(file_path, lazy, sample_frac, sample_n, **kwargs)
    else:
        raise ValueError(f"Unsupported engine: {engine}. Use 'pandas' or 'polars'")


def _load_csv_pandas(
    file_path: Path, sample_frac: Optional[float], sample_n: Optional[int], **kwargs
) -> pd.DataFrame:
    """Load CSV with pandas backend."""
    # Load the data
    df = pd.read_csv(file_path, **kwargs)

    # Apply sampling if requested
    if sample_n is not None:
        df = df.sample(n=min(sample_n, len(df)), random_state=42)
    elif sample_frac is not None:
        df = df.sample(frac=sample_frac, random_state=42)

    return df


def _load_parquet_pandas(
    file_path: Path, sample_frac: Optional[float], sample_n: Optional[int], **kwargs
) -> pd.DataFrame:
    """Load Parquet with pandas backend."""
    # Load the data
    df = pd.read_parquet(file_path, **kwargs)

    # Apply sampling if requested
    if sample_n is not None:
        df = df.sample(n=min(sample_n, len(df)), random_state=42)
    elif sample_frac is not None:
        df = df.sample(frac=sample_frac, random_state=42)

    return df


def _load_csv_polars(
    file_path: Path, lazy: bool, sample_frac: Optional[float], sample_n: Optional[int], **kwargs
) -> Union["pl.DataFrame", "pl.LazyFrame"]:
    """Load CSV with polars backend."""
    if not POLARS_AVAILABLE:
        raise ImportError("Polars is not installed. Install with: pip install polars")

    if lazy:
        # Use lazy loading
        # Apply sampling if requested
        if sample_n is not None:
            print(f"Loading first {sample_n} rows lazily from {file_path}")
            df = pl.scan_csv(file_path, n_rows=sample_n, **kwargs)
        else:
            df = pl.scan_csv(file_path, **kwargs)

        return df
    else:
        # Eager loading
        df = pl.read_csv(file_path, **kwargs)

        # Apply sampling if requested
        if sample_n is not None:
            df = df.sample(n=min(sample_n, len(df)), seed=42)
        elif sample_frac is not None:
            df = df.sample(fraction=sample_frac, seed=42)

        return df


def _load_parquet_polars(
    file_path: Path, lazy: bool, sample_frac: Optional[float], sample_n: Optional[int], **kwargs
) -> Union["pl.DataFrame", "pl.LazyFrame"]:
    """Load Parquet with polars backend."""
    if not POLARS_AVAILABLE:
        raise ImportError("Polars is not installed. Install with: pip install polars")

    if lazy:
        # Use lazy loading
        # Apply sampling if requested
        if sample_n is not None:
            print(f"Loading first {sample_n} rows lazily from {file_path}")
            df = pl.scan_parquet(file_path, n_rows=sample_n, **kwargs)
        else:
            df = pl.scan_parquet(file_path, **kwargs)

        return df
    else:
        # Eager loading
        df = pl.read_parquet(file_path, **kwargs)

        # Apply sampling if requested
        if sample_n is not None:
            df = df.sample(n=min(sample_n, len(df)), seed=42)
        elif sample_frac is not None:
            df = df.sample(fraction=sample_frac, seed=42)

        return df
