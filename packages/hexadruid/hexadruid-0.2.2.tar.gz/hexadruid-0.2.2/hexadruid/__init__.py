# hexadruid/__init__.py

"""
HexaDruid 🧠
============

Spark-native skew detection, schema inference, salting & key detection toolkit.

This package exposes both expert APIs and a set of beginner-friendly wrappers,
including an interactive optimizer that recommends columns and lets you
pick one on the fly.
"""

from .hexadruid import (
    HexaDruid,
    balance_skew,
    DRTree,
    QuantileSkewDetector,
    KeyFeatureDetector,
    AutoParameterAdvisor,
)

__all__ = [
    "HexaDruid",
    "balance_skew",
    "DRTree",
    "QuantileSkewDetector",
    "KeyFeatureDetector",
    "AutoParameterAdvisor",
    # simplified wrappers
    "simple_optimize",
    "infer_schema",
    "detect_skew",
    "detect_keys",
    "visualize_salting",
    # interactive wrapper
    "interactive_optimize",
]


def simple_optimize(
    df,
    skew_col: str,
    sample_frac: float = 0.01,
    salt_count: int = 10,
):
    """
    One-liner pipeline: infer schema, build DRTree, and rebalance skew on `skew_col`.
    Returns a salted & repartitioned DataFrame.
    """
    hd = HexaDruid(df)
    hd.schemaVisor(sample_frac=sample_frac)
    return hd.apply_smart_salting(skew_col, salt_count=salt_count)


def infer_schema(df, sample_frac: float = 0.01):
    """
    Infer safe schema and build a one-level DRTree.
    Returns: (typed_df, StructType, DRTree)
    """
    hd = HexaDruid(df)
    return hd.schemaVisor(sample_frac=sample_frac)


def detect_skew(df, threshold: float = 0.1, top_n: int = 3):
    """
    Detect the top-N skewed numeric columns in your DataFrame.
    Returns a list of column names.
    """
    hd = HexaDruid(df)
    return hd.detect_skew(threshold=threshold, top_n=top_n)


def detect_keys(df, threshold: float = 0.99, max_combo: int = 3):
    """
    Detect primary or composite key candidates.
    Returns a list of column(s) that can serve as a key.
    """
    hd = HexaDruid(df)
    return hd.detect_keys(threshold=threshold, max_combo=max_combo)


def visualize_salting(df, skew_col: str, salt_count: int = 10):
    """
    Quickly apply salting and display before/after counts.
    Returns the salted DataFrame.
    """
    hd = HexaDruid(df)

    # show original distribution
    print("\n🔍 Original distribution:")
    df.groupBy(skew_col).count().orderBy("count", ascending=False).show(10)

    # apply salting
    df_salted = hd.apply_smart_salting(skew_col, salt_count=salt_count)

    # show new salt distribution
    print("\n  After salting (by salt bucket):")
    df_salted.groupBy("salt").count().orderBy("salt").show()

    return df_salted


def interactive_optimize(
    df,
    sample_frac: float = 0.1,
    skew_top_n: int = 5,
    cat_top_n: int = 5,
):
    """
    Interactive optimization pipeline:

    1. Recommends:
       - Top skewed numeric columns
       - Top low-cardinality categorical columns
    2. Shows the metrics table.
    3. Prompts you to pick ANY of those columns.
    4. Applies heavy-hitter salting on your choice.

    Returns the salted & repartitioned DataFrame.
    """
    hd = HexaDruid(df)
    advisor = AutoParameterAdvisor(df, skew_top_n=skew_top_n, cat_top_n=cat_top_n)

    # 1) Get recommendations & show metrics
    skew_cands, cat_cands, metrics_df = advisor.recommend()
    print("\n🔍 Recommended columns & metrics:\n")
    metrics_df.show(truncate=False)

    # 2) Build full list of choices
    all_cands = skew_cands + cat_cands
    print(f"\nNumeric candidates: {skew_cands}")
    print(f"Categorical candidates: {cat_cands}")

    # 3) Prompt user choice from either list
    prompt = f"\nPick a column to rebalance from {all_cands}: "
    choice = input(prompt).strip()
    if choice not in all_cands:
        raise ValueError(f"Invalid selection '{choice}'. Choose from {all_cands}")

    # 4) Apply salting on the chosen column
    print(f"\n⚙️  Applying smart salting on '{choice}' …")
    df_salted = hd.apply_smart_salting(choice)

    return df_salted