variable "vpc_id" {
  type        = string
  description = "Target VPC ID"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

# 1. EKS Node Security Group
resource "aws_security_group" "eks_nodes" {
  name        = "titan-eks-nodes-sg-${var.environment}"
  description = "Security group for EKS worker nodes"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "titan-eks-nodes-sg-${var.environment}"
    Project     = "TITAN"
    Environment = var.environment
  }
}

# 2. RDS Security Group (Least Privilege: ONLY from EKS Nodes)
resource "aws_security_group" "rds" {
  name        = "titan-rds-sg-${var.environment}"
  description = "Allows inbound PostgreSQL traffic solely from EKS worker nodes"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from EKS nodes"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "titan-rds-sg-${var.environment}"
    Project     = "TITAN"
    Environment = var.environment
  }
}

output "eks_nodes_sg_id" {
  value = aws_security_group.eks_nodes.id
}

output "rds_sg_id" {
  value = aws_security_group.rds.id
}
