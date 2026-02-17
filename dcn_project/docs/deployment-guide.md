# Data Collection Node (DCN) - Deployment Guide

## 📋 Prerequisites

### Required Software
- **Kubernetes Cluster**: v1.28 or higher
- **kubectl**: Configured and connected to your cluster
- **Helm**: v3.x (optional, for enhanced deployments)
- **Docker**: For building custom images
- **Git**: For cloning the repository

### Cluster Requirements
- **Minimum Nodes**: 3 worker nodes
- **CPU**: 8 cores per node (24 cores total)
- **Memory**: 16 GB per node (48 GB total)
- **Storage**: 1 TB persistent storage available

### Network Requirements
- **Ingress Controller**: NGINX Ingress Controller installed
- **Load Balancer**: Available for external access
- **DNS**: For ingress hostname resolution
- **Ports**: 80/443 (HTTP/HTTPS), 5432 (PostgreSQL), 9092 (Kafka)

---

## 🚀 Quick Start Deployment

### 1. Clone Repository
```bash
git clone https://github.com/yourorg/dcn-project.git
cd dcn-project
```

### 2. Configure Environment
```bash
# Edit secrets (IMPORTANT: Change passwords!)
nano kubernetes/secrets/dcn-secrets.yaml

# Edit ConfigMaps for your environment
nano kubernetes/configmaps/collector-config.yaml
nano kubernetes/configmaps/api-config.yaml
```

### 3. Deploy DCN
```bash
cd scripts
chmod +x deploy.sh
./deploy.sh production latest
```

### 4. Verify Deployment
```bash
kubectl get pods -n dcn
kubectl get svc -n dcn
kubectl get ingress -n dcn
```

---

## 📦 Component-by-Component Deployment

If you prefer manual control or troubleshooting, deploy components individually:

### Step 1: Create Namespace
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl get namespace dcn
```

### Step 2: Deploy RBAC
```bash
kubectl apply -f kubernetes/rbac/rbac.yaml
kubectl get serviceaccount -n dcn
kubectl get role -n dcn
kubectl get rolebinding -n dcn
```

### Step 3: Deploy Secrets
```bash
# IMPORTANT: Update passwords before deploying!
kubectl apply -f kubernetes/secrets/dcn-secrets.yaml
kubectl get secrets -n dcn
```

### Step 4: Deploy ConfigMaps
```bash
kubectl apply -f kubernetes/configmaps/collector-config.yaml
kubectl apply -f kubernetes/configmaps/api-config.yaml
kubectl get configmaps -n dcn
```

### Step 5: Deploy Infrastructure

#### Kafka
```bash
kubectl apply -f kubernetes/statefulsets/kafka-statefulset.yaml

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app=kafka -n dcn --timeout=300s

# Verify
kubectl get statefulset kafka -n dcn
kubectl get pods -l app=kafka -n dcn
```

#### TimescaleDB
```bash
kubectl apply -f kubernetes/statefulsets/timescaledb-statefulset.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=timescaledb -n dcn --timeout=300s

# Verify
kubectl exec -it timescaledb-0 -n dcn -- psql -U dcn -c "\l"
```

### Step 6: Initialize Database Schema
```bash
# Port forward to TimescaleDB
kubectl port-forward -n dcn svc/timescaledb 5432:5432 &

# Run initialization script
psql -h localhost -U dcn -d dcn -f database/init.sql

# Create hypertables for time-series data
psql -h localhost -U dcn -d dcn <<EOF
CREATE TABLE IF NOT EXISTS metrics (
    timestamp TIMESTAMPTZ NOT NULL,
    name TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    labels JSONB,
    collector TEXT
);

SELECT create_hypertable('metrics', 'timestamp', if_not_exists => TRUE);

CREATE INDEX ON metrics (name, timestamp DESC);
CREATE INDEX ON metrics USING GIN (labels);

CREATE TABLE IF NOT EXISTS metric_metadata (
    name TEXT PRIMARY KEY,
    description TEXT,
    labels TEXT[],
    type TEXT,
    unit TEXT
);

