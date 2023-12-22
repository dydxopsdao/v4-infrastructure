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


def run(event, context):
    logger.info(f"Invoked with: {event}")

    raw_private_key = os.environ['RSA_PRIVATE_KEY'].encode("utf-8")
    private_key = read_private_key(raw_private_key)

    signature_bytes = sign_message(private_key, event["message"])
    signature_encoded = base64.b64encode(signature_bytes).decode("ascii")

    outgoing_message = build_outgoing_message(event["message"], signature_encoded)
    email_client = Mailer(
        sender=os.environ["SENDER"],
        region=os.environ["EMAIL_AWS_REGION"],
    )
    for recipient in os.environ["RECIPIENTS"].split(","):
        logger.info(f"Sending to: {recipient}")
        email_client.send(
            subject="dYdX Chain: action required",
            message=outgoing_message,
            recipient=recipient,
        )

    response = {"signature_base64": signature_encoded}
    return json.dumps(response)


def read_private_key(raw_key: str):
    private_key = serialization.load_pem_private_key(
        raw_key,
        password=None,
    )
    return private_key


def sign_message(
    private_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey,
    message: str,
):
    signature = private_key.sign(
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature


def build_outgoing_message(message: str, signature: str):
    outgoing_message = f"{message}\n\n----- RSA signature -----\n{signature}"
    return outgoing_message
