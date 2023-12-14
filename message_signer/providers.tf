terraform {
  cloud {
    organization = "dydxopsdao"

    workspaces {
      name = "message-signer"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.30.0"
    }
  }

  required_version = "~> 1.5.7"
}

provider "aws" {}
