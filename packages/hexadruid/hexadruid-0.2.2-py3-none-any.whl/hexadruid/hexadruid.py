# hexadruid.py
"""
HexaDruid 🧠⚡
-------------
Spark-native skew detection, schema inference, heavy-hitter salting &
key detection toolkit—automatically picks your skew column and
bucket count for maximum performance.

Core features:
• schemaVisor()         — infer safe schema + 1-level DRTree
• detect_skew()         — top-N skewed numeric columns
• apply_smart_salting() — auto-detect skew & salt into dynamic buckets
• detect_keys()         — primary/composite key detection
• AutoParameterAdvisor — recommends skew/categorical columns & metrics
"""

import logging
import os
import re
import json

from typing import List, Tuple, Dict, Any, Optional


from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, when, concat_ws, expr,
    approx_count_distinct, floor, rand, hash, pmod
)
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, DoubleType, BooleanType,
    TimestampType, StringType
)


# ──────────────────────────────────────────────────────────────────────────────
# LOGGER
# ──────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger("HexaDruid")
if not logger.hasHandlers():
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


# ──────────────────────────────────────────────────────────────────────────────
# DRTree NODE CLASSES
# ──────────────────────────────────────────────────────────────────────────────
class Branch:
    """Leaf name + SQL predicate."""
    def __init__(self, name: str, predicate: str):
        self.name = name
        self.predicate = predicate

    def to_dict(self) -> dict[str,str]:
        return {"name": self.name, "predicate": self.predicate}


class Root:
    """Top-level node grouping branches."""
    def __init__(self, name: str):
        self.name = name
        self.branches: List[Branch] = []

    def add_branch(self, b: Branch):
        self.branches.append(b)

    def to_dict(self) -> dict[str,Any]:
        return {"root": self.name,
                "branches":[br.to_dict() for br in self.branches]}


class DRTree:
    """Recursive decision-rule tree for logical sharding."""
    def __init__(self):
        self.roots: List[Root] = []

    def add_root(self, root: Root):
        self.roots.append(root)

    def to_dict(self, concise: bool = True) -> dict[str,Any]:
        tree = []
        for r in self.roots:
            branches = []
            for b in r.branches:
                p = b.predicate
                if concise and len(p) > 60:
                    p = p[:57] + "..."
                branches.append({"name":b.name,"predicate":p})
            tree.append({"root":r.name,"branches":branches})
        return {"dr_tree": tree}


# ──────────────────────────────────────────────────────────────────────────────
# SKEW DETECTION
# ──────────────────────────────────────────────────────────────────────────────
class QuantileSkewDetector:
    """IQR-based skew detector."""
    def __init__(self, threshold: float = 0.1, top_n: int = 3):
        self.threshold = threshold
        self.top_n = top_n

    def detect(self, df: DataFrame) -> List[str]:
        cols = [f.name for f in df.schema.fields
                if isinstance(f.dataType, (IntegerType, DoubleType))]
        scores = []
        for c in cols:
            q1, q2, q3 = df.stat.approxQuantile(c, [0.25,0.5,0.75],0.01)
            iqr = max(q3 - q1, 1e-9)
            skew = abs((q3 - q2)-(q2 - q1)) / iqr
            scores.append((c, skew))
        scores.sort(key=lambda x: -x[1])
        return [c for c,s in scores if s > self.threshold][:self.top_n]


# ──────────────────────────────────────────────────────────────────────────────
# KEY DETECTION
# ──────────────────────────────────────────────────────────────────────────────
class KeyFeatureDetector:
    """
    Detect primary/composite keys via distinct-to-null ratios.
    Always returns at least one “best” candidate.
    """
    def __init__(self, threshold: float = 0.99, max_combo: int = 3):
        self.threshold = threshold
        self.max_combo = max_combo

    def detect(self, df: DataFrame, dr_tree: Optional[DRTree] = None) -> List[str]:
        total = df.count()
        # 1) Compute distinct & null counts for every column in one pass
        distincts = df.agg(
            *[approx_count_distinct(c).alias(c) for c in df.columns]
        ).first().asDict()
        nulls = df.select(
            *[expr(f"sum(CASE WHEN {c} IS NULL THEN 1 ELSE 0 END) as {c}_nulls")
              for c in df.columns]
        ).first().asDict()

        # 2) Compute uniqueness ratios
        ratios = {
            c: (distincts[c] - nulls[f"{c}_nulls"]) / max(total, 1)
            for c in df.columns
        }

        # 3) Check single columns meeting threshold
        singles = [c for c, r in ratios.items() if r >= self.threshold]
        if singles:
            return singles

        # 4) Otherwise, find the highest‐ratio single
        best_single = max(ratios.items(), key=lambda x: x[1])[0]

        # 5) (Optional) attempt composites only if best_single is still too low
        best_ratio = ratios[best_single]
        if best_ratio < self.threshold and self.max_combo >= 2:
            # Test combos of size 2…max_combo:
            cand = sorted(df.columns, key=lambda x: -ratios[x])[:10]
            for size in range(2, min(self.max_combo, len(cand)) + 1):
                from itertools import combinations
                for combo in combinations(cand, size):
                    expr_combo = concat_ws(
                        "||", *[col(c).cast("string") for c in combo]
                    ).alias("combo_key")
                    uniq = df.select(expr_combo) \
                            .agg(approx_count_distinct("combo_key")) \
                            .first()[0]
                    ratio = uniq / max(total, 1)
                    if ratio >= self.threshold:
                        return list(combo)

        # 6) Fallback to best single
        return [best_single]



