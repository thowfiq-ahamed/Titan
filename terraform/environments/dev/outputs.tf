output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "ID of created VPC"
}

output "eks_cluster_name" {
  value       = module.eks.cluster_name
  description = "Name of provisioned EKS cluster"
}

output "eks_cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "EKS control plane API endpoint"
}

output "ecr_repository_url" {
  value       = module.ecr.repository_url
  description = "ECR image repository endpoint"
}

output "rds_endpoint" {
  value       = module.rds.db_endpoint
  description = "PostgreSQL database connection endpoint"
}

output "github_actions_role_arn" {
  value       = module.iam.github_actions_role_arn
  description = "IAM role ARN assumed by GitHub Actions via OIDC"
}
