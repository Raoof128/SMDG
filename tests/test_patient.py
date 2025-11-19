from pathlib import Path

from fhir_generator.main import FHIRDataGenerator


def test_generate_single_patient(tmp_path: Path) -> None:
    generator = FHIRDataGenerator(seed=42)
    resources = generator.generate_patient_resources()
    patient = next(res for res in resources if res.get("resourceType") == "Patient")

    assert patient["resourceType"] == "Patient"
    assert patient["gender"] in {"male", "female", "other"}

    generator.export_patient_folder(resources, tmp_path)
    assert (tmp_path / "bundle.json").exists()


def test_bundle_creation() -> None:
    generator = FHIRDataGenerator(seed=1)
    resources = generator.generate_patient_resources()
    bundle = generator.bundle(resources)

    assert bundle["resourceType"] == "Bundle"
    assert len(bundle["entry"]) == len(resources)