# ──────────────────────────────────────────────────────────────────────────────
# AUTO PARAMETER ADVISOR
# ──────────────────────────────────────────────────────────────────────────────
# In hexadruid.py, replace your AutoParameterAdvisor with this:

class AutoParameterAdvisor:
    """
    Very fast recommendations by sampling up to `max_sample` rows.
    Recommends:
      - skewed numeric columns (IQR-based)
      - low-cardinality string columns
      - metrics DataFrame with skew, distinct, nulls
    """
    def __init__(
        self,
        df: DataFrame,
        skew_top_n: int = 3,
        cat_top_n: int = 3,
        sample_frac: float = 0.01,
        max_sample: int = 1000,
        seed: int = 42
    ):
        self.df = df
        self.skew_top_n = skew_top_n
        self.cat_top_n = cat_top_n
        self.sample_frac = sample_frac
        self.max_sample = max_sample
        self.seed = seed
        self.spark = SparkSession.builder.getOrCreate()

    def recommend(self) -> Tuple[List[str], List[str], DataFrame]:
        # 1) SAMPLE a small driver-friendly slice
        sample = (
            self.df
            .sample(False, self.sample_frac, self.seed)
            .limit(self.max_sample)
            .cache()
        )
        n = sample.count()

        # 2) Identify candidate columns
        num_cols = [
            f.name for f in sample.schema.fields
            if isinstance(f.dataType, (IntegerType, DoubleType))
        ]
        str_cols = [
            f.name for f in sample.schema.fields
            if isinstance(f.dataType, StringType)
        ]

        # 3) COLLECT bulk metrics in one agg:
        from pyspark.sql.functions import sum as _sum, when
        agg_exprs = []
        for c in num_cols + str_cols:
            agg_exprs.append(approx_count_distinct(c).alias(f"{c}_distinct"))
            agg_exprs.append(
                _sum(when(col(c).isNull(), 1).otherwise(0)).alias(f"{c}_nulls")
            )
        row = sample.agg(*agg_exprs).first().asDict()

        # 4) Compute ratios and pick top categorical
        cat_metrics = []
        for c in str_cols:
            distinct = row[f"{c}_distinct"]
            nulls = row[f"{c}_nulls"]
            ratio = (distinct - nulls) / max(n,1)
            cat_metrics.append((c, distinct, nulls, ratio))
        cat_metrics.sort(key=lambda x: -x[3])
        cat_cands = [c for c,_,_,_ in cat_metrics][: self.cat_top_n]

        # 5) Detect skewed numeric via IQR on the same sample
        skew_scores = []
        for c in num_cols:
            q1,q2,q3 = sample.stat.approxQuantile(c, [0.25,0.5,0.75], 0.01)
            iqr = max(q3 - q1, 1e-9)
            skew = abs((q3 - q2)-(q2 - q1)) / iqr
            skew_scores.append((c, skew))
        skew_scores.sort(key=lambda x: -x[1])
        skew_cands = [c for c,s in skew_scores][: self.skew_top_n]

        # 6) Build a small metrics DataFrame
        records = []
        for c, s in skew_scores[: self.skew_top_n]:
            records.append({
                "column": c,
                "type": "numeric",
                "skew": float(s),
                "distinct": int(row[f"{c}_distinct"]),
                "nulls": int(row[f"{c}_nulls"]),
            })
        for c, distinct, nulls, ratio in cat_metrics[: self.cat_top_n]:
            records.append({
                "column": c,
                "type": "categorical",
                "skew": None,
                "distinct": int(distinct),
                "nulls": int(nulls),
            })

        metrics_df = self.spark.createDataFrame(records)
        return skew_cands, cat_cands, metrics_df

