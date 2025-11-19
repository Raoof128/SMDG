"""Procedure resource generator."""

from __future__ import annotations

import random
from typing import Any, Dict

from faker import Faker

from .utils import CODING_SYSTEMS, build_reference, coded_text, current_period, new_uuid


def create_procedure(fake: Faker, patient_id: str, encounter_id: str) -> Dict[str, Any]:
    """Create a Procedure resource for the supplied patient."""

    procedure_id = new_uuid()
    proc_code = random.choice(CODING_SYSTEMS["procedures"])
    period = current_period(hours=random.randint(1, 3))

    return {
        "resourceType": "Procedure",
        "id": procedure_id,
        "status": "completed",
        "code": coded_text(**proc_code),
        "subject": build_reference("Patient", patient_id),
        "encounter": build_reference("Encounter", encounter_id),
        "performedPeriod": period,
    }