CREATE TABLE IF NOT EXISTS data_sources (
    name TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    last_collection TIMESTAMPTZ,
    metrics_count INTEGER
);
EOF
```

### Step 7: Deploy Application Services

#### Collector Service
```bash
kubectl apply -f kubernetes/deployments/collector-deployment.yaml
kubectl apply -f kubernetes/services/collector-service.yaml

# Monitor rollout
kubectl rollout status deployment/dcn-collector -n dcn

# Check logs
kubectl logs -f -l app=dcn-collector -n dcn
```

#### API Service
```bash
kubectl apply -f kubernetes/deployments/api-deployment.yaml
kubectl apply -f kubernetes/services/api-service.yaml

# Monitor rollout
kubectl rollout status deployment/dcn-api -n dcn

# Check logs
kubectl logs -f -l app=dcn-api -n dcn
```

### Step 8: Deploy Ingress
```bash
kubectl apply -f kubernetes/ingress/dcn-ingress.yaml

# Get ingress details
kubectl get ingress dcn-ingress -n dcn
kubectl describe ingress dcn-ingress -n dcn
```

### Step 9: Deploy Auto-Scaling
```bash
kubectl apply -f kubernetes/hpa/dcn-hpa.yaml

# Verify HPA
kubectl get hpa -n dcn
kubectl describe hpa dcn-api-hpa -n dcn
```

### Step 10: Deploy Monitoring
```bash
# Deploy ServiceMonitors for Prometheus
kubectl apply -f kubernetes/monitoring/servicemonitor.yaml

# Deploy alert rules
kubectl apply -f kubernetes/monitoring/prometheusrule.yaml

# Verify
kubectl get servicemonitor -n dcn
kubectl get prometheusrule -n dcn
```

---

## 🔍 Verification Steps

### 1. Check All Pods Are Running
```bash
kubectl get pods -n dcn

# Expected output:
# NAME                            READY   STATUS    RESTARTS   AGE
# dcn-api-xxxxx-xxxxx            1/1     Running   0          5m
# dcn-collector-xxxxx-xxxxx      1/1     Running   0          5m
# kafka-0                         1/1     Running   0          10m
# kafka-1                         1/1     Running   0          10m
# kafka-2                         1/1     Running   0          10m
# timescaledb-0                   1/1     Running   0          10m
```

### 2. Test API Health
```bash
# Port forward
kubectl port-forward -n dcn svc/dcn-api 8080:80

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl http://localhost:8080/api/v1/counters
```

### 3. Check Metrics Collection
```bash
# View collector logs
kubectl logs -n dcn -l app=dcn-collector --tail=100

# Should see logs like:
# INFO - Collecting ONTAP metrics from 2 clusters
# INFO - Collected 150 ONTAP metrics
# INFO - Sent 150 metrics to topic dcn-metrics
```

### 4. Verify Kafka Topics
```bash
# Exec into Kafka pod
kubectl exec -it kafka-0 -n dcn -- bash

# List topics
kafka-topics --bootstrap-server localhost:9092 --list

# Check dcn-metrics topic
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic dcn-metrics --from-beginning --max-messages 10
```

### 5. Query Database
```bash
# Connect to database
kubectl exec -it timescaledb-0 -n dcn -- psql -U dcn

# Check metrics table
SELECT COUNT(*) FROM metrics;
SELECT DISTINCT name FROM metrics LIMIT 10;
SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5;
```

---

## 🔧 Configuration

### Update Collector Configuration
```bash
# Edit ConfigMap
kubectl edit configmap collector-config -n dcn

# Restart collectors to pick up changes
kubectl rollout restart deployment/dcn-collector -n dcn
```

### Update API Configuration
```bash
# Edit ConfigMap
kubectl edit configmap api-config -n dcn

# Restart API servers
kubectl rollout restart deployment/dcn-api -n dcn
```

### Update Secrets
```bash
# WARNING: This will restart all pods using the secrets
kubectl delete secret dcn-secrets -n dcn
kubectl apply -f kubernetes/secrets/dcn-secrets.yaml

