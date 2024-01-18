import boto3
from botocore.exceptions import ClientError


SIGNING_ALGORITHM = "RSASSA_PSS_SHA_256"


class Signer:
    def __init__(self, region, key_id, algorithm=SIGNING_ALGORITHM) -> None:
        self.client = boto3.client("kms", region_name=region)
        self.key_id = key_id
        self.algorithm = algorithm

    def sign(self, message: str) -> bytes:
        print(f"Signing message; key_id={self.key_id} algorithm={self.algorithm} message_length={len(message)}")
        try:
            # Docs:
            # - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms/client/sign.html
            response = self.client.sign(
                KeyId=self.key_id,
                Message=message,
                MessageType="RAW",
                SigningAlgorithm=self.algorithm,
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            print("Signature created!")
            return response["Signature"]
