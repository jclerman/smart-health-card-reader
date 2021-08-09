"""Pytest fixtures common to the entire project."""
import pytest


@pytest.fixture(scope="session")
def test_jws_payload() -> str:
    """Return a JWS payload as a pytest test-fixture."""
    return (
        '{"iss":"https://spec.smarthealth.cards/examples/issuer","nbf":1628099964.297,'
        '"vc":{"type":["https://smarthealth.cards#health-card","https://smarthealth.cards#immunization",'
        '"https://smarthealth.cards#covid19"],"credentialSubject":{"fhirVersion":"4.0.1","fhirBundle":'
        '{"resourceType":"Bundle","type":"collection","entry":[{"fullUrl":"resource:0","resource":'
        '{"resourceType":"Patient","name":[{"family":"Anyperson","given":["John","B."]}],'
        '"birthDate":"1951-01-20"}},{"fullUrl":"resource:1","resource":{"resourceType":"Immunization",'
        '"status":"completed","vaccineCode":{"coding":[{"system":"http://hl7.org/fhir/sid/cvx","code":'
        '"207"}]},"patient":{"reference":"resource:0"},"occurrenceDateTime":"2021-01-01","performer":[{'
        '"actor":{"display":"ABC General Hospital"}}],"lotNumber":"0000001"}},{"fullUrl":"resource:2",'
        '"resource":{"resourceType":"Immunization","status":"completed","vaccineCode":{"coding":[{"system"'
        ':"http://hl7.org/fhir/sid/cvx","code":"207"}]},"patient":{"reference":"resource:0"},'
        '"occurrenceDateTime":"2021-01-29","performer":[{"actor":{"display":"ABC General Hospital"}}],'
        '"lotNumber":"0000007"}}]}}}}'
    )


@pytest.fixture(scope="session")
def pk_url() -> str:
    """Return a public-key URL as a pytest test-fixture."""
    return "https://spec.smarthealth.cards/examples/issuer/.well-known/jwks.json"
