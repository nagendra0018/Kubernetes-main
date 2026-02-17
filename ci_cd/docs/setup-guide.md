# CI/CD Project Setup Guide

This guide provides comprehensive instructions for setting up and deploying the CI/CD pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Jenkins Configuration](#jenkins-configuration)
4. [Kubernetes Setup](#kubernetes-setup)
5. [Ansible Configuration](#ansible-configuration)
6. [Monitoring Setup](#monitoring-setup)
7. [Running the Pipeline](#running-the-pipeline)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Docker**: Version 20.10+
- **Kubernetes**: Version 1.28+ (kubectl configured)
- **Jenkins**: Version 2.400+
- **Ansible**: Version 2.15+
- **Python**: Version 3.11+
- **Git**: Version 2.40+

### Required Access

- Docker registry credentials
- Kubernetes cluster access (admin)
- Jenkins admin credentials
- SonarQube server access
- Slack webhook (for notifications)

### Infrastructure Requirements

- **Development**: 1 node (2 CPU, 4GB RAM)
- **Test**: 2 nodes (4 CPU, 8GB RAM)
- **Production**: 3+ nodes (8 CPU, 16GB RAM)

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourorg/cicd-demo.git
cd cicd-demo/ci_cd
```

### 2. Configure Environment Variables

Create `.env` file in project root:

```bash
# Docker Registry
DOCKER_REGISTRY=docker.io/yourorg
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-password

# Kubernetes
KUBE_CONFIG_PATH=/path/to/kubeconfig
KUBE_CONTEXT=your-cluster-context

# SonarQube
SONAR_HOST_URL=https://sonarqube.example.com
SONAR_TOKEN=your-sonar-token

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Application
APP_NAME=cicd-demo
APP_VERSION=1.0.0
```

### 3. Install Python Dependencies

```bash
cd application
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Check Docker
docker version

# Check Kubernetes
kubectl cluster-info
kubectl get nodes

# Check Ansible
ansible --version

# Check Python
python --version
pytest --version
```

---

## Jenkins Configuration

### 1. Install Jenkins

```bash
# Using Docker
docker run -d \
  --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

### 2. Install Required Plugins

Navigate to **Manage Jenkins → Manage Plugins** and install:

- Docker Pipeline
- Kubernetes
- Ansible
- SonarQube Scanner
- Slack Notification
- Blue Ocean (optional)

### 3. Configure Jenkins Credentials

Navigate to **Manage Jenkins → Manage Credentials** and add:

**Docker Registry:**

- ID: `docker-credentials`
- Type: Username with password
- Username: Your Docker username
- Password: Your Docker password

**Kubernetes:**

- ID: `k8s-credentials`
- Type: Secret file
- File: Upload your kubeconfig

**SonarQube:**

- ID: `sonar-token`
- Type: Secret text
- Secret: Your SonarQube token

**Slack:**

- ID: `slack-webhook`
- Type: Secret text
- Secret: Your Slack webhook URL

### 4. Configure Global Tools

Navigate to **Manage Jenkins → Global Tool Configuration**:

**Docker:**

- Name: `docker`
- Install automatically: Yes

**SonarQube Scanner:**

- Name: `sonar-scanner`
- Install automatically: Yes

**Ansible:**

- Name: `ansible`
- Path: `/usr/bin/ansible-playbook`

### 5. Create Pipeline Job

1. Click **New Item**
2. Enter name: `cicd-demo-pipeline`
3. Select **Pipeline**
4. Configure:
   - **Pipeline Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: Your repository URL
   - **Script Path**: `ci_cd/jenkins/Jenkinsfile`
5. Save

---

## Kubernetes Setup

### 1. Create Namespaces

```bash
kubectl apply -f kubernetes/dev/namespace.yaml
kubectl apply -f kubernetes/test/namespace.yaml
kubectl apply -f kubernetes/prod/namespace.yaml
```

### 2. Create Secrets

```bash
# Docker registry secret
kubectl create secret docker-registry docker-registry-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  --namespace=dev

kubectl create secret docker-registry docker-registry-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  --namespace=test

kubectl create secret docker-registry docker-registry-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  --namespace=prod
```

### 3. Install Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### 4. Install Cert-Manager (for TLS)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 5. Deploy to Development

```bash
cd scripts
chmod +x deploy.sh
./deploy.sh dev latest
```

---

## Ansible Configuration

### 1. Install Ansible Collections

```bash
ansible-galaxy collection install kubernetes.core
ansible-galaxy collection install community.general
```

### 2. Configure Inventory

Edit `ansible/inventory/dev.ini`, `test.ini`, and `prod.ini`:

```ini
[dev]
dev-k8s-master ansible_host=YOUR_DEV_K8S_IP ansible_user=ubuntu

[dev:vars]
environment=dev
replicas=1
```

### 3. Test Ansible Connection

```bash
ansible -i ansible/inventory/dev.ini dev -m ping
```

### 4. Test Deployment Playbook

```bash
ansible-playbook \
  ansible/playbooks/deploy-to-k8s.yml \
  -i ansible/inventory/dev.ini \
  -e "image_tag=latest"
```

---

## Monitoring Setup

### 1. Install Prometheus

```bash
kubectl create namespace monitoring

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --values monitoring/prometheus/prometheus.yml
```

### 2. Install Grafana

```bash
helm repo add grafana https://grafana.github.io/helm-charts

helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword='admin123'
```

### 3. Configure Grafana

1. Get Grafana password:

```bash
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

2. Port-forward to access:

```bash
kubectl port-forward --namespace monitoring svc/grafana 3000:80
```

3. Access at `http://localhost:3000`
4. Add Prometheus data source: `http://prometheus-server.monitoring.svc.cluster.local`
5. Import dashboard from `monitoring/grafana/dashboards/application-overview.json`

### 4. Configure Alerts

```bash
kubectl apply -f monitoring/prometheus/alert-rules.yml
```

---

## Running the Pipeline

### 1. Manual Trigger

1. Go to Jenkins dashboard
2. Click on `cicd-demo-pipeline`
3. Click **Build with Parameters**
4. Enter parameters:
   - `BRANCH`: main
   - `IMAGE_TAG`: v1.0.0
5. Click **Build**

### 2. Git Webhook Trigger

Configure webhook in your Git repository:

- URL: `http://jenkins.example.com/github-webhook/`
- Events: Push, Pull Request

### 3. Monitor Pipeline

- **Blue Ocean**: Click on build to see visual pipeline
- **Console Output**: View detailed logs
- **Test Results**: View test reports
- **Coverage**: View coverage reports

### 4. Approval Process

**Test Environment:**

- Requires manual approval after smoke tests pass
- Timeout: 1 hour
- Any user can approve

**Production Environment:**

- Requires manual approval after integration tests
- Timeout: 4 hours
- Only `devops-lead` or `cto` can approve

---

## Troubleshooting

### Pipeline Fails at Build Stage

**Issue**: Docker build fails
**Solution**:

```bash
# Check Docker daemon
docker ps

# Check credentials
docker login

# Manual build
cd application
docker build -t test-image .
```

### Pipeline Fails at Deploy Stage

**Issue**: Cannot connect to Kubernetes
**Solution**:

```bash
# Verify kubectl
kubectl cluster-info

# Check namespace
kubectl get namespaces

# Check deployments
kubectl get deployments -n dev
```

### Pods Not Starting

**Issue**: Pods in CrashLoopBackOff
**Solution**:

```bash
# Check pod logs
kubectl logs -n dev <pod-name>

# Describe pod
kubectl describe pod -n dev <pod-name>

# Check events
kubectl get events -n dev --sort-by='.lastTimestamp'
```

### Health Checks Failing

**Issue**: Readiness/Liveness probes fail
**Solution**:

```bash
# Port forward to pod
kubectl port-forward -n dev <pod-name> 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# Check application logs
kubectl logs -n dev <pod-name> -f
```

### Canary Deployment Issues

**Issue**: Canary validation fails
**Solution**:

```bash
# Check Prometheus metrics
kubectl port-forward -n monitoring svc/prometheus-server 9090:80

# Query error rate
# Navigate to: http://localhost:9090
# Query: (sum(rate(http_request_errors_total[5m])) / sum(rate(http_requests_total[5m]))) * 100

# Manual rollback
cd scripts
./rollback.sh prod
```

### Monitoring Not Working

**Issue**: Metrics not showing in Grafana
**Solution**:

```bash
# Check Prometheus targets
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
# Navigate to: http://localhost:9090/targets

# Check pod annotations
kubectl get pod -n dev <pod-name> -o yaml | grep prometheus

# Verify metrics endpoint
kubectl port-forward -n dev <pod-name> 8000:8000
curl http://localhost:8000/metrics
```

---

## Next Steps

1. **Customize Pipeline**: Modify `jenkins/Jenkinsfile` for your needs
2. **Add Tests**: Extend `application/tests/` with more test cases
3. **Configure Alerts**: Customize `monitoring/prometheus/alert-rules.yml`
4. **Set up Backup**: Configure backup for persistent data
5. **Documentation**: Update project-specific documentation

---

## Support

For issues or questions:

- Check troubleshooting section above
- Review logs: Jenkins, Kubernetes, Application
- Contact DevOps team: devops@example.com
