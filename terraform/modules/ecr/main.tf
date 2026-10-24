variable "repository_name" {
  type        = string
  default     = "titan-inventory-api"
  description = "ECR repository name"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

resource "aws_ecr_repository" "repo" {
  name                 = "${var.repository_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Project     = "TITAN"
    Environment = var.environment
  }
}

resource "aws_ecr_lifecycle_policy" "cleanup" {
  repository = aws_ecr_repository.repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images older than 14 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 14
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Retain last 30 tagged images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = { type = "expire" }
      }
    ]
  })
}

output "repository_url" {
  value = aws_ecr_repository.repo.repository_url
}

output "repository_arn" {
  value = aws_ecr_repository.repo.arn
}
