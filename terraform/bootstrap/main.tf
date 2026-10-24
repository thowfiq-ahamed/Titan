# ==============================================================================
# TITAN Terraform State Bootstrap (S3 + DynamoDB Locking)
# Creates remote state backend without circular dependency
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for state backend"
}

variable "environment" {
  type        = string
  default     = "bootstrap"
  description = "Environment identifier"
}

provider "aws" {
  region = var.aws_region
}

# 1. State Bucket
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "titan-terraform-state-${var.aws_region}"
  force_destroy = false

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Project     = "TITAN"
    ManagedBy   = "Terraform"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state_encryption" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "state_public_block" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 2. DynamoDB State Locking Table
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "titan-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Project     = "TITAN"
    ManagedBy   = "Terraform"
    Environment = var.environment
  }
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.terraform_state.id
  description = "Name of S3 bucket hosting remote state"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.terraform_locks.id
  description = "Name of DynamoDB table for state locking"
}
