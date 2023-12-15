import base64
import json

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import message_signer


def smoke_test():
    message = "lorem"
    private_key = _read_private_key()
    result_raw = message_signer.run({"message": message})
    result_json = json.loads(result_raw)
    signature = base64.b64decode(result_json["signed_message_base64"])
    _verify_signature(
        signature,
        message,
        private_key.public_key(),
    )


def _read_private_key():
    # TODO: generate ad hoc for tests
    with open(
        "./rsa-private.pem",  # TODO: move to AWS vault
        "rb",
    ) as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    return private_key


def _verify_signature(
    signature: bytes,
    message: str,
    public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey,
):
    public_key.verify(
        signature,
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )


if __name__ == "__main__":
    smoke_test()
