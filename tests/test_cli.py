import json
from pathlib import Path

import pytest

from fhir_generator.cli import load_resources_from_dir
from fhir_generator.main import FHIRDataGenerator


def test_load_resources_ignores_bundles(tmp_path: Path) -> None:
    patient = {"resourceType": "Patient", "id": "123"}
    bundle = {"resourceType": "Bundle", "id": "bundle", "entry": []}

    patient_file = tmp_path / "patient.json"
    bundle_file = tmp_path / "bundle.json"
    patient_file.write_text(json.dumps(patient))
    bundle_file.write_text(json.dumps(bundle))

    resources = load_resources_from_dir(tmp_path)
    assert len(resources) == 1
    assert resources[0]["resourceType"] == "Patient"


def test_generate_dataset_invalid_count() -> None:
    generator = FHIRDataGenerator()
    with pytest.raises(ValueError):
        generator.generate_dataset(0)


def test_export_csv_summary(tmp_path: Path) -> None:
    generator = FHIRDataGenerator(seed=101)
    dataset = generator.generate_dataset(1)
    csv_path = tmp_path / "summary.csv"

    generator.export_csv_summary(dataset, csv_path)

    contents = csv_path.read_text().splitlines()
    assert contents[0].startswith("patient_id")
    assert len(contents) == 2
