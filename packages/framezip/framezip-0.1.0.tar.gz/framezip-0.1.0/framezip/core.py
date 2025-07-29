import pandas as pd
from typing import Sequence, Union


IndexLike = Union[int, str]
IndexLikeSeq = Union[IndexLike, Sequence[IndexLike]]


def ensure_sequence(val: IndexLikeSeq) -> Sequence[IndexLike]:
    """
    Ensures the input is returned as a sequence (list), even if a single item.

    Parameters
    ----------
    val : int, str, or Sequence[int | str]
        A single column index/name or a sequence of column indices/names.

    Returns
    -------
    Sequence[int | str]
        A list-like sequence containing the input value(s).
        If a single value is passed, it is wrapped in a list.
    """
    if isinstance(val, (str, int)):
        return [val]
    return val


def pack(
    df: pd.DataFrame, key_cols: IndexLikeSeq, col_to_pack: IndexLikeSeq
) -> pd.DataFrame:
    """
    Groups a DataFrame by one or more key columns and packs other columns into lists.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame to group.
    key_cols : int, str, or Sequence[int | str]
        Column name(s) or index(es) to group by.
    col_to_pack : int, str, or Sequence[int | str]
        Column name(s) or index(es) whose values should be aggregated into lists.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with one row per unique key combination, and each packed column
        containing lists of aggregated values.
    """
    key_cols = ensure_sequence(key_cols)
    col_to_pack = ensure_sequence(col_to_pack)

    keys = [df.columns[i] if isinstance(i, int) else i for i in key_cols]
    packed_cols = [df.columns[i] if isinstance(i, int) else i for i in col_to_pack]

    packed_dict = {col: list for col in packed_cols}
    packed = df.groupby(keys).agg(packed_dict).reset_index()

    return packed


def unpack(df: pd.DataFrame, key_cols: IndexLikeSeq) -> pd.DataFrame:
    """
    Unpacks list-like columns in a DataFrame by exploding all non-key columns.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame in which some columns contain list-like values (typically created
        by the `pack()` function).
    key_cols : int, str, or Sequence[int | str]
        Column name(s) or index(es) used as grouping keys in the packed DataFrame.
        These columns will be preserved and not exploded.

    Returns
    -------
    pd.DataFrame
        A DataFrame where all non-key columns containing lists are exploded into
        multiple rows, one for each list element.
    """
    key_cols = ensure_sequence(key_cols)
    keys = [df.columns[i] if isinstance(i, int) else i for i in key_cols]
    packed_cols = [col for col in df.columns if col not in keys]

    return df.explode(packed_cols)
