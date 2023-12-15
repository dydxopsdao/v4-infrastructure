import base64
import json
import logging

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run(event, context=None):
    message = event["message"]
    private_key = read_private_key()
    signature = sign_message(private_key, message)
    data = {"signed_message_base64": base64.b64encode(signature).decode("ascii")}
    return json.dumps(data)


def read_private_key():
    # TODO: read from envvar or config file
    with open(
        "./rsa-private.pem",  # TODO: move to AWS vault
        "rb",
    ) as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
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
