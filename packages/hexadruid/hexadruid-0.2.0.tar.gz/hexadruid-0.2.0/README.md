# HexaDruid 🧠⚡

[![PyPI version](https://badge.fury.io/py/hexadruid.svg)](https://badge.fury.io/py/hexadruid)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**HexaDruid** is an intelligent Spark optimizer designed to tackle **data skew**, **ambiguous key detection**, and **schema bloat** using smart salting, recursive shard-aware rule trees, and adaptive tuning. It enables better parallelism, safer memory layout, and intelligent insight into skewed datasets using PySpark’s native DataFrame API.

---

## 🚀 Installation

```bash
pip install hexadruid
```
To upgrade to the latest version?

```bash
pip install --upgrade hexadruid
```
---

## 🔍 Features

- 📊 **Smart Salting** using Z-score or IQR skew analysis + percentile bucketing
- 🌲 **Recursive DRTree** for shard-based logical filtering with SQL predicates
- 🔑 **Primary & Composite Key Detection** (UUIDs, alphanumerics, hex — optional)
- 🧠 **Schema Inference** with safe type coercion, length introspection & metadata tags
- ⚙️ **Auto-Parameter Advisor** for optimal salt count and shuffle parallelism
- 📉 **Z-Score Plots** and **partition size diagnostics** for visibility
- ✅ Fully **PySpark-native** — No RDDs, no CLI dependencies, no black-box wrappers
- 🚨 **Robust headerless/corrupt file handling:** `schemaVisor()` now safely infers schema even for files without headers, random/duplicate columns, and all-null columns, automatically skipping or dropping problematic columns.
- 🛡️ **Automatic type correction:** String columns with mostly-numeric content are auto-cast to `IntegerType`/`DoubleType` with fallback and null-tolerant handling.
- 🏷️ **Column profile metadata:** All inferred columns include `cardinality`, `is_categorical`, `max_length`, and `avg_length` in metadata for downstream ML or analytics.
- 📉 **All-null column detection and drop:** Empty columns are automatically flagged and excluded from the inferred schema.
- 🪓 **Improved error handling:** No more crashes when loading malformed, sparse, or incomplete CSV/Parquet/JSON files.
- 🪄 **Safer fallbacks:** DRTree logic now always returns a safe fallback if no splits or predicates are found (avoids runtime errors).
- 📜 **Verbose logging for edge cases:** All non-critical issues (like fully-empty columns, unknown types) are now logged as warnings, not hard errors.
- 🦾 **Internal modularization:** Codebase refactored for maintainability and extensibility.
- 🧪 **Expanded test coverage:** Fuzzed and synthetic data edge cases now fully covered in tests.
---

## 🧠 Quickstart

```python
from hexadruid import HexaDruid

hd = HexaDruid(df)

# Step 1: Apply smart salting to balance skew
df_salted = hd.apply_smart_salting("sales_amount")

# Step 2 (Optional): Detect candidate primary or composite keys
key_info = hd.detect_keys()

# Step 3: Run schema optimizer + DRTree analyzer
typed_df, inferred_schema, dr_tree = HexaDruid.schemaVisor(df)
```

---

## 📚 What Does It Do?

Imagine a typical DataFrame:

| order_id (UUID) | amount  |
|-----------------|---------|
| a12e...         | 500.0   |
| b98c...         | 5000.0  |
| ...             | ...     |

You're doing:

```python
df.groupBy("amount").agg(...)
```

But **most rows have the same `amount`**, so Spark sends 99% of the work to 1 executor = skew 💥

---

## 🛠️ Main Classes & API Reference

Here are the key classes exposed by the HexaDruid package:

| Class                  | Description                                                                         |
|------------------------|-------------------------------------------------------------------------------------|
| `HexaDruid`            | Main entrypoint; handles smart salting, key detection, and schema optimization      |
| `SkewFeatureDetector`  | Detects skewed numeric columns for rebalancing                                      |
| `KeyFeatureDetector`   | Detects primary/composite keys (unique columns/combinations)                        |
| `DRTree`               | Decision Rule Tree for logical sharding                                             |
| `AutoParameterAdvisor` | Recommends optimal columns for skew balancing and groupBy                           |
| `AdaptiveShuffleTuner` | Tunes shuffle partition count dynamically                                           |
| `Branch`, `Root`       | (Advanced) Internal tree structure helpers                                          |

---

---

## 📑 API Reference

All core APIs are PySpark DataFrame-native. Below are the main classes and methods:

---

### `HexaDruid`

| Method                                                                          | Description                                                                                         |
|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `HexaDruid(df, salt_count=10, output_dir="hexa_druid_outputs")`                  | Initialize with a Spark DataFrame. Optional: set default salt bucket count and output directory.    |
| `apply_smart_salting(col_name, visualize=True, fine_tune=True, auto_tune=True, target_rows=1_000_000)` | Balance skew in `col_name` by bucketizing (salting), visualizing, tuning salt count, and auto-tuning partitions. Returns a salted DataFrame with new columns: `salt`, `salted_key`. |
| `detect_keys(dr_tree=None, composite_max_size=3, composite_threshold=0.99, verbose=True)` | Detects the best candidate for a **primary key** or a **composite key**. Uses shard-aware logic if a `dr_tree` is passed. Returns a dict: `{type, columns, confidence}` or None.     |
| `repartition_on_salt(num_partitions=10)`                                         | Repartitions the salted DataFrame evenly on the `salted_key` column. Returns a repartitioned DataFrame.                     |
| `show_partition_sizes(df, label="")`                                             | Prints the record count of each partition in the DataFrame, labeled for diagnostics.                                        |
| `build_shard_tree(detector, max_depth=3, min_samples=500)`                       | Recursively build a logical sharding tree (DRTree) by splitting on skewed columns. Detector must implement `.detect()`.    |
| `analyze_distribution(col_name)`                                                 | Returns distribution stats (`p95`, `p05`, `mean`, `std`) for a given column.                                              |
| `schemaVisor(df, sample_fraction=0.2, max_depth=3, min_samples=500, skew_thresh=0.1, skew_top_n=3)` *(static)* | Infers schema types, casts columns, and builds a DRTree for sharding. Returns a tuple: (`typed_df`, `StructType`, `DRTree`). |
| `infer_numeric_columns(df)` *(static)*                                           | Returns a list of numeric columns (int, float, double, long, bigint).                                                    |
| `detect_low_cardinality_categorical(df)` *(static)*                              | Finds the first string column with ≤20 unique values (good for groupBy). Raises ValueError if none found.                  |
| `timeit(func, label="")` *(static)*                                              | Times the execution of a function and logs the result.                                                                    |
| `_plot_comparison(col_name, df2)` *(private)*                                    | Generates and saves z-score barplots for original vs salted columns.                                                      |

---

### `SkewFeatureDetector`

| Method                                            | Description                                                              |
|---------------------------------------------------|--------------------------------------------------------------------------|
| `SkewFeatureDetector(threshold=0.1, top_n=3)`     | Initialize detector with skew threshold and number of columns to return. |
| `detect(df)`                                      | Returns the top-N most skewed numeric columns by quartile-based score.   |

---

### `KeyFeatureDetector`

| Method                                                                                                   | Description                                                        |
|----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| `KeyFeatureDetector(verbose=False)`                                                                      | Initialize detector for verbose logging.                           |
| `detect(df, dr_tree=None)`                                                                               | Returns best candidate key columns (single/composite), optionally shard-aware. List[str].        |
| `detectPrimaryKey(df, dr_tree=None, confidence_threshold=0.99, verbose=False)` *(static)*                | Detects primary key with confidence score. Returns dict or None.   |
| `detectCompositeKey(df, dr_tree=None, max_combination_size=3, confidence_threshold=0.99, verbose=False)` *(static)* | Detects composite keys by testing combinations of 2-3 columns. Returns dict or None.    |

---

### `AutoParameterAdvisor`

| Method                                                     | Description                                                           |
|------------------------------------------------------------|-----------------------------------------------------------------------|
| `AutoParameterAdvisor(df, skew_top_n=3, cat_top_n=3)`      | Initialize with DataFrame and how many top columns to suggest.        |
| `recommend()`                                              | Returns (skew candidates, groupBy candidates, metrics DataFrame).     |
| `advise()`                                                 | Interactive prompt: pick skew/groupBy columns (returns 2 strings).    |

---

### `DRTree`

| Method                       | Description                                               |
|------------------------------|-----------------------------------------------------------|
| `DRTree()`                   | Create a new, empty Decision Rule Tree.                   |
| `add_root(root)`             | Add a `Root` node to the DRTree.                          |
| `to_dict()`                  | Returns a JSON-serializable dictionary of the tree.       |

---

### `Branch`, `Root`, `DecisionNode`, `LeafNode`

- **Branch**: Simple data holder for a leaf/shard predicate and its name.
- **Root**: Logical tree root node; holds one or more branches.
- **DecisionNode**: Internal tree node representing a split on a numeric column.
- **LeafNode**: Terminal node; represents a filtered logical subset ("shard") of your data.

---

### `balance_skew`

| Function                                                   | Description                                                                                           |
|------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| `balance_skew(df, output_dir="hexa_druid_outputs", partitions=10, verbose=False)` | Runs full salting pipeline interactively: prompts for skew/groupBy columns, applies salting, shows before/after partition diagnostics. Returns a new DataFrame. |

---

### `AdaptiveShuffleTuner`

| Method                                     | Description                                                     |
|---------------------------------------------|-----------------------------------------------------------------|
| `tune(spark, df, target_rows=1_000_000)` *(static)* | Auto-tunes shuffle partitions based on target rows per partition. Returns repartitioned DataFrame. |

---

> **Tip:**  
> - See the `tests/` directory for working code samples and usage patterns.
> - All methods are intended for use with Spark DataFrames (PySpark >= 3.5.1).
> - Advanced users can directly use the `KeyFeatureDetector`, `SkewFeatureDetector`, and `AutoParameterAdvisor` in custom pipelines.

---

### ⚖️ Smart Salting to the Rescue

```python
df2 = hd.apply_smart_salting("amount")
```

What happens?

```
 Step 1: Analyze column distribution via IQR or Z-score
 Step 2: Generate N percentile buckets
 Step 3: Assign salt ID per row using bucket bounds
 Step 4: Create salted_key = amount_salt
 Step 5: Repartition on salted_key for parallelism
```

📈 This rebalances the shuffle phase for joins, groupBy, and aggregates.

---

### 🧠 DRTree Explained Visually

The DRTree is a **decision-rule tree**, not a classifier.

It recursively splits data into shards by applying SQL-style predicates. Each leaf is a filtered logical subset of the DataFrame.

```
                        [Root: sales_amount]
                                |
                   ┌───────────┴────────────┐
        [amount <= 500]             [amount > 500]
               |                           |
       ┌───────┴───────┐            ┌──────┴───────┐
 [amount <= 100] [>100, ≤500]   [>500, ≤1000]  [>1000]
       |         |                  |             |
   [Leaf A]   [Leaf B]          [Leaf C]       [Leaf D]
 (shard_1)   (shard_2)         (shard_3)      (shard_4)
```

Each **leaf** holds:
- Filtered subset of the DataFrame (as a Spark SQL query)
- Associated metadata like row count, min/max, schema drift
- Auto key detection can run **within** these shards

---

### 🔬 Leaf-Level Parallelization

DRTree enables **parallel insight**:

- Each leaf is **autonomous** (you can infer schema, key, and stats per leaf)
- Makes the system robust to changes over time (drift detection)
- Enables controlled analytics:
  
```
[DRTree Output]
Leaf A:
  - rows: 30K
  - key_confidence: 0.92
  - type: Float(5,2)

Leaf D:
  - rows: 300K (hotspot!)
  - key_confidence: 0.12
  - type: String(255)
```

---

## 🔑 Key Detection (Optional & Shard-Aware)

```python
key_info = hd.detect_keys()
```

You **don’t need to force primary keys**.

This is just **analysis** — it evaluates uniqueness confidence for each column (or combination of columns):

- **Primary Key:**

```python
score = (approx_count_distinct(col) / total_rows) - null_ratio
```

If `score ≥ 0.99`, it’s a good candidate.

- **Composite Key:**

```python
combo_key = concat_ws("_", col1, col2, ...)
score = approx_count_distinct(combo_key) / total_rows - null_ratio
```

DRTree passes its **shard filters** into `detect_keys()` to evaluate keys per **subgroup** — boosting accuracy.

---

## 🧠 Smart Salting Internals

### 🧪 Step-by-step:

1. **Detect Skew**  
   - If `z_score` range is too large or  
   - IQR shows asymmetry (Q3 - Q2 ≫ Q2 - Q1)

2. **Split by Percentiles**

```python
percentiles = percentile_approx("amount", [0.0, 0.1, ..., 1.0])
```

3. **Salt Bucketing Logic**

```python
salt = when(col >= p0 & col < p1, 0) \
     .when(col >= p1 & col < p2, 1) ...
```

4. **Create Salted Key**

```python
salted_key = concat_ws("_", col("amount"), col("salt"))
df = df.withColumn("salted_key", salted_key).repartition("salted_key")
```

5. **Auto-Tune Salt Count**

- If distribution is dense, fewer buckets suffice
- Otherwise, more salting is applied dynamically

---

## 📈 Visualization Example

Output from `schemaVisor()`:

```
Leaf Node A [shard_0]
- size: 102,391
- type: Float(8,2)
- confidence: 92%

Leaf Node B [shard_1]
- size: 489,128 (dense zone)
- skew detected!
- Recommended salt count: 10
```

You can visualize the Z-score distribution:

```
Before:
  [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■             ]

After:
  [■■■■■■■■■■■■■■■■■■■■■      ■■■■■■■■■■■■■■■■■■■■■■   ]
```

---

## 🧪 Testing

```bash
pytest tests/
```

Mocked `SparkSession` with synthetic data is used to ensure full coverage.

---

## 🧱 Suggested Project Structure

```
hexadruid/
├── __init__.py
├── core.py                # HexaDruid entry point
├── skew_balancer.py       # Smart salting logic
├── drtree.py              # DRTree shard splitting
├── key_detection.py       # Unique key checker
├── schema_optimizer.py    # Type inference
├── advisor.py             # Parameter tuning
├── utils.py               # Logging, plots, etc.
└── tests/                 # Test suite
```

---

## 🔧 Roadmap

- [ ] CLI interface  
- [ ] Delta Lake + Iceberg support  
- [ ] JupyterLab extension  
- [ ] DRTree JSON export for audits  
- [ ] Cost metrics estimation  
- [ ] Column statistics and visualization dashboard

---

## 📄 License

MIT License

---

## 🤝 Contributing

Pull requests, ideas, and contributions welcome!

We believe Spark shouldn’t be slow. Let’s make it smarter together.

---
