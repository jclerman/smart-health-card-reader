"""Pytest fixtures common to the entire project."""
import pytest

from smart_health_card_reader.parse import remove_prefix

TEST_QR_CODE = (
    "shc:/567629095243206034602924374044603122295953265460346029254077280433602870286471"
    "67452228092861333145643765314159064022030645045908564355034142454136403706366541713"
    "72412363803043756220467374075323239254334433260573601064529295312707424284350386122"
    "12767168367567417255366703343736256473453800242139440770252507263124235736570011321"
    "05221716234384040064053115727615607001120754022122323263428420068703024705875260023"
    "60600327247067572123683521426424636168246055032432215569562773696368061237550404045"
    "56364050631642242033312213524072850441150772856074109555975363459657144674408294173"
    "03374077610769632608423612352171582367544020536355215703000765767060421268357606122"
    "42708733774425545633677770072036305033258526111246331502464050757773665263420122967"
    "39533839247769202776626162453542061074647457060073605321505720280020732566570654663"
    "92107585860613335275869384233235064325808693754660057063261776766397136582506607030"
    "50240825453957560942554333686804594244672706393935725065075311405960675922617070432"
    "76724735221453830667343537058240936456323126307342852280873750009264526733809553504"
    "39545321434040326508635820761007380543703476433668447759416234067303523365530674053"
    "87624644557251060702357306521217123637577313067681010765912115956592877343206293644"
    "55286004106408736560352569063625751254642536406466686024694231650835451141526611125"
    "41105422310437753445560505507296643257367002074012565350671624361636404246039763375"
    "30573024260626522124051059753077230500526258555852116565684060124562404539756762242"
    "7711030536265430375437436564540213040452945435375325336"
)
TEST_FULL_B64 = (
    "eyJ6aXAiOiJERUYiLCJhbGciOiJFUzI1NiIsImtpZCI6IjNLZmRnLVh3UC03Z1h5eXd0VWZVQUR3QnVtRE9QS01ReC1pRUxMMTFXOXMifQ"
    "."
    "3ZJJb9swEIX_SjC9ytqQxpVudQp0ORQFmvZS-EBTY4sFF4GLEDfQf-8M7aBtkOSUU3Ub8fHje4-8AxUC9DDGOIW-qsKEsgxG-Dii0HEspfBDqPBWm"
    "EljqEid0EMBdreHvrlq39Rd111dlm23LmCW0N9BPE4I_Y8_zIe4V6dhxQOhntYpY5JVv0RUzj4rlG5WQ9PBtgDpcUAbldBf0-4nysiW9qPy39EH5v"
    "RwWdZlQzz-u0l20Mgaj8ElL_Em24fzQnGOA9JpTbSTEzrAHykjkZPW37wmwf3-vibB_fAI-AvFof3coTB4ggijNPHgrSWND_mMg5rRco-f3MjzpoT"
    "tQgF3isK_E5FZTfe6WdXNqq1hWYpH3TTPu_n4b8UhiphCjssXHpEvaBZSKovXbsgE6QZlD9l4OIaI5vx-6GZGvS6dP1TcbBXUUMn5lgAy74S2XsOy"
    "XQqYzhVkO3v0aNnb3w2SyEmZfF7isDfKnBBtDlxzLKpq77yh98hehIzOM3JQYdIi17m5vniPFr3QFx9cmFQUmoqiErWLn5PZ8Vao89c82WD7XzbYd"
    "i_d4JoXFvp-Aw"
    "."
    "FnP3tkXjlm1EiTyNxKfKEG3GaBE27hxKzD2-akgdga8nnqUi9ZkUZTxpkEHt7KbknX0xXwQeZUBKUZJZXbxMbQ"
)
TEST_B64_SIG = "FnP3tkXjlm1EiTyNxKfKEG3GaBE27hxKzD2-akgdga8nnqUi9ZkUZTxpkEHt7KbknX0xXwQeZUBKUZJZXbxMbQ"


@pytest.fixture(scope="session")
def qr_int_str() -> str:
    """Pytest fixture providing the digit-string encoded by a SMART Health Card QR code, without the 'shc:/' prefix."""
    return remove_prefix(TEST_QR_CODE)


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
