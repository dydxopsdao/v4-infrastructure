# === IAM role ===

data "aws_iam_policy_document" "lambda_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "lambda-runner"
  assume_role_policy = data.aws_iam_policy_document.lambda_role.json
}

# === Permissions ===

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ses:SendRawEmail",
    ]
    resources = ["arn:aws:ses:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_permissions" {
  name        = "lambda-permissions"
  path        = "/"
  description = "Permissions for lambda"
  policy      = data.aws_iam_policy_document.lambda_permissions.json
}

resource "aws_iam_role_policy_attachment" "lambda_permissions" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_permissions.arn
}

# === Lambda function ===

resource "aws_lambda_function" "notify_validators" {
  function_name    = "notify_validators"
  package_type     = "Image"
  image_uri        = "${aws_ecr_repository.validator_notifier.repository_url}:latest"
  role             = aws_iam_role.iam_for_lambda.arn
  timeout          = 90
  source_code_hash = timestamp() # Force update on every apply

  environment {
    variables = {
      RSA_PRIVATE_KEY     = var.rsa_private_key
      EMAIL_AWS_REGION    = data.aws_region.current.name
      SENDER              = "dYdX Ops Services <infrastructure@dydxopsservices.com>"
      RECIPIENTS          = var.recipients
      AUTHORIZATION_TOKEN = var.authorization_token
    }
  }
}

resource "aws_lambda_function_url" "notify_validators_url" {
  function_name      = aws_lambda_function.notify_validators.function_name
  authorization_type = "NONE"
}
