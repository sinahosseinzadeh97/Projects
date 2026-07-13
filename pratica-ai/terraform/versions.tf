# === FILE: terraform/versions.tf ===
# Terraform configuration for Sinistri FNOL Agent
# Region: eu-south-1 (Milano, Italy) — GDPR compliant

terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket  = "sinistri-terraform-state"
    key     = "pratica-ai/terraform.tfstate"
    region  = "eu-south-1"
    encrypt = true
  }
}

provider "aws" {
  region = "eu-south-1" # Milan — GDPR compliant, all data stays in EU

  default_tags {
    tags = {
      Project     = "pratica-ai"
      Environment = var.environment
      ManagedBy   = "terraform"
      DataRegion  = "EU-South-1-Milan"
      GDPRScope   = "true"
    }
  }
}
