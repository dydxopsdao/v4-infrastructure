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
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "terraform_data" "build_python_package" {
  triggers_replace = {
    always = timestamp()
  }

  provisioner "local-exec" {
    command = <<EOT
      rm -rf ./package
      mkdir -p ./package
      pip install --target ./package cryptography
      cp ./message_signer.py ./package
    EOT
  }
}

data "archive_file" "lambda" {
  depends_on  = [terraform_data.build_python_package]
  type        = "zip"
  source_dir  = "package"
  output_path = "package.zip"
}

resource "aws_lambda_function" "sign_message" {
  filename      = "package.zip"
  function_name = "sign_message"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "message_signer.run"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.11"

  environment {
    variables = {
      RSA_PRIVATE_KEY = var.rsa_private_key
    }
  }
}
