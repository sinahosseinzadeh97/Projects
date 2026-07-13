# === FILE: terraform/variables.tf ===
# Input variables for Sinistri FNOL Agent infrastructure

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "app_name" {
  description = "Application name used for resource naming"
  type        = string
  default     = "pratica-ai"
}

variable "aws_region" {
  description = "AWS region — must be EU for GDPR compliance"
  type        = string
  default     = "eu-south-1"
}

variable "domain_name" {
  description = "Domain name for the application (e.g. sinistri.yourcompany.it)"
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.small"
}

variable "ecs_cpu" {
  description = "ECS task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 512
}

variable "ecs_memory" {
  description = "ECS task memory in MiB"
  type        = number
  default     = 1024
}

variable "min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of ECS tasks for auto-scaling"
  type        = number
  default     = 10
}

variable "google_api_key" {
  description = "Google Gemini API key for the AI agent"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Application secret key for JWT signing"
  type        = string
  sensitive   = true
}
