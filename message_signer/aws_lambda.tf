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

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "sign_message.py"
  output_path = "sign_message.zip"
}

resource "aws_lambda_function" "sign_message" {
  filename      = "sign_message.zip"
  function_name = "sign_message"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "sign_message.run"

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.11"
}
