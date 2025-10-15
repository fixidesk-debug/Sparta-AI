// Terraform skeleton for Sparta AI infrastructure (AWS example)
// Fill provider credentials using environment variables or a workspace secret manager

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

// VPC, subnets, security groups would be defined here or imported from modules
// Example: create ECR repository for images
resource "aws_ecr_repository" "backend" {
  name                 = "sparta-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "frontend" {
  name                 = "sparta-frontend"
  image_tag_mutability = "MUTABLE"
}

// RDS Postgres, ElastiCache Redis, EKS cluster modules should be added here
// Use official modules for production-grade resources

output "ecr_backend_uri" {
  value = aws_ecr_repository.backend.repository_url
}
