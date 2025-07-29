# framezip

A lightweight Python module for **packing** and **unpacking** pandas DataFrames by grouping rows into list-aggregated columns and exploding them back into individual rows.

---

## Features

- **Pack** rows sharing common keys into a single row with list-aggregated columns.
- **Unpack** those list columns back into multiple rows.
- Flexible column referencing by name or integer index.

---

## Installation

Make sure you have pandas installed:

```
pip install framezip
```

## Use Cases

* Aggregate user sessions or grouped events into compact representations.
* Compress DataFrame rows for efficient storage or transfer.
* Switch easily between grouped (packed) and row-wise (unpacked) views.
* Prepare data for modeling or reporting workflows requiring different granularities.

## Notes

* Accepts column indices or names for flexibility.
* Uses pandas groupby().agg(list) and explode() for performance.
* Requires pandas version 0.25 or later (for explode() support).
