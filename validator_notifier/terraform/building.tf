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

resource "aws_iam_role" "builder" {
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
  role       = aws_iam_role.builder.name
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

resource "aws_codebuild_project" "this" {
  name          = "validator-notifier"
  description   = "Managed by Terraform"
  service_role  = aws_iam_role.builder.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  source {
    type            = "GITHUB"
    location        = var.codebuild_github_repo
    git_clone_depth = 1
    buildspec       = <<EOF
      version: 0.2
      phases:
        pre_build:
          commands:
            - echo Logging in to Amazon ECR...
            - aws ecr get-login-password --region ${data.aws_region.current.name} | docker login --username AWS --password-stdin ${aws_ecr_repository.validator_notifier.repository_url}
            - REPOSITORY_URI=${aws_ecr_repository.validator_notifier.repository_url}
        build:
          commands:
            - echo Build started on `date`
            - echo Building the Docker image...  
            - docker build -t $REPOSITORY_URI:latest .
            - docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG
        image_publish:
          commands:
            - echo Build completed on `date`
            - echo Pushing the Docker image...
            - docker push $REPOSITORY_URI:latest
            - docker push $REPOSITORY_URI:$IMAGE_TAG
        deploy:
          commands:
            - echo Deploying the Docker image to ECR...
            - aws lambda update-function-code --region ${data.aws_region.current.name} --function-name notify_validators --image-uri $REPOSITORY_URI:latest --publish
      EOF
  }

  environment {
    compute_type                = "BUILD_LAMBDA_1GB"
    type                        = "LINUX_LAMBDA_CONTAINER"
    image                       = "aws/codebuild/amazonlinux-x86_64-lambda-standard:python3.12"
    image_pull_credentials_type = "CODEBUILD"

    # dynamic "environment_variable" {
    #   for_each = var.environment_variables
    #   content {
    #     name  = environment_variable.key
    #     value = environment_variable.value
    #   }
    # }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "log-group"
      stream_name = "log-stream"
    }

    s3_logs {
      status = "DISABLED"
    }
  }
}
