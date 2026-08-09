# EKBA Enterprise Infrastructure — Main Terraform Configuration

terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "ekba-tfstate-prod"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "ekba-tflocks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "EKBA"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 1. VPC Network Module
module "vpc" {
  source             = "./modules/vpc"
  cidr_block         = var.vpc_cidr
  environment        = var.environment
  availability_zones = var.availability_zones
}

# 2. S3 Encrypted Document Storage Module
module "s3" {
  source      = "./modules/s3"
  environment = var.environment
}

# 3. AWS Secrets Manager Module (No Delete Path Enforcement)
module "secrets" {
  source      = "./modules/secrets"
  environment = var.environment
}

# 4. EKS Managed Kubernetes Cluster Module
module "eks" {
  source          = "./modules/eks"
  cluster_name    = "ekba-${var.environment}-eks"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  environment     = var.environment
}
