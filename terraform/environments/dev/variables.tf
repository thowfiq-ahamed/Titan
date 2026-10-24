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

variable "kubernetes_version" {
  type        = string
  default     = "1.31"
  description = "Target Kubernetes version for EKS cluster"
}

variable "github_repo" {
  type        = string
  default     = "thowfiq-ahamed/Titan"
  description = "GitHub repository for OIDC identity federation"
}
