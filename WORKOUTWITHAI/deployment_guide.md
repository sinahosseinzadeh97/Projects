# Fitness App Backend Deployment Guide

This guide provides instructions for deploying the Fitness App Backend using Docker and Kubernetes.

## Prerequisites

- Docker and Docker Compose installed
- Kubernetes cluster set up (or minikube for local testing)
- kubectl configured to connect to your cluster
- GitHub account for CI/CD pipeline

## Local Deployment with Docker Compose

For development and testing purposes, you can deploy the application locally using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fitness-app.git
   cd fitness-app
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Verify all services are running:
   ```bash
   docker-compose ps
   ```

4. Access the API at http://localhost:8000
   - API documentation is available at http://localhost:8000/docs
   - Monitoring dashboard is available at http://localhost:3000

5. To stop the services:
   ```bash
   docker-compose down
   ```

## Production Deployment with Kubernetes

For production deployment, follow these steps:

1. Set up secrets in your Kubernetes cluster:
   ```bash
   # Create a namespace for the application
   kubectl create namespace fitness-app
   
   # Create secrets
   kubectl create secret generic fitness-secrets \
     --namespace=fitness-app \
     --from-literal=database-url=postgresql://fitness_user:fitness_password@postgres:5432/fitness_db \
     --from-literal=celery-broker-url=redis://redis:6379/0 \
     --from-literal=celery-result-backend=redis://redis:6379/0 \
     --from-literal=postgres-password=fitness_password \
     --from-literal=grafana-admin-password=admin
   ```

2. Deploy the application components:
   ```bash
   # Deploy database and message broker
   kubectl apply -f deployment/kubernetes-services.yml --namespace=fitness-app
   
   # Wait for database to be ready
   kubectl rollout status deployment/postgres --namespace=fitness-app
   
   # Deploy API and worker services
   kubectl apply -f deployment/kubernetes.yml --namespace=fitness-app
   
   # Deploy monitoring
   kubectl apply -f monitoring/kubernetes-monitoring.yml --namespace=fitness-app
   ```

3. Verify all deployments are running:
   ```bash
   kubectl get pods --namespace=fitness-app
   ```

4. Access the services:
   ```bash
   # Get the API service URL
   kubectl get service fitness-api --namespace=fitness-app
   
   # Get the Grafana dashboard URL
   kubectl get service grafana --namespace=fitness-app
   ```

## CI/CD Pipeline Setup

The application includes a GitHub Actions workflow for continuous integration and deployment:

1. Fork the repository to your GitHub account

2. Set up the following secrets in your GitHub repository:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token
   - `KUBE_CONFIG`: Base64-encoded Kubernetes configuration file

3. Push changes to the main branch to trigger the CI/CD pipeline:
   - Tests will run automatically
   - Docker images will be built and pushed to Docker Hub
   - Kubernetes deployments will be updated with the new images

## Scaling the Application

To scale the application components:

```bash
# Scale API servers
kubectl scale deployment fitness-api --replicas=4 --namespace=fitness-app

# Scale worker processes
kubectl scale deployment fitness-worker --replicas=4 --namespace=fitness-app
```

## Monitoring and Troubleshooting

- Access Prometheus at http://[prometheus-service-url]:9090
- Access Grafana at http://[grafana-service-url]:3000
  - Default credentials: admin/admin (change after first login)
  - Dashboards are pre-configured for API and worker metrics

- View logs:
  ```bash
  # API logs
  kubectl logs -l app=fitness-api --namespace=fitness-app
  
  # Worker logs
  kubectl logs -l app=fitness-worker --namespace=fitness-app
  ```

- Check service health:
  ```bash
  # API health endpoint
  curl http://[api-service-url]/health
  ```

## Backup and Restore

To backup the PostgreSQL database:

```bash
# Get the postgres pod name
POSTGRES_POD=$(kubectl get pod -l app=postgres --namespace=fitness-app -o jsonpath="{.items[0].metadata.name}")

# Create a backup
kubectl exec $POSTGRES_POD --namespace=fitness-app -- pg_dump -U fitness_user fitness_db > backup.sql
```

To restore from backup:

```bash
# Copy the backup file to the pod
kubectl cp backup.sql $POSTGRES_POD:/tmp/backup.sql --namespace=fitness-app

# Restore the database
kubectl exec $POSTGRES_POD --namespace=fitness-app -- psql -U fitness_user -d fitness_db -f /tmp/backup.sql
```