# ──────────────────────────────────────────────────────────────────────────────
# MAIN API
# ──────────────────────────────────────────────────────────────────────────────
class HexaDruid:
    """
    Main interface:
     • schemaVisor()
     • detect_skew()
     • apply_smart_salting()
     • detect_keys()
    """
    def __init__(self, df: DataFrame, output_dir: str="hexa_druid_outputs"):
        self.df = df.cache()
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        logger.info(f"Initialized HexaDruid (out={output_dir})")

    def schemaVisor(
        self,
        sample_frac: float = 0.01,  # unused now, kept for signature compatibility
        max_sample: int = 1000
    ) -> tuple[DataFrame, StructType, DRTree]:
        """
        Fast schema inference + 1-level DRTree:
        1) Collect only max_sample rows in one go
        2) Infer types via regex/JSON on that small list
        3) (Optionally) build a trivial DRTree with a single 'all' branch
        """
        # 1) One Spark job to grab up to max_sample rows
        sample_rows = self.df.limit(max_sample).collect()

        # 2) Driver-side per-column type sniffing
        fields = []
        for c in self.df.columns:
            vals = [str(getattr(r, c)) for r in sample_rows if getattr(r, c) is not None]
            dtype = StringType()
            if vals and all(re.fullmatch(r"^-?\d+$", v) for v in vals):
                dtype = IntegerType()
            elif vals and all(re.fullmatch(r"^-?\d+\.\d+$", v) for v in vals):
                dtype = DoubleType()
            elif vals and all(v.lower() in ("true","false","0","1") for v in vals):
                dtype = BooleanType()
            elif vals and all(re.fullmatch(
                    r"\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(.\d+)?)?", v
                ) for v in vals):
                dtype = TimestampType()
            else:
                # JSON sniff
                def is_json(s: str) -> bool:
                    try: json.loads(s); return True
                    except: return False
                if vals and all(is_json(v) for v in vals):
                    dtype = StringType()
            fields.append(StructField(c, dtype, True))

        # 3) Build StructType and cast DataFrame
        schema = StructType(fields)
        typed = self.df
        for f in fields:
            tname = f.dataType.simpleString()
            typed = typed.withColumn(f.name, expr(f"try_cast({f.name} as {tname})"))

        # 4) Build a trivial DRTree (no expensive quantiles)
        dr = DRTree()
        root = Root("all")
        root.add_branch(Branch("all", "true"))
        dr.add_root(root)

        return typed.cache(), schema, dr

    def detect_skew(self, threshold: float=0.1, top_n: int=3) -> List[str]:
        """IQR-skew detection."""
        return QuantileSkewDetector(threshold, top_n).detect(self.df)

    def apply_smart_salting(
        self,
        col_name: Optional[str]=None,
        salt_count: Optional[int]=None
    ) -> DataFrame:
        """
        Dynamically detect skew column & bucket count, then salt:

        1) If col_name=None, auto-detect top-1 skewed column.
        2) If salt_count=None, use defaultParallelism or 10.
        3) Identify heavy hitters > total/salt_count.
        4) Assign salt:
           • heavy hitters → random bucket
           • others → pmod(hash(key), salt_count)
        5) Repartition on salted_key & cache.
        """
        # 1) detect column
        if col_name is None:
            cols = self.detect_skew(top_n=1)
            col_name = cols[0] if cols else self.df.columns[0]
            logger.info(f"Auto-detected skew column: {col_name}")

        # 2) choose salt_count
        sc = SparkSession.builder.getOrCreate().sparkContext
        default = sc.defaultParallelism or 10
        salt_count = salt_count or default
        logger.info(f"Using salt_count={salt_count}")

        # 3) heavy-hitter detection
        total = self.df.count()
        threshold = total / salt_count
        heavy = [
            r[col_name] for r in
            self.df.groupBy(col_name).count()
                   .filter(col("count") > threshold)
                   .select(col_name).collect()
        ]
        logger.info(f"Found heavy hitters: {heavy}")

        # 4) build salt expr
        salt_expr = when(
            col(col_name).isin(heavy),
            floor(rand(seed=42) * salt_count)
        ).otherwise(
            pmod(hash(col(col_name)), salt_count)
        )

        # 5) apply & repartition
        df2 = (
            self.df
            .withColumn("salt", salt_expr.cast("int"))
            .withColumn("salted_key", concat_ws("_", col(col_name), col("salt")))
            .repartition(salt_count, "salted_key")
            .cache()
        )
        return df2

    def detect_keys(self, threshold: float=0.99, max_combo: int=3) -> List[str]:
        """Primary/composite key detection."""
        return KeyFeatureDetector(threshold, max_combo).detect(self.df)


# backward alias
balance_skew = HexaDruid.apply_smart_salting
