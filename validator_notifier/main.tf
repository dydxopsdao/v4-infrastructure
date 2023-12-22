resource "aws_ecr_repository" "validator_notifier" {
  name = "validator-notifier"
  image_scanning_configuration {
    scan_on_push = true
  }
  image_tag_mutability = "MUTABLE"
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }

  statement {
    effect = "Allow"
    actions = ["ses:SendEmail"]
    resources = ["arn:aws:*:*:*:*"]
  }

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

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# resource "terraform_data" "build_python_package" {
#   triggers_replace = {
#     always = timestamp()
#   }

#   provisioner "local-exec" {
#     command = <<EOT
#       rm -rf ./package
#       mkdir -p ./package
#       pip install --upgrade pip
#       pip install --target ./package -r requirements.txt
#       cp ./message_signer.py ./package
#     EOT
#   }
# }

# resource "docker_image" "message_signer" {
#   name = "message-signer"
#   build {
#     context = "."
#     tag     = ["message-signer:lastest"]
#     # build_arg = {
#     #   foo : "zoo"
#     # }
#     # label = {
#     #   author : "zoo"
#     # }
#   }
# }

# data "archive_file" "lambda" {
#   depends_on  = [terraform_data.build_python_package]
#   type        = "zip"
#   source_dir  = "package"
#   output_path = "package.zip"
# }

resource "aws_lambda_function" "notify_validators" {
  function_name    = "notify_validators"
  package_type     = "Image"
  image_uri        = "${aws_ecr_repository.validator_notifier.repository_url}:latest"
  role             = aws_iam_role.iam_for_lambda.arn
  timeout          = 90
  source_code_hash = timestamp()

  environment {
    variables = {
      RSA_PRIVATE_KEY  = var.rsa_private_key
      EMAIL_AWS_REGION = "ap-northeast-1"
      SENDER           = "dYdX Ops Services <infrastructure@dydxopsservices.com>"
      RECIPIENTS       = var.recipients
    }
  }
}
