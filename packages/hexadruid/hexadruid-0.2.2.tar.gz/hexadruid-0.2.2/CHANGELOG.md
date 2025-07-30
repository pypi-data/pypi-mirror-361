# Changelog

# Changelog for HexaDruid v2.1

## [2.1] - 2025-07-12
### Added
- Full dynamic schema inference with null threshold and optional column protection.
- Enhanced DRTree to provide concise or detailed shard predicate descriptions.
- Smart salting with auto parameter tuning based on data distribution and Spark parallelism.
- Key detection improved to find primary and composite keys with confidence scoring.
- Adaptive shuffle tuning to optimize Spark partition count based on data size.
- Interactive advisor class for guided skew and grouping column selection.
- Detailed profiling output including null fractions, cardinality, and data types.
- Support for robust null handling and optional auto-drop of highly null columns.
- Visualization of original vs salted data z-scores saved as PNG files.
- Logging improvements and time measurement utilities for performance tracking.

### Fixed
- Fixed bug in schemaVisor where typed DataFrame was not properly initialized before casting.
- Fixed DRTree `to_dict` method to accept concise output flag without breaking compatibility.
- Corrected skew detection to avoid exceptions on malformed or missing numeric columns.
- Fixed headerless CSV detection logic to correctly drop header rows after renaming.
- Improved error handling during casting operations to use `try_cast` and avoid job failures.

### Removed
- Deprecated earlier static methods replaced by better instance method implementations.
- Removed hard-coded default partitions in favor of dynamic tuning.

### Notes
- This release lays the groundwork for full multi-format input support (CSV, JSON, Parquet, Avro, DB tables).
- Next updates will focus on enhanced schema inference, multi-format ingestion, and streaming support.
---
## [0.2.0] - 2025-07-12
### Changed
- Rebuilt core as obfuscated module using Nuitka for code protection.
- Removed all unnecessary files and previous builds.
- Improved compatibility and reduced source code exposure for SaaS deployment.
- Bugfixes and performance optimizations.

---

## [1.9] - 2025-07-12

### Changed
- Core module (`hexadruid_core.py`) fully obfuscated and now distributed as a compiled binary (`hexadruid_core.pyd`) for enhanced security and IP protection.
- Improved internal error handling during schema inference and data casting, making HexaDruid far more robust on dirty, real-world data.
- Updated `schemaVisor()` to use `try_cast` for all numeric, date, and timestamp conversions, auto-nullifying malformed values and preventing pipeline crashes.
- Enhanced dynamic header detection and handling for headerless and corrupted CSV/Parquet files.
- Smarter dropping of all-null and garbage columns based on robust sampling.
- Performance tuning and minor bug fixes for DataFrame analysis and partitioning.
- Refactored package layout to remove legacy files and simplify the import structure.

### Added
- Dynamic fallback for cases when no skewed columns are detected: HexaDruid now skips salting automatically and informs the user.
- Improved debug and info logging for all major steps, making pipeline issues easier to trace.

### Security
- Major codebase obfuscation using Nuitka; core business logic now protected as compiled bytecode.

---

## [0.1.8] - 2025-07-09

### Major Enhancements

- **Refactored Smart Schema Detection**:  
  - Now robustly auto-casts string columns to `int`/`double` where >90% of sampled values are numeric.
  - Handles malformed values gracefully—falls back to string or double if too many nulls after casting.
  - Fully tolerant of headerless files (no error or failure on missing headers).

- **Null-Tolerant Type Coercion**:  
  - All numeric inferences are now *null-tolerant* (columns with malformed values are safely cast, no job crash).

- **Improved DRTree Logic**:  
  - Logical sharding works even on datasets with minimal or non-skewed columns.
  - DRTree gracefully falls back to a single logical shard if splits aren't viable.

- **Protected/Obfuscated Core**:  
  - Swapped out PyArmor for Nuitka to compile core logic as a `.pyd` binary module (not shipped as plaintext).
  - Obfuscated `_core.py` is never exposed in the PyPI or GitHub repo.
  - Updated `.gitignore` to strictly block all core binary artifacts and sensitive files.

### API & Usability

- `schemaVisor()`:
  - Now *never* fails on files without headers; can be safely called on any flat file.
  - User headers can be optionally injected.

- **Docs & Packaging**
  - Improved `setup.py` and packaging logic to prevent sensitive files from being published.
  - Updated `.gitignore` to reflect new obfuscation and build pipeline.
  - API Reference and Project Architecture included in documentation.

---

## [0.1.7] - 2025-07-09
### Added
- Public PyPI release
- DRTree logic for shard-wise filtering
- Smart salting with Z-score/IQR support
- Primary/composite key detection
- Auto parameter tuning advisor
- Schema inference with safe coercion

### Changed
- Obfuscated internal `_core.py` logic with pyarmor

### Removed
- Legacy CLI interface (will re-add in future)
