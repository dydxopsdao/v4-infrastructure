import base64
import json
import logging
import os

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from mailing import Mailer

logger = logging.getLogger()
logger.setLevel(logging.INFO)
{
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/",
    "rawQueryString": "",
    "headers": {
        "content-length": "25",
        "x-amzn-tls-cipher-suite": "ECDHE-RSA-AES128-GCM-SHA256",
        "x-amzn-tls-version": "TLSv1.2",
        "x-amzn-trace-id": "Root=1-65a145be-797c3178708174547ee8c103",
        "x-forwarded-proto": "https",
        "host": "in3lrxiar7xt56bm5omeew3ymq0itedm.lambda-url.ap-northeast-1.on.aws",
        "x-forwarded-port": "443",
        "content-type": "application/x-www-form-urlencoded",
        "x-forwarded-for": "193.42.98.9",
        "accept": "*/*",
        "user-agent": "curl/8.4.0",
    },
    "requestContext": {
        "accountId": "anonymous",
        "apiId": "in3lrxiar7xt56bm5omeew3ymq0itedm",
        "domainName": "in3lrxiar7xt56bm5omeew3ymq0itedm.lambda-url.ap-northeast-1.on.aws",
        "domainPrefix": "in3lrxiar7xt56bm5omeew3ymq0itedm",
        "http": {
            "method": "POST",
            "path": "/",
            "protocol": "HTTP/1.1",
            "sourceIp": "193.42.98.9",
            "userAgent": "curl/8.4.0",
        },
        "requestId": "16426a46-8b2e-4580-86fd-c7d1161f05fa",
        "routeKey": "$default",
        "stage": "$default",
        "time": "12/Jan/2024:13:59:26 +0000",
        "timeEpoch": 1705067966133,
    },
    "body": "eyJtZXNzYWdlIjogImh0dHBzIHRlc3QifQ==",
    "isBase64Encoded": True,
}


def run(event, context):
    logger.info(f"Invoked with: {event}")

    body_string = (
        base64.b64decode(event["body"]) if event["isBase64Encoded"] else event["body"]
    )
    body = json.loads(body_string)

    message = body["message"].encode("utf-8")
    logger.info(f"Message: {message}")

    try:
        ensure_authentication(event)
    except Exception as e:
        res = {"statusCode": 403}
        return res

    raw_private_key = os.environ["RSA_PRIVATE_KEY"].encode("ascii")
    private_key = read_private_key(raw_private_key)

    signature = sign_message(private_key, message)

    outgoing_message = build_outgoing_message(message.decode("utf-8"))
    email_client = Mailer(
        sender=os.environ["SENDER"],
        region=os.environ["EMAIL_AWS_REGION"],
    )
    for recipient in os.environ["RECIPIENTS"].split(","):
        logger.info(f"Sending to: {recipient}")
        email_client.send(
            subject="dYdX Chain: action required",
            outgoing_message=outgoing_message,
            signed_message=message,
            signature=signature,
            recipient=recipient,
        )

    response = {
        "signature_base64": base64.b64encode(signature).decode("ascii"),
    }
    return json.dumps(response)


def ensure_authentication(event):
    if "authorization" not in event["headers"]:
        raise Exception("Missing Authorization header")
    prefix_len = len("Bearer ")
    token = event["headers"]["authorization"][:prefix_len]
    if token != os.environ["AUTHORIZATION_TOKEN"]:
        logger.info(f"Given: {token} -- Expected: {os.environ['AUTHORIZATION_TOKEN']}")
        raise Exception("Invalid Authorization header")


def read_private_key(raw_key: str):
    private_key = serialization.load_pem_private_key(
        raw_key,
        password=None,
    )
    return private_key


def normalize_message(message: str):
    return message.replace("\r\n", "\n").replace("\r", "\n").strip()


def sign_message(
    private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey,
    message: bytes,
):
    logger.info(f"Message to sign: '{message.decode('utf-8')}'")
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature


def build_outgoing_message(message: str):
    outgoing_message = (
        f"{message}\n\n"
        "-----\n"
        "To verify the authenticity of this message:\n\n"
        "1) Download the two attached files - one with the message and one with the RSA signature.\n\n"
        "2) Ensure that you have the dYdX Ops Services public key in `dydxops-pubkey.pem`.\n\n"
        "3) Run:\n"
        "openssl dgst -sha256 -verify dydxops-pubkey.pem -signature signature.raw -sigopt rsa_padding_mode:pss message.txt\n\n"
        "You should see: 'Verified OK'.\n"
    )
    return outgoing_message
