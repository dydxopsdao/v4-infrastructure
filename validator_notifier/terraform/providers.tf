terraform {
  cloud {
    organization = "dydxopsdao"

    workspaces {
      name = "validator-notifier"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.32.0"
    }
  }

  required_version = "~> 1.5.7"
}

provider "aws" {
  # Expects the following environment variables:
  # - AWS_ACCESS_KEY_ID
  # - AWS_SECRET_ACCESS_KEY
  # - AWS_REGION
}

data "aws_region" "current" {}
