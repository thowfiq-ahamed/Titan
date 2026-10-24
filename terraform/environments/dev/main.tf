# ==============================================================================
# TITAN Platform - Development AWS Environment
# ==============================================================================

module "vpc" {
  source             = "../../modules/vpc"
  environment        = "dev"
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

module "security_groups" {
  source      = "../../modules/security_groups"
  environment = "dev"
  vpc_id      = module.vpc.vpc_id
}

module "iam" {
  source      = "../../modules/iam"
  environment = "dev"
  github_repo = var.github_repo
}

module "ecr" {
  source          = "../../modules/ecr"
  environment     = "dev"
  repository_name = "titan-inventory-api"
}

module "eks" {
  source             = "../../modules/eks"
  environment        = "dev"
  cluster_name       = "titan-eks"
  cluster_role_arn   = module.iam.eks_cluster_role_arn
  node_role_arn      = module.iam.eks_nodes_role_arn
  private_subnet_ids = module.vpc.private_app_subnet_ids
  instance_types     = ["t3.medium"]
}

module "rds" {
  source                = "../../modules/rds"
  environment           = "dev"
  private_db_subnet_ids = module.vpc.private_db_subnet_ids
  rds_security_group_id = module.security_groups.rds_sg_id
  instance_class        = "db.t4g.micro"
}
