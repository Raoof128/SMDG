"""Allergy intolerance generator."""

from __future__ import annotations

import random
from typing import Any, Dict

from faker import Faker

from .utils import build_reference, coded_text, new_uuid

ALLERGENS = [
    ("http://snomed.info/sct", "91935009", "Peanut"),
    ("http://snomed.info/sct", "235719002", "Penicillin"),
    ("http://snomed.info/sct", "300916003", "Latex"),
]


def create_allergy_intolerance(fake: Faker, patient_id: str) -> Dict[str, Any]:
    """Create an AllergyIntolerance with a randomized allergen."""

    system, code, display = random.choice(ALLERGENS)
    allergy_id = new_uuid()

    return {
        "resourceType": "AllergyIntolerance",
        "id": allergy_id,
        "clinicalStatus": coded_text(
            "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical", "active", "Active"
        ),
        "verificationStatus": coded_text(
            "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification", "confirmed", "Confirmed"
        ),
        "code": coded_text(system, code, display),
        "patient": build_reference("Patient", patient_id),
        "reaction": [
            {
                "manifestation": [coded_text("http://snomed.info/sct", "271807003", "Rash")],
                "severity": random.choice(["mild", "moderate", "severe"]),
            }
        ],
    }
