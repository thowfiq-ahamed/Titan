variable "cluster_name" {
  type        = string
  description = "EKS cluster name"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "cluster_version" {
  type        = string
  default     = "1.31"
  description = "Kubernetes control plane and node group version"
}

variable "cluster_role_arn" {
  type        = string
  description = "IAM Role ARN for EKS cluster"
}

variable "node_role_arn" {
  type        = string
  description = "IAM Role ARN for EKS worker nodes"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnets for worker nodes"
}

variable "instance_types" {
  type        = list(string)
  default     = ["t3.medium"]
  description = "EC2 instance types for nodes"
}

# 1. EKS Cluster
resource "aws_eks_cluster" "cluster" {
  name     = "${var.cluster_name}-${var.environment}"
  role_arn = var.cluster_role_arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  tags = {
    Project     = "TITAN"
    Environment = var.environment
  }
}

# 2. Managed Node Group
resource "aws_eks_node_group" "nodes" {
  cluster_name    = aws_eks_cluster.cluster.name
  node_group_name = "titan-managed-nodes-${var.environment}"
  node_role_arn   = var.node_role_arn
  version         = var.cluster_version
  subnet_ids      = var.private_subnet_ids
  instance_types  = var.instance_types

  scaling_config {
    desired_size = 2
    max_size     = 6
    min_size     = 2
  }

  update_config {
    max_unavailable = 1
  }

  tags = {
    Project     = "TITAN"
    Environment = var.environment
  }
}

output "cluster_endpoint" {
  value = aws_eks_cluster.cluster.endpoint
}

output "cluster_name" {
  value = aws_eks_cluster.cluster.name
}

output "cluster_certificate_authority_data" {
  value = aws_eks_cluster.cluster.certificate_authority[0].data
}
