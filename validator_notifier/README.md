# Validator Notifier

An AWS Lambda function that signs the input message with an asymmetric key and then sends it via email to a predefined set of recipients.

The input should be a JSON with the following format:

```
{
    "subject": "The world depends on you!",
    "content": "Please lorem your ipsums by tomorrow."
}
```

The outgoing emails will include the required message, along with its RSA signature.

## Assumptions

* AWS account
* Terraform Cloud
* Terraform CLI installed locally

## Usage

```
curl -v <lambda-endpoint> -H 'Authorization: Bearer <secret>' -d '{"subject": "lorem", "content":"ipsum"}'
```

The endpoint can be obtained from the Terraform output item: `lambda_endpoint`.

To verify the signature created by the Lambda function run:

```
base64 -d -i signature.base64 -o signature.raw
openssl dgst -sha256 -verify dydxops-pubkey.pem -signature signature.raw -sigopt rsa_padding_mode:pss message.txt
```

## Setup

### AWS account

It is recommended to created a dedicated AWS account for the project. This is a good practice for the sake of security and maintainability.

### SES

Set up Amazon SES by following their guide at: https://docs.aws.amazon.com/ses/latest/dg/setting-up.html#quick-start-verify-email-addresses .

### Private key

Prepare the RSA key:

```
openssl genrsa -out rsa-private.pem 4096
openssl rsa -in rsa-private.pem -outform PEM -pubout -out rsa-public.pem
```

### IAM user

Manually prepare an AWS IAM user for deploying the solution, preferably in a dedicated AWS account.
Call it e.g.: `terraformer`. The user should have the permissions to:

* Create IAM roles,
* Create Lambda functions,
* Create and manage ECR (container registry).

Go to `IAM -> Users -> [your new user] -> Permissions` and add the following managed policies:

* AmazonEC2ContainerRegistryFullAccess
* AWSLambda_FullAccess
* IAMFullAccess

### Terraform project

Set up a Terraform project in Terraform Cloud. Make sure to point the VCS trigger
to the `/validator_notifier/terraform` directory.

Add the following variables (note that some of them need to be of type
`env` and some of type `terraform`):

* `AWS_ACCESS_KEY_ID` - user your IAM user ID (env var)
* `AWS_SECRET_ACCESS_KEY` - user your IAM user secret key (env var)
* `AWS_REGION` - where you want the Lambda function deployed (env var)
* `rsa_private_key` - the RSA key generated earlier (terraform var)
* `recipients` - comma-separated list of emails (terraform var)
* `authorization_token` - a secret that has to be passed as bearer token (terraform var)

Create a _run_.

### Optional: dedicated invoker user

You will be able to call the Lambda function via HTTPS. However, if you want to invoke it via AWS internal systems
(e.g. for programmatic use cases, without going through the public Internet), you can create a separate user
with minimal permissions, say to list and invoke the function. An example IAM inline policy could look like this:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:ListFunctions",
                "lambda:GetFunction",
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

## Testing

Prepare environment

```
python3 -m venv python_venv
. ./python_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest
```

Run tests

```
# . ./python_venv/bin/activate
pytest
```

To manually build the image and upload it to the container registry (assuming it has been created):

```
export AWS_ACCESS_KEY_ID=<terraformer credential>
export AWS_SECRET_ACCESS_KEY=<terraformer credential>
export REGION=ap-northeast-1
export REPOSITORY=791066989954.dkr.ecr.ap-northeast-1.amazonaws.com/validator-notifier
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REPOSITORY
docker build --platform linux/amd64 -t validator-notifier:latest .
docker tag validator-notifier:latest ${REPOSITORY}:latest
docker push ${REPOSITORY}:latest
```

## Reading

* https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html
* https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function
* https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
* https://rietta.com/blog/openssl-generating-rsa-key-from-command/

## TODO

* Build Docker image via Terraform. Currently it's being built manually and pushed to ECR before applying Terraform.
* Authenticate via asymmetric cryptography - custom private key passed for the HTTPS call. Use API gateway if needed. Ditch the bearer token. Security!
* Use AWS KMS instead of plain env var to store the private key. Security!
