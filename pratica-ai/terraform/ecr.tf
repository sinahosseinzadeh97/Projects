# === FILE: terraform/ecr.tf ===
# ECR Repository for Sinistri FNOL Agent Docker images
# NOTE: The ECR repository is defined in ecs.tf alongside the cluster
# This file exists as a reference for the lifecycle policy details.
#
# Key settings (from ecs.tf):
#   - image_tag_mutability: IMMUTABLE (security best practice)
#   - scan_on_push: true (vulnerability scanning)
#   - Lifecycle: keep last 10 tagged, delete untagged after 1 day
#
# The ECR repository is intentionally co-located with ECS resources
# to avoid circular dependencies between the repository URL and
# the task definition image reference.
