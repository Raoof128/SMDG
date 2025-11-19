"""Diagnostic report generator."""

from __future__ import annotations

import datetime as dt
import random
from typing import Any, Dict, List

from faker import Faker

from .utils import build_reference, coded_text, new_uuid

REPORT_CODES = [
    ("http://loinc.org", "58410-2", "Complete blood count"),
    ("http://loinc.org", "24323-8", "Lipid panel"),
    ("http://loinc.org", "2093-3", "Cholesterol"),
]


def create_diagnostic_report(
    fake: Faker, patient_id: str, encounter_id: str, observation_ids: List[str]
) -> Dict[str, Any]:
    """Create a DiagnosticReport referencing supplied observations."""

    code_system, code, display = random.choice(REPORT_CODES)
    report_id = new_uuid()
    issued = dt.datetime.now(dt.timezone.utc).isoformat()

    return {
        "resourceType": "DiagnosticReport",
        "id": report_id,
        "status": "final",
        "code": coded_text(code_system, code, display),
        "subject": build_reference("Patient", patient_id),
        "encounter": build_reference("Encounter", encounter_id),
        "result": [{"reference": f"Observation/{obs_id}"} for obs_id in observation_ids],
        "issued": issued,
    }
