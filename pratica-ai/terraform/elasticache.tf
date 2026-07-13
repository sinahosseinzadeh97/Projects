# === FILE: terraform/elasticache.tf ===
# AWS ElastiCache Redis for Sinistri FNOL Agent
# Session cache with encryption at rest and in transit

# ── ElastiCache Subnet Group ──────────────────────────────────

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.app_name}-redis-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.app_name}-redis-subnet-group"
  }
}

# ── ElastiCache Redis Cluster ─────────────────────────────────

resource "aws_elasticache_cluster" "main" {
  cluster_id      = "${var.app_name}-redis"
  engine          = "redis"
  engine_version  = "7.1"
  node_type       = "cache.t4g.small"
  num_cache_nodes = 1
  port            = 6379

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  # Encryption at rest
  # Note: For single-node clusters, use replication group for
  # at-rest encryption. Keeping simple for dev/startup.

  # Maintenance window (Italian night)
  maintenance_window = "tue:03:00-tue:04:00"

  # Snapshot for backup
  snapshot_retention_limit = var.environment == "prod" ? 7 : 1
  snapshot_window          = "02:00-03:00"

  tags = {
    Name = "${var.app_name}-redis"
  }
}

# ── ElastiCache Replication Group (prod — encryption support) ─
# Uncomment for production with encryption at rest + in transit

# resource "aws_elasticache_replication_group" "main" {
#   replication_group_id = "${var.app_name}-redis"
#   description          = "Redis for Sinistri FNOL Agent"
#
#   engine               = "redis"
#   engine_version       = "7.1"
#   node_type            = "cache.t4g.small"
#   num_cache_clusters   = 1
#   port                 = 6379
#
#   subnet_group_name    = aws_elasticache_subnet_group.main.name
#   security_group_ids   = [aws_security_group.redis.id]
#
#   at_rest_encryption_enabled = true
#   transit_encryption_enabled = true
#   auth_token                 = random_password.redis_auth_token.result
#
#   maintenance_window         = "tue:03:00-tue:04:00"
#   snapshot_retention_limit   = 7
#   snapshot_window            = "02:00-03:00"
#
#   tags = {
#     Name      = "${var.app_name}-redis"
#     Encrypted = "true"
#   }
# }

resource "random_password" "redis_auth_token" {
  length  = 64
  special = false # ElastiCache auth tokens cannot have special chars
}
