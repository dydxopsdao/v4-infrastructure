"""
RSA Sign a Message using a private key

Just turns this example into a script:
    https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#signing
"""

import sys
import hashlib
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

if len(sys.argv) != 6:
    print(
        "USAGE: sign.py in-privkey in-pubkey in-message out-signature-raw out-signature-base64"
    )
    sys.exit(2)

privkeyfile = sys.argv[1]
pubkeyfile = sys.argv[2]
messagefile = sys.argv[3]
sigfile_raw = sys.argv[4]
sigfile_b64 = sys.argv[5]

with open(privkeyfile, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(), password=None, backend=default_backend()
    )

with open(pubkeyfile, "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read())

with open(messagefile, "r") as file_to_sign:
    message = file_to_sign.read().encode("utf-8")

signature = private_key.sign(
    message,
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256(),
)

with open(sigfile_raw, "wb") as to_sig_file:
    to_sig_file.write(signature)

with open(sigfile_b64, "wb") as to_sig_file:
    to_sig_file.write(base64.b64encode(signature))

public_key.verify(
    signature,
    message,
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256(),
)
