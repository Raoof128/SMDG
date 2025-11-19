"""Observation resource generator."""

from __future__ import annotations

import datetime as dt
import random
from typing import Any, Dict

from faker import Faker

from .utils import CODING_SYSTEMS, build_reference, coded_text, new_uuid, observation_value

OBSERVATION_TYPES = ["blood_pressure", "heart_rate", "temperature", "glucose", "cholesterol", "spo2"]


def create_observation(
    fake: Faker, patient_id: str, encounter_id: str, observation_type: str | None = None
) -> Dict[str, Any]:
    """Create a vital-sign Observation linked to the provided patient and encounter."""

    obs_type = observation_type or random.choice(OBSERVATION_TYPES)
    obs_code = CODING_SYSTEMS["observations"].get(obs_type, {"system": "", "code": "", "display": obs_type})
    observation_id = new_uuid()

    observation = {
        "resourceType": "Observation",
        "id": observation_id,
        "status": "final",
        "category": [
            coded_text(
                system="http://terminology.hl7.org/CodeSystem/observation-category",
                code="vital-signs",
                display="Vital Signs",
            )
        ],
        "code": coded_text(**obs_code),
        "subject": build_reference("Patient", patient_id),
        "encounter": build_reference("Encounter", encounter_id),
        "effectiveDateTime": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    observation.update(observation_value(obs_type))
    return observation
