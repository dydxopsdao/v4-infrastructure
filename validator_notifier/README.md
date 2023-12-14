# Validator Notifier

An AWS Lambda function that signs the input message with an asymmetric key and then sends it via email to a predefined set of recipients.

The input should be a JSON with the following format:

```
{
    "subject": "The world on you depends",
    "content": "Please lorem your ipsums by tomorrow."
}
```

The outgoing emails will include the required message, along with its signature.

The signing key is RSA 4096 and the algorithm used is SHA-256 with the padding scheme PSS.

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
openssl dgst -sha256 -verify dydxops-pubkey.pem -signature signature.sig -sigopt rsa_padding_mode:pss message.txt
```

## Setup

### AWS account

It is recommended to created a dedicated AWS account for the project. This is a good practice for the sake of security and maintainability.

### SES

Set up Amazon SES by following their guide at: https://docs.aws.amazon.com/ses/latest/dg/setting-up.html#quick-start-verify-email-addresses .

### IAM user

Manually create an AWS IAM user for deploying the solution, preferably in a dedicated AWS account.
Call it e.g.: `terraformer`. Go to:
`IAM -> Users -> [your new user] -> Permissions -> Add permissions -> Attach policies directly`
and add the following managed policies:

* AmazonEC2ContainerRegistryFullAccess
* AWSLambda_FullAccess
* IAMFullAccess
* AWSCodeBuildAdminAccess
* AWSKeyManagementServicePowerUser

### Terraform project

Set up a Terraform project in Terraform Cloud called `validator-notifier`. Configure the source repository.
Make sure to point the VCS trigger to the `/validator_notifier/terraform` directory.

Add the following variables (note that some of them need to be of type `env` and some of type `terraform`):

Env vars:

* `AWS_ACCESS_KEY_ID` - your IAM user (e.g. terraformer)'s ID
* `AWS_SECRET_ACCESS_KEY` - your IAM user (e.g. terraformer)'s secret key
* `AWS_REGION` - where you want the Lambda function deployed

Terraform vars:

* `recipients` - comma-separated list of emails
* `authorization_token` - a secret that has to be passed as bearer token
* `codebuild_github_repo` - URL of the source GitHub repository for AWS CodeBuild. It should end with '.git'
* `codebuild_github_branch` - Repository branch that should be used by CodeBuild

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

## Obtaining the public key

After the signing key is created in KMS, you can obtain its public key by inspecting
the Terraform Cloud's output entry `kms_key_id`.

For manual steps using CLI see:
https://aws.amazon.com/blogs/security/how-to-verify-aws-kms-asymmetric-key-signatures-locally-with-openssl/

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

## TODO

* Authenticate via asymmetric cryptography - custom private key passed for the HTTPS call. Use API gateway if needed. Ditch the bearer token. Security!
