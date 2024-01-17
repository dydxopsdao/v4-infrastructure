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

locals {
  lambda_function_name = "notify_validators"
}





# DOES THIS HAPPEN ON PLAN OR ON APPLY?!?!

data "external" "build_image_with_codebuild" {
  # TODO: Trigger a build and wait until it's finished. Something along the lines of:
  # BUILD_ID=$(aws codebuild start-build --region=$REGION --project-name=validator-notifier | jq '.build.id')
  # While not BUILD_PHASE == "COMPLETED":
  # BUILD_PHASE=$(aws codebuild batch-get-builds --region=$REGION --ids=$BUILD_ID | jq '.builds[0].currentPhase')
  program = ["bash", "${path.module}/build-image-with-codebuild.sh"]

  query = {
    region = data.aws_region.current.name
  }

  depends_on = [aws_codebuild_project.validator_notifier]
}

resource "aws_lambda_function" "notify_validators" {
  function_name    = local.lambda_function_name
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

  depends_on = [data.external.build_image_with_codebuild]
}

resource "aws_lambda_function_url" "notify_validators_url" {
  function_name      = aws_lambda_function.notify_validators.function_name
  authorization_type = "NONE"
}
