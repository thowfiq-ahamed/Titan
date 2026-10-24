variable "environment" {
  type        = string
  description = "Environment name"
}

variable "github_repo" {
  type        = string
  default     = "titan-platform/titan"
  description = "GitHub org/repo for OIDC federation"
}

# 1. EKS Cluster Role
resource "aws_iam_role" "eks_cluster" {
  name = "titan-eks-cluster-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

# 2. EKS Node Group Role
resource "aws_iam_role" "eks_nodes" {
  name = "titan-eks-nodes-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_node" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodes.name
}

# 3. GitHub Actions OIDC Federation Role (Keyless Authentication)
resource "aws_iam_openid_connect_provider" "github" {
  count           = var.environment == "dev" ? 1 : 0
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1", "1c587693c4e5836e315333ce987712369c0d7b41"]
}

resource "aws_iam_role" "github_actions_oidc" {
  name = "titan-github-actions-oidc-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = "arn:aws:iam::*:oidc-provider/token.actions.githubusercontent.com"
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:*"
        }
      }
    }]
  })
}

output "eks_cluster_role_arn" {
  value = aws_iam_role.eks_cluster.arn
}

output "eks_nodes_role_arn" {
  value = aws_iam_role.eks_nodes.arn
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions_oidc.arn
}