# Restart affected deployments
kubectl rollout restart deployment/dcn-collector -n dcn
kubectl rollout restart deployment/dcn-api -n dcn
```

---

## 📊 Accessing Services

### API Service
```bash
# Via LoadBalancer (if available)
API_IP=$(kubectl get svc dcn-api -n dcn -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "API URL: http://$API_IP"

# Via Ingress
INGRESS_HOST=$(kubectl get ingress dcn-ingress -n dcn -o jsonpath='{.spec.rules[0].host}')
echo "API URL: https://$INGRESS_HOST"

# Via Port Forward (for testing)
kubectl port-forward -n dcn svc/dcn-api 8080:80
echo "API URL: http://localhost:8080"
```

### API Documentation
```bash
# Access Swagger UI
open http://$API_IP/docs

# Or via port-forward
kubectl port-forward -n dcn svc/dcn-api 8080:80
open http://localhost:8080/docs
```

### Metrics Endpoints
```bash
# Collector metrics
kubectl port-forward -n dcn svc/dcn-collector 9090:9090
curl http://localhost:9090/metrics

# API metrics
curl http://$API_IP/metrics
```

---

## 🔍 Troubleshooting

### Pods Not Starting

**Check pod status:**
```bash
kubectl get pods -n dcn
kubectl describe pod <pod-name> -n dcn
kubectl logs <pod-name> -n dcn
```

**Common issues:**
- Insufficient resources: Check node resources
- Image pull errors: Verify image registry access
- Configuration errors: Check ConfigMaps and Secrets

### Database Connection Issues

**Test connectivity:**
```bash
# Port forward to database
kubectl port-forward -n dcn svc/timescaledb 5432:5432

# Test connection
psql -h localhost -U dcn -d dcn -c "SELECT 1"
```

**Check credentials:**
```bash
kubectl get secret dcn-secrets -n dcn -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 --decode
```

### Kafka Issues

**Check Kafka brokers:**
```bash
kubectl exec -it kafka-0 -n dcn -- kafka-broker-api-versions --bootstrap-server localhost:9092
```

**Check topic lag:**
```bash
kubectl exec -it kafka-0 -n dcn -- kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group dcn-processors
```

### Service Not Accessible

**Check services:**
```bash
kubectl get svc -n dcn
kubectl describe svc dcn-api -n dcn
```

**Check ingress:**
```bash
kubectl get ingress -n dcn
kubectl describe ingress dcn-ingress -n dcn
```

**Test from within cluster:**
```bash
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n dcn -- \
  curl http://dcn-api.dcn.svc.cluster.local/health
```

---

## 🔄 Upgrading

### Upgrade Application Version
```bash
# Update image in deployment
kubectl set image deployment/dcn-api dcn-api=yourorg/dcn-api:v2.0.0 -n dcn
kubectl set image deployment/dcn-collector collector=yourorg/dcn-collector:v2.0.0 -n dcn

# Monitor rollout
kubectl rollout status deployment/dcn-api -n dcn
kubectl rollout status deployment/dcn-collector -n dcn
```

### Rollback if Needed
```bash
# Rollback to previous version
kubectl rollout undo deployment/dcn-api -n dcn
kubectl rollout undo deployment/dcn-collector -n dcn
```

---

## 🧹 Cleanup

### Delete All DCN Resources
```bash
# Delete namespace (this removes everything)
kubectl delete namespace dcn

# Or delete individual components
kubectl delete -f kubernetes/deployments/
kubectl delete -f kubernetes/services/
kubectl delete -f kubernetes/ingress/
kubectl delete -f kubernetes/statefulsets/
kubectl delete -f kubernetes/configmaps/
kubectl delete -f kubernetes/secrets/
kubectl delete -f kubernetes/rbac/
```

### Delete Persistent Data
```bash
# List PVCs
kubectl get pvc -n dcn

# Delete specific PVCs
kubectl delete pvc kafka-data-kafka-0 -n dcn
kubectl delete pvc timescaledb-data-timescaledb-0 -n dcn
```

---

## 📞 Support

For deployment issues, contact:
- **Email**: dcn-support@netapp.com
- **Slack**: #dcn-support
- **Documentation**: `/docs` directory

---

**Deployment Guide Version**: 1.0.0  
**Last Updated**: February 2026
