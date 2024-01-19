import base64

import boto3
from botocore.exceptions import ClientError

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key


SIGNING_ALGORITHM = "RSASSA_PSS_SHA_256"


class Signer:
    def __init__(self, region, key_id, logger, algorithm=SIGNING_ALGORITHM) -> None:
        self.client = boto3.client("kms", region_name=region)
        self.key_id = key_id
        self.algorithm = algorithm
        self.logger = logger

    def sign(self, message: bytes) -> bytes:
        self.logger.info(f"Signing: key_id={self.key_id} algorithm={self.algorithm} message_length={len(message)}")
        self.logger.info(f"Message ({type(message)}):")
        self.logger.info(message)
        try:
            # Docs:
            # - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms/client/sign.html
            response = self.client.sign(
                KeyId=self.key_id,
                Message=message,
                MessageType="RAW",
                SigningAlgorithm=self.algorithm,
            )
            signature = response["Signature"]
        except ClientError as e:
            self.logger.info(e.response["Error"]["Message"])

        self.logger.info("Signature created:")
        self.logger.info(signature)

        # --- debugging ---
        pub_response = self.client.get_public_key(KeyId=self.key_id)
        self.logger.info("Public key response:")
        self.logger.info(pub_response)
        public_key=load_pem_public_key(f"-----BEGIN PUBLIC KEY-----\n{base64.b64encode(pub_response['PublicKey']).decode('ascii')}\n-----END PUBLIC KEY-----\n".encode('ascii'))
        self.verify(
            signature,
            message,
            public_key=public_key,
        )
        # --- debugging ---

        return signature

    def verify(
        self,
        signature: bytes,
        message: bytes,
        public_key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey,
    ):
        self.logger.info("Verifying message:")
        self.logger.info(message)
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        self.logger.info("Public key:")
        self.logger.info(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("ascii")
        )
