from fhir_generator.validators.fhir_validator import validate_collection, validate_resource


def test_validate_resource_rejects_bad_reference() -> None:
    resource = {
        "resourceType": "Observation",
        "id": "abc",
        "status": "final",
        "code": {"text": "demo"},
        "subject": {"reference": "NotAReference"},
    }

    assert validate_resource(resource) is False


def test_validate_collection_handles_multiple() -> None:
    patient = {"resourceType": "Patient", "id": "1", "name": ["foo"], "gender": "male", "birthDate": "2020-01-01"}
    encounter = {
        "resourceType": "Encounter",
        "id": "2",
        "status": "finished",
        "class": {"system": "http://hl7.org/fhir/v3/ActCode", "code": "AMB"},
        "subject": {"reference": "Patient/1"},
    }

    assert validate_collection([patient, encounter]) is True
