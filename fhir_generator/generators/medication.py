"""Medication request generator."""

from __future__ import annotations

import datetime as dt
import random
from typing import Any, Dict

from faker import Faker

from .utils import CODING_SYSTEMS, build_reference, coded_text, new_uuid


def create_medication_request(
    fake: Faker, patient_id: str, practitioner_id: str | None = None, encounter_id: str | None = None
) -> Dict[str, Any]:
    """Create a MedicationRequest ordering a common therapy."""

    med_code = random.choice(CODING_SYSTEMS["medications"])
    request_id = new_uuid()
    authored_on = dt.datetime.now(dt.timezone.utc).isoformat()

    medication_request = {
        "resourceType": "MedicationRequest",
        "id": request_id,
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": coded_text(**med_code),
        "subject": build_reference("Patient", patient_id),
        "authoredOn": authored_on,
        "dosageInstruction": [
            {
                "sequence": 1,
                "text": f"Take {random.randint(1, 2)} tablet(s) by mouth daily",
            }
        ],
    }

    if practitioner_id:
        medication_request["requester"] = build_reference("Practitioner", practitioner_id)
    if encounter_id:
        medication_request["encounter"] = build_reference("Encounter", encounter_id)

    return medication_request
