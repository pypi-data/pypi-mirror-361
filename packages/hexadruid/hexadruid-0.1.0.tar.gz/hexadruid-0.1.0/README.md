# HexaDruid

HexaDruid is a blazing-fast optimization engine for PySpark that intelligently:
- Detects and rebalances skewed columns using dynamic value bucketing
- Automatically detects primary keys and composite key candidates
- Splits your data logically using DRTree sharding
- Optionally tunes shuffle partitions

## Installation

```bash
pip install .
