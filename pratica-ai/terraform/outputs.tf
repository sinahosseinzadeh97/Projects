# === FILE: terraform/outputs.tf ===
# Outputs for Sinistri FNOL Agent infrastructure

output "alb_dns_name" {
  description = "ALB DNS name — use for CNAME or Route53 alias"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for pushing Docker images"
  value       = aws_ecr_repository.main.repository_url
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name for deployments"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name for deployments"
  value       = aws_ecs_service.main.name
}

output "app_url" {
  description = "Application URL (HTTPS)"
  value       = "https://${var.domain_name}"
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs (for additional resources)"
  value       = aws_subnet.private[*].id
}

output "sns_alerts_topic_arn" {
  description = "SNS topic ARN for alert subscriptions"
  value       = aws_sns_topic.alerts.arn
}
