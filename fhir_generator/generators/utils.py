"""Utility helpers for FHIR resource generation."""

from __future__ import annotations

import datetime as dt
import random
import uuid
from typing import Any, Dict

from faker import Faker

CODING_SYSTEMS = {
    "gender": {
        "male": {"system": "http://hl7.org/fhir/administrative-gender", "code": "male", "display": "Male"},
        "female": {"system": "http://hl7.org/fhir/administrative-gender", "code": "female", "display": "Female"},
        "other": {"system": "http://hl7.org/fhir/administrative-gender", "code": "other", "display": "Other"},
    },
    "encounter": [
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB", "display": "ambulatory"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP", "display": "inpatient encounter"},
        {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "EMER", "display": "emergency"},
    ],
    "conditions": [
        {"system": "http://hl7.org/fhir/sid/icd-10", "code": "E11", "display": "Type 2 diabetes mellitus"},
        {"system": "http://hl7.org/fhir/sid/icd-10", "code": "I10", "display": "Essential (primary) hypertension"},
        {"system": "http://hl7.org/fhir/sid/icd-10", "code": "J45", "display": "Asthma"},
    ],
    "observations": {
        "blood_pressure": {"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"},
        "heart_rate": {"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"},
        "temperature": {"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"},
        "glucose": {"system": "http://loinc.org", "code": "2339-0", "display": "Glucose [Mass/volume] in Blood"},
        "cholesterol": {"system": "http://loinc.org", "code": "2093-3", "display": "Cholesterol"},
        "spo2": {
            "system": "http://loinc.org",
            "code": "59408-5",
            "display": "Oxygen saturation in Arterial blood by Pulse oximetry",
        },
    },
    "medications": [
        {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975", "display": "Metformin 500 MG"},
        {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "617314", "display": "Lisinopril 10 MG"},
        {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "198211", "display": "Simvastatin 20 MG"},
    ],
    "procedures": [
        {"system": "http://www.ama-assn.org/go/cpt", "code": "93000", "display": "Electrocardiogram"},
        {"system": "http://www.ama-assn.org/go/cpt", "code": "71020", "display": "Chest x-ray"},
    ],
}


def new_uuid() -> str:
    """Return a new UUID4 string."""

    return str(uuid.uuid4())


def build_reference(resource_type: str, resource_id: str) -> Dict[str, str]:
    """Construct a FHIR reference."""

    return {"reference": f"{resource_type}/{resource_id}"}


def coded_text(system: str, code: str, display: str) -> Dict[str, Any]:
    """Return a CodeableConcept dictionary."""

    return {"coding": [{"system": system, "code": code, "display": display}], "text": display}


def random_gender(fake: Faker) -> Dict[str, Any]:
    """Return a gender coding drawn from HL7 administrative gender values."""

    gender = random.choice(list(CODING_SYSTEMS["gender"].values()))
    return gender


def build_period(start: dt.datetime, hours: int = 1) -> Dict[str, str]:
    """Construct a period dictionary spanning a given number of hours from ``start``."""

    end = start + dt.timedelta(hours=hours)
    return {"start": start.isoformat(), "end": end.isoformat()}


def weight_height_for_age(age: int) -> Dict[str, float]:
    """Return rough height/weight estimates with gaussian noise for a given age."""

    base_weight = 20 + age * 0.8
    base_height = 120 + age * 1.2
    return {
        "weight": round(random.gauss(base_weight, 10), 1),
        "height": round(random.gauss(base_height, 8), 1),
    }


def random_practitioner(fake: Faker) -> Dict[str, Any]:
    """Create a practitioner identity with a plausible qualification."""

    practitioner_id = new_uuid()
    return {
        "resourceType": "Practitioner",
        "id": practitioner_id,
        "name": [
            {
                "family": fake.last_name(),
                "given": [fake.first_name()],
            }
        ],
        "qualification": [
            {
                "identifier": [
                    {
                        "system": "http://hl7.org/fhir/sid/us-npi",
                        "value": fake.bothify(text="#######"),
                    }
                ],
                "code": coded_text(
                    system="http://terminology.hl7.org/CodeSystem/v2-0360",
                    code="MD",
                    display="Doctor of Medicine",
                ),
            }
        ],
    }


def random_ethnicity(fake: Faker) -> Dict[str, Any]:
    """Return a randomized US-core ethnicity CodeableConcept."""

    values = [
        ("2135-2", "Hispanic or Latino"),
        ("2186-5", "Not Hispanic or Latino"),
    ]
    code, display = random.choice(values)
    return coded_text("urn:oid:2.16.840.1.113883.6.238", code, display)


def random_location(fake: Faker) -> Dict[str, str]:
    """Return a simple address structure."""

    return {
        "city": fake.city(),
        "state": fake.state_abbr(),
        "postalCode": fake.postcode(),
        "country": "USA",
    }


def observation_value(observation_type: str) -> Dict[str, Any]:
    """Generate structured observation values based on the requested type."""

    if observation_type == "blood_pressure":
        systolic = int(random.gauss(120, 15))
        diastolic = int(random.gauss(80, 10))
        return {
            "component": [
                {
                    "code": coded_text("http://loinc.org", "8480-6", "Systolic blood pressure"),
                    "valueQuantity": {"value": systolic, "unit": "mmHg"},
                },
                {
                    "code": coded_text("http://loinc.org", "8462-4", "Diastolic blood pressure"),
                    "valueQuantity": {"value": diastolic, "unit": "mmHg"},
                },
            ]
        }
    if observation_type == "heart_rate":
        return {"valueQuantity": {"value": int(random.gauss(72, 8)), "unit": "beats/min"}}
    if observation_type == "temperature":
        return {"valueQuantity": {"value": round(random.gauss(98.6, 0.7), 1), "unit": "F"}}
    if observation_type == "glucose":
        return {"valueQuantity": {"value": round(random.gauss(100, 25), 1), "unit": "mg/dL"}}
    if observation_type == "cholesterol":
        return {"valueQuantity": {"value": round(random.gauss(190, 35), 1), "unit": "mg/dL"}}
    if observation_type == "spo2":
        return {"valueQuantity": {"value": round(random.gauss(97, 2), 1), "unit": "%"}}
    return {"valueString": "Synthetic observation"}


def current_period(hours: int = 1) -> Dict[str, str]:
    """Return a period anchored to now with the given duration in hours."""

    start = dt.datetime.now(dt.timezone.utc)
    return build_period(start, hours=hours)


def pick_weighted(values: Dict[Any, float]) -> Any:
    """Select a key from a weight mapping using roulette-wheel selection."""

    total = sum(values.values())
    rand = random.uniform(0, total)
    cumulative = 0.0
    for item, weight in values.items():
        cumulative += weight
        if rand <= cumulative:
            return item
    return item
