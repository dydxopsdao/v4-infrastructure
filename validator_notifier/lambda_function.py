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
    body = json.loads(event['body']) if event['isBase64Encoded'] else event['body']
    logger.info(f"Event body: {body}")


    raw_private_key = os.environ["RSA_PRIVATE_KEY"].encode("ascii")
    private_key = read_private_key(raw_private_key)

    message = event["message"].encode("utf-8")
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
        "2) Ensure that you have the dYdX Ops Services public key in `pubkey.pem`.\n\n"
        "3) Run:\n"
        "openssl dgst -sha256 -verify pubkey.pem -signature signature.raw -sigopt rsa_padding_mode:pss message.txt\n\n"
        "You should see: 'Verified OK'.\n"
    )
    return outgoing_message
