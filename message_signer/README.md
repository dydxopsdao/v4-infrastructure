# Message Signer

An AWS Lambda function that signs the input message with an asymmetric key.

The input should be a JSON with the following format:

```
{
    "message": "<a message string to be signed>"
}
```

The returned value is a JSON with the following format:

```
{
    "signature_base64": <base64-encoded RSA signature string>
}
```

## Assumptions

* AWS account
* Terraform Cloud
* Terraform CLI installed locally

## Usage

Prepare the RSA key:

```
openssl genrsa -out rsa-private.pem 4096
openssl rsa -in rsa-private.pem -outform PEM -pubout -out rsa-public.pem
```

Prepare an AWS IAM user for deploying the solution, preferably in a dedicated AWS account.
The user should have the permissions to:

* Create IAM roles,
* Create Lambda functions.

Set up the Terraform project:

```
cd ./message_signer
terraform login
terraform init
terraform apply
```

This will create a dedicated workspace in Terraform Cloud but the AWS deployment will fail (no credentials).
In the new Terraform Cloud workspace set up the following variables:

* `AWS_ACCESS_KEY_ID` - user your IAM user ID
* `AWS_SECRET_ACCESS_KEY` - user your IAM user secret key
* `AWS_REGION` - where you want the Lambda function deployed

Then re-run:

```
terraform apply
```

The Lambda function should be deployed.

## Reading

* https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html
* https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function
* https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
* https://rietta.com/blog/openssl-generating-rsa-key-from-command/
