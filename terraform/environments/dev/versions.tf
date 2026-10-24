terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Remote state backend configuration template:
  # Run `terraform init -backend-config="bucket=..."`
  # backend "s3" {
  #   bucket         = "titan-terraform-state-us-east-1"
  #   key            = "environments/dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "titan-terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "TITAN"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}
