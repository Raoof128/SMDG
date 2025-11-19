"""Patient resource generator."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict

from faker import Faker

from .utils import new_uuid, random_ethnicity, random_gender, random_location, weight_height_for_age


def create_patient(fake: Faker) -> Dict[str, Any]:
    """Create a Patient resource with realistic demographic signals."""

    patient_id = new_uuid()
    gender = random_gender(fake)
    birth_date = fake.date_of_birth(minimum_age=0, maximum_age=90)
    age = (dt.date.today() - birth_date).days // 365
    body = weight_height_for_age(age)

    return {
        "resourceType": "Patient",
        "id": patient_id,
        "identifier": [
            {
                "use": "official",
                "system": "http://hospital.smarthealth.org/mrn",
                "value": fake.unique.bothify(text="??#####"),
            }
        ],
        "name": [
            {
                "family": fake.last_name(),
                "given": [fake.first_name()],
            }
        ],
        "gender": gender["code"],
        "birthDate": birth_date.isoformat(),
        "extension": [
            {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                "valueCodeableConcept": random_ethnicity(fake),
            }
        ],
        "address": [
            {
                "line": [fake.street_address()],
                **random_location(fake),
            }
        ],
        "telecom": [
            {"system": "phone", "value": fake.phone_number(), "use": "mobile"},
            {"system": "email", "value": fake.email(), "use": "home"},
        ],
        "extension_body": {
            "height_cm": body["height"],
            "weight_kg": body["weight"],
        },
    }
