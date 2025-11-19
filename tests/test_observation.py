from fhir_generator.generators.observation import OBSERVATION_TYPES
from fhir_generator.main import FHIRDataGenerator


def test_observation_values_align() -> None:
    generator = FHIRDataGenerator(seed=5)
    resources = generator.generate_patient_resources()
    observations = [res for res in resources if res.get("resourceType") == "Observation"]

    assert {obs.get("code", {}).get("text") for obs in observations}
    for obs in observations:
        assert obs["status"] == "final"
        assert obs.get("subject")
        assert obs.get("encounter")

    assert len(observations) == len(OBSERVATION_TYPES)
