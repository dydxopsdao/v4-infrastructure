import base64
import json
import logging
import os

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from mailing import Mailer
from signing import Signer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


MAX_MESSAGE_LENGTH = 4096


class MessageTooLongError(Exception):
    pass


def run(event, context):
    try:
        ensure_authentication(event)
    except Exception as e:
        logger.info(f"Authentication failed: {e}")
        return {"statusCode": 403}

    try:
        subject, unified_message, decorated_content = validate_input(event)
    except MessageTooLongError as e:
        logger.info("Message is too long")
        return {
            "statusCode": 400,
            "body": f"Message is too long. Maximum length is {MAX_MESSAGE_LENGTH}.",
        }
    except Exception as e:
        logger.info(f"Input validation failed: {e}")
        return {"statusCode": 400}

    raw_private_key = os.environ["RSA_PRIVATE_KEY"].encode("ascii")
    private_key = read_private_key(raw_private_key)
    signature = sign_message(private_key, unified_message)
    signature_base64 = base64.b64encode(signature).decode("ascii")

    send_emails(subject, decorated_content, unified_message, signature)

    # --- TEMP ---
    print("Checks...")
    kms_signer = Signer(
        region=os.environ["EMAIL_AWS_REGION"],
        key_id=os.environ["KMS_SIGNING_KEY_ID"],
    )
    kms_signature = kms_signer.sign(unified_message)
    print(f"KMS signature: {kms_signature}")
    print(f"Python signature: {signature_base64}")
    # --- TEMP ---

    response = {
        "signature_base64": signature_base64,
    }
    return json.dumps(response)


def ensure_authentication(event):
    if "authorization" not in event["headers"]:
        raise Exception("Missing Authorization header")
    prefix_len = len("Bearer ")
    token = event["headers"]["authorization"][prefix_len:]
    if token != os.environ["AUTHORIZATION_TOKEN"]:
        raise Exception("Invalid Authorization header")


def validate_input(event):
    body_string = (
        base64.b64decode(event["body"]) if event["isBase64Encoded"] else event["body"]
    )
    body = json.loads(body_string)

    subject = body["subject"]
    content = body["content"]
    logger.info(f"Subject: {subject}; Content: {content}")

    unified_message = f"{subject}\n\n{content}".encode("utf-8")
    if len(unified_message) > MAX_MESSAGE_LENGTH:
        raise MessageTooLongError()

    decorated_content = decorate_content(content)

    return subject, unified_message, decorated_content


def decorate_content(original_message: str) -> str:
    decorated_message = (
        f"{original_message}\n\n"
        "-----\n"
        "To verify the authenticity of this message:\n\n"
        "1) Download the two attached files - one with the message and one with the RSA signature.\n"
        "2) Ensure that you have the dYdX Ops Services public key in `dydxops-pubkey.pem`.\n"
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


def send_emails(
    subject: str, decorated_content: str, unified_message: bytes, signature: bytes
):
    email_client = Mailer(
        sender=os.environ["SENDER"],
        region=os.environ["EMAIL_AWS_REGION"],
    )
    for recipient_raw in os.environ["RECIPIENTS"].split(","):
        recipient_cleaned = recipient_raw.strip()
        if not recipient_cleaned:
            continue
        logger.info(f"Sending to: {recipient_cleaned}")
        email_client.send(
            subject=subject,
            content=decorated_content,
            unified_message=unified_message,
            signature=signature,
            recipient=recipient_cleaned,
        )
