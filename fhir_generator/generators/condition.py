"""Condition resource generator."""

from __future__ import annotations

import datetime as dt
import random
from typing import Any, Dict

from faker import Faker

from .utils import CODING_SYSTEMS, build_reference, coded_text, new_uuid


def create_condition(fake: Faker, patient_id: str, encounter_id: str | None = None) -> Dict[str, Any]:
    """Create a synthetic active Condition for a patient."""

    condition_code = random.choice(CODING_SYSTEMS["conditions"])
    condition_id = new_uuid()
    recorded_date = dt.datetime.now(dt.timezone.utc).isoformat()
    condition = {
        "resourceType": "Condition",
        "id": condition_id,
        "clinicalStatus": coded_text("http://terminology.hl7.org/CodeSystem/condition-clinical", "active", "Active"),
        "verificationStatus": coded_text(
            "http://terminology.hl7.org/CodeSystem/condition-ver-status", "confirmed", "Confirmed"
        ),
        "code": coded_text(**condition_code),
        "subject": build_reference("Patient", patient_id),
        "recordedDate": recorded_date,
    }
    if encounter_id:
        condition["encounter"] = build_reference("Encounter", encounter_id)
    return condition
