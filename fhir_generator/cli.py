"""Command line interface for the FHIR data generator."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import List

from .main import FHIRDataGenerator

LOGGER = logging.getLogger(__name__)


def configure_logging(verbose: bool = False) -> None:
    """Configure root logging once per CLI invocation."""

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthetic FHIR data generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    patient_parser = subparsers.add_parser("create-patient", help="Generate a single patient resource")
    patient_parser.add_argument("--output", type=Path, help="Path to write the patient JSON")
    patient_parser.add_argument("--seed", type=int, help="Seed for deterministic output")

    dataset_parser = subparsers.add_parser("create-dataset", help="Generate a dataset of synthetic patients")
    dataset_parser.add_argument("--count", type=int, default=1, help="Number of patients to generate")
    dataset_parser.add_argument("--output", type=Path, default=Path("output"), help="Directory to store output")
    dataset_parser.add_argument("--seed", type=int, help="Seed for deterministic output")
    dataset_parser.add_argument("--csv", action="store_true", help="Export CSV summary as well")

    bundle_parser = subparsers.add_parser("bundle", help="Create a bundle for previously generated resources")
    bundle_parser.add_argument("--input", type=Path, required=True, help="Directory containing patient folders")
    bundle_parser.add_argument("--output", type=Path, default=Path("output/synthetic_bundle.json"))

    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def load_resources_from_dir(path: Path) -> List[dict]:
    """Load non-bundle JSON resources from a directory tree."""

    resources: List[dict] = []
    for file in sorted(path.glob("**/*.json")):
        try:
            with file.open() as handle:
                resource = json.load(handle)
        except json.JSONDecodeError:
            LOGGER.error("Skipping invalid JSON file %s", file)
            continue
        if isinstance(resource, dict) and resource.get("resourceType") != "Bundle":
            resources.append(resource)
    return resources


def main(argv: List[str] | None = None) -> None:
    """Entrypoint used by ``python -m fhir_generator.cli``."""

    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.verbose)

    try:
        if args.command == "create-patient":
            generator = FHIRDataGenerator(seed=args.seed)
            resources = generator.generate_patient_resources()
            patient = next(res for res in resources if res.get("resourceType") == "Patient")
            output = json.dumps(patient, indent=2)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(output)
                LOGGER.info("Wrote patient to %s", args.output)
            else:
                print(output)
            return

        if args.command == "create-dataset":
            if args.count < 1:
                parser.error("--count must be at least 1")

            generator = FHIRDataGenerator(seed=args.seed)
            dataset = generator.generate_dataset(args.count)
            generator.export_dataset(dataset, args.output)
            if args.csv:
                csv_path = args.output / "summary.csv"
                generator.export_csv_summary(dataset, csv_path)
            return

        if args.command == "bundle":
            resources = load_resources_from_dir(args.input)
            generator = FHIRDataGenerator()
            bundle = generator.bundle(resources)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(bundle, indent=2))
            LOGGER.info("Wrote bundle to %s", args.output)
            return
    except Exception as exc:  # pragma: no cover - defensive top-level catch
        LOGGER.exception("Unhandled error: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
