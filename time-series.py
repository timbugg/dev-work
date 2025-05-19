import pandas as pd

def time_series_active_counts_distinct(df, start_col, end_col, time_freq='MS', start_date=None, end_date=None,
                                       group_cols=None, distinct_col=None):
    """
    Count distinct entities (e.g., AccountID, CustomerID) active over time, with optional grouping.

    Parameters:
    - df: pandas DataFrame with time-based activity (must include start/end and group columns).
    - start_col: name of the start date column.
    - end_col: name of the end date column (can be NaT).
    - time_freq: time grid frequency, e.g., 'MS' for monthly.
    - start_date: optional override for start of time grid.
    - end_date: optional override for end of time grid.
    - group_cols: list of column names to group by (e.g., ['ProductType', 'Region']).
    - distinct_col: name of column to count uniquely (e.g., 'CustomerID' or 'AccountID').

    Returns:
    - DataFrame with 'Period', group_cols..., and 'ActiveCount'
    """

    # Ensure datetime format
    df[start_col] = pd.to_datetime(df[start_col])
    df[end_col] = pd.to_datetime(df[end_col])

    # Determine time window
    if start_date is None:
        start_date = df[start_col].min()
    if end_date is None:
        end_date = df[end_col].max()

    # Create time periods
    time_index = pd.date_range(start=start_date, end=end_date, freq=time_freq)
    group_cols = group_cols or []

    results = []

    for period in time_index:
        # Select active rows for this period
        active = df[(df[start_col] <= period) & ((df[end_col].isna()) | (df[end_col] > period))]

        # Drop duplicates to ensure distinct entity counts
        if distinct_col:
            dedup_cols = [distinct_col] + group_cols
            active = active.drop_duplicates(subset=dedup_cols)

        # Count entities grouped by specified columns
        group = active.groupby(group_cols)[distinct_col if distinct_col else start_col].nunique().reset_index()
        group['Period'] = period
        group.rename(columns={distinct_col if distinct_col else start_col: 'ActiveCount'}, inplace=True)

        results.append(group)

    final_df = pd.concat(results, ignore_index=True)

    return final_df
