import base64
import hashlib
import json
import os

import boto3
import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pytest

import lambda_function


RSA_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIJQgIBADANBgkqhkiG9w0BAQEFAASCCSwwggkoAgEAAoICAQCp+iitDuMSqsH7
VEar5eI03ReXM2fsAUlQhUtSkpYczFMvta8fnUq1tKD71/XN1B6vDRRiJ0CsIR1U
g6X4Wts5Lmt4059RHPIBFD4E2d2pgIeQUaVwWJ+HyYx4AAS8/Dc+dSkahydr1apB
1ShxD00jP8AoCyCoYoylYqlEGp2NODprEWdjvxY1dYoaTZo/XyBWJp7xlBqKn1SN
08qAxPPAKc+SVQ5JwDTAQ7pcJhKggzKqrWBnFmLZxD2YHfOcfvEXrME6aDWsqHLd
tO0Uod+lCxHoXCPxN/OyhLBlPOHFIAJ+sR058/RfOkSKIfI10wl8f0MYv/KzKmY7
HVzpxqJQj4asbsGSLWM+tdSeE2BpTbWm6tj/LxF4pSFiobVC0bYdFS5LyntZRHn2
jQfpQnT0QvKBe39s8uDeY2gIVAMTUGInwL9NU5KHZHEBzwEX6921mHBI5pVLN6eK
YYutHmNT9UDE/jFhq5cpgqypEImR43nsMkYlLBz5HhnfoDNfBSHBFT5dT/zBtbUu
QVZPtGBkLVUVdhA+68fMwUqB7W9/Mafd2/Xz3StHddR10NgUt6m2UYOP8z+AFp42
XcLNPQ8tGP+c38ZDMHExbxNpefubOLOKNV6AeqV4rLXW1zgs3XXDMS6RpFZ6JDYc
K3oeOoCPB1Wk7EOEDPJ5QaMO5hQ1EwIDAQABAoICAEWiFcfPsXaUPaOYgtso8eJ2
MJPgm1IztLUn5hONubFSg0GoTHXHGjQWK10Au9H2dBuCYDdVnUjmx/03cWas0eI7
Agwdpca09O88O6wBFK272c1lpUDBDZmzF7iRSV+ic39Cv/P+Kkgi3/zYNhkbC57F
HxNIe7h/pt6Z7H3Z6XFQ952lI5XZUl/UJx9fazFK5xRj/fk5kyX238y6Vtsp1DGE
72QjNBdChlm9ZTsa3caj+L2zCSsyIIzVt+X5XzNdTadFPmOPDW4OFAB/fiBVsCkM
v+lQ1eib41neweS3bEY1NtBv/mkfZ50bYbi072Tdb6Vw/SvGdsavN/I/tTCQDy4G
gFaEW+gvoXEBIW6XHjZ3wxQchTuDmYdvRUD22PIS7r+wL056hwYCAL3TnPuK8NXJ
AHDh9hyCWXv3K13sYXkhVsrPJt61eUkS40huVIYo0urATK2KEzzVygBxhNAU+VFm
lBDMIrALP1JBIacUTJ9W2wrPGSNcrrAw3ZZFoMJerg0bDvbXhZpFmLMet41Q0kGg
L24VlrjMH26fYzvXMG+yYVvC6tzldKcILZRtDi3g0uJaA8wnqkkLNQTaka6y4yW+
saEv0tKTMpkei3+xDNx14lEpJMuVm0hASOx/2AAFmunw0I0E57/L11sVajEKXQNx
P7N3mxtSsImAOp3btB8BAoIBAQDbBQ05HN01S/UMTH+qAl4VhT0PPhoh5jBhldyf
ET4pqBMoFGY9jWZIdNMafdPoL/KkfFrwohuj4JrlnZGTyEKAjxIG/u9J085WYtFp
GdLegg4CA/6FSlKGC+UdwEor8G4LPHJ9Cv36u8TwUOta9EZiNopTVWx0Nq1PsDJY
wSSikPdJ59bASjhwm7c66Mv1F5M3wYwgmpwcZDNw8RDibCvIk/Z9wZ8Ip543R4rU
AJI3fpgQUrysnBfEPym19n6KOC9J0dBuR1egf75jh94Fty6PsP7aoc92BScu9dVq
+fPd+TamvYqAOoo445wVTtXTj/OGVAg5l+whSoVOilOX2dc9AoIBAQDGrUiCW/eu
dskuFdoidMx1lK+8PZo2KQqLbv32MEpqt4LEEkgDHO7uh7vQ31+6RBWCydArSy1g
Lva/BIqpp/94GhAtOazLk2iw39rLigLdhPcKweYVARC2bL/aeecgIMI3KVMc4hPr
mYJ4O5/nIXcay3PGzDxTCUNEXWdf8RV4YMVviGU9pxOwoLRv5jq+EWmmsP9ekUPj
mfYVSjsWy7o19Y/BnK+aEWzcGodDTQgAnmzanCunJiWZe+IYLKN61O0Cha0AaJ+H
Wa9L4el3MudLWSH6G7FgZ0fE/ExmZxxWzPQr574C9SQ2xcWIimuZwwMcSPdnKlhS
rN8KjU7F+IKPAoIBAQDC3h3DwQC4WNqwlKfJ1c1sDF4lX7XUj4BgcvwWszrByX8x
2+STw2lL8lWZbnbKUU7sNpCbJUC+cCqhPa629CjnRWRewRiacU9W4Rk9D/LkcoaQ
GImuglAmYBL8g4f6zDK84I1k4BDVs5cn0nd1N34gCDLOrmSOic9t5XEGMuKrmZvM
L/CMqfzJhGJkkZhWeyFLLHPG1okrYaO7S2Egc+oIzk0z2r/q7WgB+y90LQXrRkF5
1IN2eHNU8nXkJmq0BAVfAsUWOXenn8D/wXUzVKaixnIaiHmTokYYrDW0tqvZxdBw
TpgaOvucXjcTZk8tqxibXczroVZA0JMHLF/v7axpAoIBAHWP/CQHP5yg9ZKro5RY
ANRi00pUOXhq+K5hUy3mjWJwjJRxLOOKr2e+Mcj7JK4Xs5Lc0K2NoqATqjaF/Xc+
zdDHu2LHihQ8eeqPy+w9Ekz6bSSUcA1lv/nyh+RD1hwQxlvVvDSPIrJ699Ulkw01
pEDauvubxuZryL4fdxgylD3TJYFF+IJu5xvRPHQqjAAEVbwpaDMRSlbXt+IJNsXa
b6mWUSaEDPTh8sSbfga5Ak87b7Y8SyhxTjZwM+2SHHqGnGitqR1gy2VQEIaae4fp
Oyw+5fgVgvREqRdLI/pEcWR7itCgJLOjU3aFuMl+/wTRfHm0Q5FsYS8q1CBuVXqX
/skCggEAezKmCVOnKPQiJXXX3s2cZGtpcfgz5tFDwcZ9Fl9UsYhA+Oz6GlhYJUYu
cqS07tLh9FQIEpLUBjr0RTvyVOCnFyuSKFMFbrzqKYDHSQ5mQSw/eGmYGRCpPfzt
TwEW6bYwvbQ4yzXQLcKEua8D/Qpaj+HJU7xiv4LS7If5JUcPvM63FSH1IFQNjqcD
Eu8g/TaYlUmvgnmOy6U8nV2Szq8UlTsbV+7o3vbbhIzNZZqpDFPjmbpCGILaMRsh
/lDWLHpr9Rljorr1hTeciBwYcxqWzjT9GeGqjZUWWFpSeIrZFcq3WSOs0xETGQrQ
z6WohhfweRlSiRSWJlsaBzHWvYm+fA==
-----END PRIVATE KEY-----
"""


def test_integrity():
    message = "lorem"
    print("Message:")
    print(message)

    prehashed = hashlib.sha256(message.encode("utf-8")).hexdigest()
    print("Prehashed:")
    print(prehashed)

    private_key = serialization.load_pem_private_key(
        RSA_PRIVATE_KEY.encode("ascii"),
        password=None,
    )

    public_key = private_key.public_key()
    print("Public key:")
    print(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
    )

    signature = private_key.sign(
        prehashed.encode("ascii"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    print("Signature raw:")
    print(signature)

    print("Signature base64:")
    print(base64.b64encode(signature))


def test_smoke_lambda(monkeypatch, private_key):
    def mocked_boto3_client(*args, **kwargs):
        return MockedBoto3Client()

    message = "lorem"
    os.environ["RSA_PRIVATE_KEY"] = RSA_PRIVATE_KEY
    os.environ["EMAIL_AWS_REGION"] = "region"
    os.environ["SENDER"] = "sender"
    os.environ["RECIPIENTS"] = "recipient1,recipient2"
    monkeypatch.setattr(boto3, "client", mocked_boto3_client)

    result_raw = lambda_function.run(
        {"message": message},
        {"private_key": RSA_PRIVATE_KEY.encode("ascii")},
    )

    result_json = json.loads(result_raw)
    print("Signature in:", result_json["signature_base64"])
    signature = base64.b64decode(result_json["signature_base64"])
    print("Signature transformed:", base64.b64encode(signature).decode("ascii")) 
    verify_signature(
        signature,
        message,
        private_key.public_key(),
    )


@pytest.fixture
def private_key():
    return serialization.load_pem_private_key(
        RSA_PRIVATE_KEY.encode("ascii"),
        password=None,
    )


class MockedBoto3Client:
    def send_email(self, Destination, Message, Source):
        print("Sending email to:", Destination)
        return {"MessageId": "test-message-id"}


def verify_signature(
    signature: bytes,
    message: str,
    public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey,
):
    print("Message:", message.encode("utf-8"))
    public_key.verify(
        signature,
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    print("Public key:")
    print(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
    )
