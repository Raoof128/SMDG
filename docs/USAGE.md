# Usage Guide

This guide summarizes common ways to consume the Synthetic Medical Data Generator from the command line and as a Python module.

## Command Line

```bash
python -m fhir_generator.cli create-dataset --count 5 --output output --csv
```

Key options:

| Flag | Description |
| --- | --- |
| `--count` | Number of synthetic patients to generate (must be >= 1). |
| `--seed` | Seed for reproducible results. |
| `--output` | Target folder or bundle file path depending on the command. |
| `--csv` | When set on `create-dataset`, emit `summary.csv` next to JSON exports. |
| `--verbose` | Enable debug-level logging for troubleshooting. |

### Examples

* Single patient JSON to stdout: `python -m fhir_generator.cli create-patient`
* Deterministic patient to file: `python -m fhir_generator.cli create-patient --seed 2024 --output examples/patient.json`
* Consolidate existing JSON resources: `python -m fhir_generator.cli bundle --input output/patient_001 --output bundle.json`

## Python API

```python
from pathlib import Path
from fhir_generator.main import FHIRDataGenerator

generator = FHIRDataGenerator(seed=7)
dataset = generator.generate_dataset(count=2)
generator.export_dataset(dataset, Path("output"))
```

Key methods:

- `generate_patient_resources()` → list of resource dicts linked to a single patient.
- `generate_dataset(count)` → list of patient resource lists; validates `count` >= 1.
- `bundle(resources, bundle_type="collection")` → FHIR Bundle dict.
- `export_dataset(dataset, output_root)` → writes resource JSON, patient bundles, and consolidated bundle.
- `export_csv_summary(dataset, output_file)` → writes demographics/vitals summary.

## Validation

Structural validation runs before writing files. Invalid resources (missing required fields or malformed references) are logged and skipped to keep exported assets usable.

## Reproducibility

Pass `--seed <int>` to the CLI or `FHIRDataGenerator(seed=...)` to deterministic outputs for demos and tests.
