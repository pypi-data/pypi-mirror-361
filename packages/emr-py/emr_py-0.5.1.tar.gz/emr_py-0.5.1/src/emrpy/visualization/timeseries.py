"""
Time Series Visualization Utilities

Functions for plotting financial and time series data with proper handling
of trading gaps and discontinuous timestamps.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple


def plot_timeseries(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    value_col: str = "close",
    segment_col: Optional[str] = None,
    segment_value: Optional[str] = None,
    tick_every: int = 100,
    figsize: Tuple[int, int] = (12, 6),
) -> None:
    """
    Plot time series data with continuous bar numbering to avoid trading gaps.

    This function creates a continuous plot by using bar numbers instead of timestamps,
    which eliminates gaps from weekends and holidays in financial data.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the time series data
    timestamp_col : str, default 'timestamp'
        Name of the timestamp column
    value_col : str, default 'close'
        Name of the column containing values to plot
    segment_col : str, optional
        Column name to filter by (e.g., 'Symbol' for stock tickers)
    segment_value : str, optional
        Value to filter on in segment_col (e.g., 'AAPL')
    tick_every : int, default 100
        Show timestamp labels every N bars
    figsize : tuple, default (12, 6)
        Figure size as (width, height)

    Examples:
    ---------
    >>> # Plot AAPL data
    >>> plot_timeseries(
    ...     df=stock_data,
    ...     segment_col='Symbol',
    ...     segment_value='AAPL'
    ... )

    >>> # Plot all data without filtering
    >>> plot_timeseries(df=price_data)
    """
    # Filter and sort
    data = df.copy()
    if segment_col and segment_value:
        data = data[data[segment_col] == segment_value].copy()

    data[timestamp_col] = pd.to_datetime(data[timestamp_col])
    data = data.sort_values(timestamp_col).reset_index(drop=True)

    # Create continuous bar numbering
    data["bar_number"] = range(len(data))

    # Create plot
    plt.figure(figsize=figsize)
    plt.plot(data["bar_number"], data[value_col], lw=1)

    # Set title and labels
    title = f"{segment_value} {value_col.title()}" if segment_value else f"{value_col.title()}"
    plt.title(f"{title} (Trading Bars Only)")
    plt.xlabel("Bar Number (continuous through trading sessions)")
    plt.ylabel(f"{value_col.title()}")

    # Add timestamp ticks
    if len(data) > tick_every:
        tick_positions = data["bar_number"][::tick_every]
        tick_labels = data[timestamp_col].dt.strftime("%Y-%m-%d %H:%M")[::tick_every]
        plt.xticks(tick_positions, tick_labels, rotation=45)

    plt.tight_layout()
    plt.show()


def plot_multiple_log_returns(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    price_col: str = "close",
    segment_col: str = "Symbol",
    segment_values: Optional[list] = None,
    figsize: Tuple[int, int] = (12, 8),
) -> None:
    """
    Plot multiple time series as cumulative log returns for comparison.

    Converts price data to log returns and plots them on the same graph,
    making it easy to compare performance across different assets.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the time series data
    timestamp_col : str, default 'timestamp'
        Name of the timestamp column
    price_col : str, default 'close'
        Name of the price column
    segment_col : str, default 'Symbol'
        Column name that identifies different assets
    segment_values : list, optional
        List of assets to plot. If None, plots all unique values
    figsize : tuple, default (12, 8)
        Figure size as (width, height)

    Examples:
    ---------
    >>> # Plot specific stocks
    >>> plot_multiple_log_returns(
    ...     df=stock_data,
    ...     segment_values=['AAPL', 'GOOGL', 'MSFT']
    ... )

    >>> # Plot all assets in the dataset
    >>> plot_multiple_log_returns(df=stock_data)
    """
    # Get list of assets to plot
    if segment_values is None:
        segment_values = df[segment_col].unique()

    plt.figure(figsize=figsize)

    # Plot each asset
    for asset in segment_values:
        # Filter data for this asset
        asset_data = df[df[segment_col] == asset].copy()

        if len(asset_data) < 2:  # Need at least 2 points for returns
            continue

        # Sort by timestamp
        asset_data[timestamp_col] = pd.to_datetime(asset_data[timestamp_col])
        asset_data = asset_data.sort_values(timestamp_col).reset_index(drop=True)

        # Calculate log returns and cumulative sum
        asset_data["log_returns"] = np.log(asset_data[price_col] / asset_data[price_col].shift(1))
        asset_data["cumulative_log_returns"] = asset_data["log_returns"].cumsum()

        # Create bar numbers for continuous plotting
        asset_data["bar_number"] = range(len(asset_data))

        # Plot (skip first row since it will be NaN)
        plt.plot(
            asset_data["bar_number"][1:],
            asset_data["cumulative_log_returns"][1:],
            label=asset,
            linewidth=1.5,
        )

    plt.title("Cumulative Log Returns Comparison")
    plt.xlabel("Bar Number (continuous through trading sessions)")
    plt.ylabel("Cumulative Log Returns")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
