# === IAM role ===

data "aws_iam_policy_document" "builder_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "image_builder" {
  name               = "image-builder"
  assume_role_policy = data.aws_iam_policy_document.builder_assume_role.json
}

# === Permissions ===

data "aws_iam_policy_document" "builder_permissions" {
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

resource "aws_iam_policy" "builder_permissions" {
  name        = "builder-permissions"
  path        = "/"
  description = "Permissions for image builder"
  policy      = data.aws_iam_policy_document.builder_permissions.json
}

resource "aws_iam_role_policy_attachment" "builder_permissions" {
  role       = aws_iam_role.image_builder.name
  policy_arn = aws_iam_policy.builder_permissions.arn
}

# === Image creation ===

resource "aws_ecr_repository" "validator_notifier" {
  name = "validator-notifier"
  image_scanning_configuration {
    scan_on_push = true
  }
  image_tag_mutability = "MUTABLE"
}
