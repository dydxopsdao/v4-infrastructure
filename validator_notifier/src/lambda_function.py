import base64
import json
import logging
import os

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from .mailing import Mailer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run(event, context):
    try:
        ensure_authentication(event)
    except Exception as e:
        logger.info(f"Authentication failed: {e}")
        return {"statusCode": 403}

    try:
        subject, signed_message, decorated_content = parse_input(event)
    except Exception as e:
        logger.info(f"Input parsing failed: {e}")
        return {"statusCode": 400}

    raw_private_key = os.environ["RSA_PRIVATE_KEY"].encode("ascii")
    private_key = read_private_key(raw_private_key)
    signature = sign_message(private_key, signed_message)

    email_client = Mailer(
        sender=os.environ["SENDER"],
        region=os.environ["EMAIL_AWS_REGION"],
    )
    for recipient in os.environ["RECIPIENTS"].split(","):
        logger.info(f"Sending to: {recipient}")
        email_client.send(
            subject=subject,
            content=decorated_content,
            signed_message=signed_message,
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
    token = event["headers"]["authorization"][prefix_len:]
    if token != os.environ["AUTHORIZATION_TOKEN"]:
        raise Exception("Invalid Authorization header")


def parse_input(event):
    body_string = (
        base64.b64decode(event["body"]) if event["isBase64Encoded"] else event["body"]
    )
    body = json.loads(body_string)

    subject = body["subject"]
    content = body["content"]
    logger.info(f"Subject: {subject}; Content: {content}")

    signed_message = f"{subject}\n\n{content}".encode("utf-8")
    decorated_content = decorate_content(content)

    return subject, signed_message, decorated_content


def decorate_content(original_message: str) -> str:
    decorated_message = (
        f"{original_message}\n\n"
        "-----\n"
        "To verify the authenticity of this message:\n\n"
        "1) Download the two attached files - one with the message and one with the RSA signature.\n\n"
        "2) Ensure that you have the dYdX Ops Services public key in `dydxops-pubkey.pem`.\n\n"
        "3) Run:\n"
        "openssl dgst -sha256 -verify dydxops-pubkey.pem -signature signature.raw -sigopt rsa_padding_mode:pss message.txt\n\n"
        "You should see: 'Verified OK'.\n"
    )
    return decorated_message


def read_private_key(raw_key: str):
    private_key = serialization.load_pem_private_key(
        raw_key,
        password=None,
    )
    return private_key


# See: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#signing
def sign_message(
    private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey,
    message: bytes,
) -> bytes:
    logger.info(f"Message to sign: '{message.decode('utf-8')}'")
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature
