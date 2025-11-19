"""Primary entry point for generating synthetic FHIR data.

This module exposes :class:`FHIRDataGenerator`, an orchestrator responsible for
assembling coherent clinical stories, exporting resources to disk, and
producing CSV summaries or FHIR Bundles. The generator intentionally keeps a
small dependency footprint while still emitting realistic values suitable for
integration tests and analytics sandboxes.
"""

from __future__ import annotations

import csv
import json
import logging
import random
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from faker import Faker

from .generators.allergy import create_allergy_intolerance
from .generators.condition import create_condition
from .generators.diagnostic_report import create_diagnostic_report
from .generators.encounter import create_encounter
from .generators.medication import create_medication_request
from .generators.observation import OBSERVATION_TYPES, create_observation
from .generators.patient import create_patient
from .generators.procedure import create_procedure
from .generators.utils import new_uuid, random_practitioner
from .validators.fhir_validator import validate_resource

LOGGER = logging.getLogger(__name__)


class FHIRDataGenerator:
    """Synthetic HL7 FHIR resource generator."""

    def __init__(self, seed: Optional[int] = None, locale: str = "en_US") -> None:
        """Create a generator with optional deterministic seeding.

        Args:
            seed: Optional seed value for reproducible outputs.
            locale: Faker locale string used for demographic fields.
        """

        self.fake = Faker(locale)
        self.seed = seed
        self.set_seed(seed)

    def set_seed(self, seed: Optional[int]) -> None:
        """Seed Python and Faker RNGs when a value is provided."""

        if seed is not None:
            random.seed(seed)
            self.fake.seed_instance(seed)
            LOGGER.info("Seed set to %s", seed)

    def generate_patient_resources(self) -> List[Dict]:
        """Generate a cohesive set of resources linked to a single patient."""

        practitioner = random_practitioner(self.fake)
        patient = create_patient(self.fake)
        encounter = create_encounter(self.fake, patient["id"], practitioner_id=practitioner["id"])
        observations = [create_observation(self.fake, patient["id"], encounter["id"], obs) for obs in OBSERVATION_TYPES]
        condition = create_condition(self.fake, patient["id"], encounter_id=encounter["id"])
        procedure = create_procedure(self.fake, patient["id"], encounter["id"])
        medication_request = create_medication_request(
            self.fake, patient["id"], practitioner_id=practitioner["id"], encounter_id=encounter["id"]
        )
        diagnostic_report = create_diagnostic_report(
            self.fake,
            patient_id=patient["id"],
            encounter_id=encounter["id"],
            observation_ids=[obs["id"] for obs in observations],
        )
        allergy = create_allergy_intolerance(self.fake, patient["id"])

        resources: List[Dict] = [
            practitioner,
            patient,
            encounter,
            condition,
            procedure,
            medication_request,
            diagnostic_report,
            allergy,
            *observations,
        ]

        LOGGER.debug("Generated %d resources for patient %s", len(resources), patient["id"])
        return resources

    def generate_dataset(self, count: int) -> List[List[Dict]]:
        """Generate multiple patient resource collections.

        Raises:
            ValueError: if ``count`` is less than 1.
        """

        if count < 1:
            msg = "Count must be at least 1"
            raise ValueError(msg)

        LOGGER.info("Generating dataset with %d patients", count)
        return [self.generate_patient_resources() for _ in range(count)]

    @staticmethod
    def bundle(resources: Iterable[Dict], bundle_type: str = "collection") -> Dict:
        """Wrap a list of resources in a FHIR Bundle structure."""

        entries = [
            {
                "fullUrl": f"urn:uuid:{res.get('id', new_uuid())}",
                "resource": res,
            }
            for res in resources
        ]
        return {"resourceType": "Bundle", "type": bundle_type, "entry": entries}

    def export_patient_folder(self, resources: List[Dict], output_dir: Path) -> None:
        """Persist a single patient's resources and bundle to disk."""

        output_dir.mkdir(parents=True, exist_ok=True)
        validated_resources: List[Dict] = []
        for resource in resources:
            if not validate_resource(resource):
                LOGGER.warning("Skipping invalid resource %s", resource.get("id"))
                continue
            filename = output_dir / f"{resource['resourceType'].lower()}_{resource['id']}.json"
            filename.write_text(json.dumps(resource, indent=2))
            validated_resources.append(resource)
            LOGGER.debug("Wrote %s", filename)

        bundle_path = output_dir / "bundle.json"
        bundle_path.write_text(json.dumps(self.bundle(validated_resources), indent=2))
        LOGGER.info("Saved bundle to %s", bundle_path)

    def export_dataset(self, dataset: List[List[Dict]], output_root: Path) -> None:
        """Persist a full dataset of patient folders and a consolidated bundle."""

        output_root.mkdir(parents=True, exist_ok=True)
        for idx, resources in enumerate(dataset, start=1):
            patient_folder = output_root / f"patient_{idx:03d}"
            self.export_patient_folder(resources, patient_folder)

        bundle_file = output_root / "synthetic_bundle.json"
        all_resources = [
            resource for patient_resources in dataset for resource in patient_resources if validate_resource(resource)
        ]
        bundle_file.write_text(json.dumps(self.bundle(all_resources), indent=2))
        LOGGER.info("Saved dataset bundle to %s", bundle_file)

    @staticmethod
    def export_csv_summary(dataset: List[List[Dict]], output_file: Path) -> None:
        """Emit a CSV summary of core demographics and vitals."""

        rows: List[Dict[str, str]] = []
        for resources in dataset:
            patient = next((res for res in resources if res.get("resourceType") == "Patient"), None)
            encounter = next((res for res in resources if res.get("resourceType") == "Encounter"), None)
            observation_map = {
                res.get("code", {}).get("text"): res for res in resources if res.get("resourceType") == "Observation"
            }
            if not patient or not encounter:
                continue

            rows.append(
                {
                    "patient_id": patient["id"],
                    "birth_date": patient.get("birthDate", ""),
                    "gender": patient.get("gender", ""),
                    "encounter_type": encounter.get("class", {}).get("display", ""),
                    "heart_rate": observation_map.get("Heart rate", {}).get("valueQuantity", {}).get("value", ""),
                    "blood_pressure_systolic": next(
                        (
                            comp.get("valueQuantity", {}).get("value", "")
                            for comp in observation_map.get("Blood pressure panel", {}).get("component", [])
                            if comp.get("code", {}).get("text") == "Systolic blood pressure"
                        ),
                        "",
                    ),
                }
            )

        if not rows:
            LOGGER.warning("No patient rows available for CSV export")
            output_file.write_text("")
            return

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        LOGGER.info("Saved CSV summary to %s", output_file)
