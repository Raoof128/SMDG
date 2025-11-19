"""Lightweight structural validator for generated FHIR resources."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterable

LOGGER = logging.getLogger(__name__)


REFERENCE_PATTERN = re.compile(r"^[A-Za-z]+/[A-Za-z0-9\-\.]{1,64}$")


REQUIRED_FIELDS = {
    "Patient": ["resourceType", "id", "name", "gender", "birthDate"],
    "Encounter": ["resourceType", "id", "status", "class", "subject"],
    "Observation": ["resourceType", "id", "status", "code", "subject"],
    "Condition": ["resourceType", "id", "code", "subject"],
    "MedicationRequest": ["resourceType", "id", "status", "intent", "medicationCodeableConcept", "subject"],
    "Procedure": ["resourceType", "id", "status", "code", "subject"],
    "DiagnosticReport": ["resourceType", "id", "status", "code", "subject"],
    "AllergyIntolerance": ["resourceType", "id", "code", "patient"],
}


def validate_resource(resource: Dict[str, Any]) -> bool:
    """Validate a single resource for structural completeness."""

    resource_type = resource.get("resourceType")
    if not resource_type:
        LOGGER.error("Missing resourceType in %s", resource)
        return False

    required = REQUIRED_FIELDS.get(resource_type, ["resourceType", "id"])
    missing = [field for field in required if field not in resource]
    if missing:
        LOGGER.error("Resource %s missing required fields: %s", resource_type, ", ".join(missing))
        return False

    if "id" in resource and not resource["id"]:
        LOGGER.error("Resource %s has empty id", resource_type)
        return False

    for reference_field in ("subject", "patient", "encounter"):
        if reference_field in resource:
            reference = resource[reference_field]
            if not isinstance(reference, dict) or "reference" not in reference:
                LOGGER.error("Resource %s has invalid reference in %s", resource_type, reference_field)
                return False
            if not REFERENCE_PATTERN.match(reference.get("reference", "")):
                LOGGER.error("Resource %s reference %s is not in <Type>/<id> form", resource_type, reference_field)
                return False

    return True


def validate_collection(resources: Iterable[Dict[str, Any]]) -> bool:
    """Validate multiple resources, returning True only if all pass."""

    valid = True
    for res in resources:
        valid = validate_resource(res) and valid
    return valid
