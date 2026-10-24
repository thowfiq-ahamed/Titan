variable "environment" {
  type        = string
  description = "Environment name"
}

variable "private_db_subnet_ids" {
  type        = list(string)
  description = "Private subnets for RDS"
}

variable "rds_security_group_id" {
  type        = string
  description = "Security group for RDS"
}

variable "instance_class" {
  type        = string
  default     = "db.t4g.micro"
  description = "RDS instance class"
}

# 1. DB Subnet Group
resource "aws_db_subnet_group" "rds" {
  name       = "titan-db-subnet-group-${var.environment}"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Project     = "TITAN"
    Environment = var.environment
  }
}

# 2. Random Secure Password
resource "random_password" "master_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# 3. AWS Secrets Manager Secret
resource "aws_secretsmanager_secret" "db_secret" {
  name                    = "titan/rds/${var.environment}/credentials"
  recovery_window_in_days = 0

  tags = {
    Project     = "TITAN"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_secret_val" {
  secret_id = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    engine   = "postgres"
    host     = aws_db_instance.postgres.address
    port     = 5432
    username = "titan_admin"
    password = random_password.master_password.result
    database = "titan_inventory"
  })
}

# 4. PostgreSQL RDS Instance
resource "aws_db_instance" "postgres" {
  identifier            = "titan-postgres-${var.environment}"
  allocated_storage     = 20
  max_allocated_storage = 100
  engine                = "postgres"
  engine_version        = "16.3"
  instance_class        = var.instance_class

  db_name  = "titan_inventory"
  username = "titan_admin"
  password = random_password.master_password.result

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [var.rds_security_group_id]

  multi_az            = var.environment == "staging" || var.environment == "prod"
  storage_encrypted   = true
  publicly_accessible = false
  skip_final_snapshot = var.environment == "dev"

  tags = {
    Project     = "TITAN"
    Environment = var.environment
  }
}

output "db_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "db_address" {
  value = aws_db_instance.postgres.address
}

output "secret_arn" {
  value = aws_secretsmanager_secret.db_secret.arn
}
