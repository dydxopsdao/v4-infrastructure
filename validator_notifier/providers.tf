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
      version = "= 5.30.0"
    }

    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }

  required_version = "~> 1.5.7"
}


provider "aws" {}

data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}
