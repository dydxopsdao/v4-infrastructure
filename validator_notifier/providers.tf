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

provider "docker" {}
