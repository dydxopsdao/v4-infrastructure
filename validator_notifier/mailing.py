# Code adapted from: https://docs.aws.amazon.com/ses/latest/dg/send-an-email-using-sdk-programmatically.html

import boto3
from botocore.exceptions import ClientError

# The character encoding for the email.
CHARSET = "UTF-8"


class Mailer:
    def __init__(self, sender, region) -> None:
        self.client = boto3.client("ses", region_name=region)
        self.sender = sender

    def send(self, subject: str, message: str, recipient: str):
        # Try to send the email.
        try:
            # Provide the contents of the email.
            # Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses/client/send_email.html
            response = self.client.send_email(
                Destination={
                    "ToAddresses": [
                        recipient,
                    ],
                },
                Message={
                    "Body": {
                        "Text": {
                            "Charset": CHARSET,
                            "Data": message,
                        },
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": subject,
                    },
                },
                Source=self.sender,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            print("Email sent! Message ID:"),
            print(response["MessageId"])
