"""Encounter resource generator."""

from __future__ import annotations

import datetime as dt
import random
from typing import Any, Dict

from faker import Faker

from .utils import CODING_SYSTEMS, build_period, build_reference, coded_text, new_uuid


def create_encounter(fake: Faker, patient_id: str, practitioner_id: str | None = None) -> Dict[str, Any]:
    """Create an Encounter tied to a patient and optional practitioner."""

    encounter_id = new_uuid()
    encounter_code = random.choice(CODING_SYSTEMS["encounter"])
    start = fake.date_time_between(start_date="-2y", end_date="now", tzinfo=dt.timezone.utc)
    period = build_period(start, hours=random.randint(1, 72))

    participants = []
    if practitioner_id:
        participants.append({"individual": build_reference("Practitioner", practitioner_id)})

    return {
        "resourceType": "Encounter",
        "id": encounter_id,
        "status": "finished",
        "class": encounter_code,
        "type": [coded_text(**encounter_code)],
        "subject": build_reference("Patient", patient_id),
        "participant": participants,
        "period": period,
        "location": [
            {
                "location": {
                    "display": f"{fake.company()} Medical Center",
                },
            }
        ],
    }
