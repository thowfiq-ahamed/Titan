variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target AWS region"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.10.0.0/16"
  description = "VPC CIDR block for dev environment"
}

variable "availability_zones" {
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
  description = "Availability zones to utilize"
}

variable "github_repo" {
  type        = string
  default     = "titan-platform/titan"
  description = "GitHub repository for OIDC identity federation"
}
