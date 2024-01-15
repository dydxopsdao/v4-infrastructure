# === Basic IAM permissions ===

data "aws_iam_policy_document" "assume_role" {
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
  name               = "lambda-assume-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# === Logging permissions ===

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda-logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

# === Email sending permissions ===

data "aws_iam_policy_document" "lambda_email" {
  statement {
    effect = "Allow"

    actions = [
      "ses:SendRawEmail",
    ]

    resources = ["arn:aws:ses:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_email" {
  name        = "lambda-email"
  path        = "/"
  description = "IAM policy for email sending from a lambda"
  policy      = data.aws_iam_policy_document.lambda_email.json
}

resource "aws_iam_role_policy_attachment" "lambda_email" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_email.arn
}

# === Image creation ===

resource "aws_ecr_repository" "validator_notifier" {
  name = "validator-notifier"
  image_scanning_configuration {
    scan_on_push = true
  }
  image_tag_mutability = "MUTABLE"
}

resource "docker_image" "default" {
  name = aws_ecr_repository.validator_notifier.name
  build {
    context = "."
    tag     = ["${aws_ecr_repository.validator_notifier.name}:latest"]
  }
  platform = "linux/amd64"
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "src/*") : filesha1(f)]))
  }
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
      EMAIL_AWS_REGION    = "ap-northeast-1"
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
