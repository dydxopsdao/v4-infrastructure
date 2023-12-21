import base64
import json
import logging
import os

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run(event, context):
    logger.info(f"Invoked with: {event}")
    raw_private_key = os.environ['RSA_PRIVATE_KEY'].encode("utf-8")
    private_key = read_private_key(raw_private_key)
    signature = sign_message(private_key, event["message"])
    data = {"signature_base64": base64.b64encode(signature).decode("ascii")}
    return json.dumps(data)


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
