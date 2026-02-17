# CI/CD Project - Complete Overview

## 🎯 Project Summary

This is a **production-ready, enterprise-grade CI/CD pipeline** that demonstrates best practices for deploying applications across multiple environments (Development, Test, Production) using modern DevOps tools and practices.

---

## 📁 Project Structure

```
ci_cd/
├── README.md                          # Main project documentation
├── application/                       # Python Flask application
│   ├── src/
│   │   └── app.py                    # REST API with 11 endpoints
│   ├── tests/
│   │   └── test_app.py               # 15 unit tests with pytest
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Production Docker image
├── jenkins/
│   └── Jenkinsfile                   # 16-stage CI/CD pipeline
├── kubernetes/                        # K8s manifests for all environments
│   ├── dev/
│   │   ├── namespace.yaml            # Dev namespace
│   │   ├── deployment.yaml           # 1 replica, minimal resources
│   │   ├── service.yaml              # LoadBalancer service
│   │   └── ingress.yaml              # dev.app.example.com
│   ├── test/
│   │   ├── namespace.yaml            # Test namespace
│   │   ├── deployment.yaml           # 2 replicas, medium resources
│   │   ├── service.yaml              # LoadBalancer service
│   │   └── ingress.yaml              # test.app.example.com
│   └── prod/
│       ├── namespace.yaml            # Production namespace
│       ├── deployment.yaml           # 3 replicas, high availability
│       ├── service.yaml              # LoadBalancer with session affinity
│       ├── ingress.yaml              # app.example.com with rate limiting
│       ├── hpa.yaml                  # Auto-scaling (3-10 pods)
│       └── network-policy.yaml       # Network security policies
├── ansible/
│   ├── playbooks/
│   │   ├── deploy-to-k8s.yml        # Main deployment playbook
│   │   └── rollback.yml              # Rollback playbook
│   └── inventory/
│       ├── dev.ini                   # Dev environment config
│       └── prod.ini                  # Prod environment config
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml            # Prometheus configuration
│   │   └── alert-rules.yml           # 15 alert rules
│   └── grafana/
│       └── dashboards/
│           └── application-overview.json  # Pre-built Grafana dashboard
├── scripts/
│   ├── build.sh                      # Build and test Docker image
│   ├── deploy.sh                     # Deploy to any environment
│   ├── rollback.sh                   # Rollback deployment
│   └── test.sh                       # Run tests locally
└── docs/
    └── setup-guide.md                # Complete setup instructions
```

---

## 🚀 Key Features

### 1. **Multi-Environment Support**

- **Development**: Auto-deploy on every commit, 1 replica
- **Test/Staging**: Manual approval required, 2 replicas
- **Production**: Manual approval with restricted approvers, 3+ replicas with auto-scaling

### 2. **Comprehensive CI/CD Pipeline** (16 Stages)

1. ✅ **Checkout** - Clone repository and capture Git metadata
2. 🔍 **Code Analysis** - Parallel linting (pylint/flake8) + SonarQube
3. 🧪 **Unit Tests** - pytest with >80% coverage requirement
4. 🐳 **Build Docker Image** - Multi-stage build, tagged with version/commit
5. 🔒 **Security Scan** - Parallel Trivy (container) + Safety (dependencies)
6. 🚢 **Deploy to Dev** - Automatic deployment to dev namespace
7. ✅ **Smoke Tests Dev** - Health checks and API validation
8. ⏸️ **Approval for Test** - Manual approval (1 hour timeout)
9. 🚢 **Deploy to Test** - Deploy to test namespace
10. 🧪 **Integration Tests** - Full test suite execution
11. ⏸️ **Approval for Production** - Restricted approval (4 hour timeout)
12. 🎯 **Deploy Canary** - 10% traffic canary release
13. 📊 **Canary Analysis** - Prometheus metrics validation
14. 🚢 **Deploy Production Full** - Blue-green deployment via Ansible
15. ✅ **Post-Deployment Validation** - Health checks and smoke tests
16. 📢 **Notifications** - Slack alerts on success/failure

### 3. **Application Features**

- **REST API**: Flask application with 11 endpoints
  - `/health` - Kubernetes liveness probe
  - `/ready` - Kubernetes readiness probe
  - `/metrics` - Prometheus metrics
  - `/api/users` - CRUD operations
  - `/api/info` - Application metadata
- **Testing**: 15 unit tests with pytest
- **Monitoring**: Built-in Prometheus metrics
- **Security**: Non-root user, minimal base image

### 4. **Deployment Strategies**

- **Development**: Direct deployment
- **Test**: Rolling update
- **Production**: Canary → Blue-Green with automatic rollback

### 5. **Monitoring & Observability**

- **Prometheus**:
  - Application metrics (request rate, errors, latency)
  - Infrastructure metrics (CPU, memory, pods)
  - Custom alert rules (15 alerts)
- **Grafana**:
  - Pre-built dashboard with 6 panels
  - Real-time monitoring across all environments
  - Alerting integration

### 6. **Security Features**

- **Container Scanning**: Trivy for vulnerability detection
- **Code Quality**: SonarQube SAST analysis
- **Dependency Checking**: Safety for Python packages
- **Network Policies**: Kubernetes network segmentation
- **RBAC**: Role-based access control
- **Non-root Containers**: Security-hardened images

### 7. **Automation**

- **Ansible Playbooks**: Automated deployment and rollback
- **Bash Scripts**: Utility scripts for common operations
- **Health Checks**: Automated validation at each stage
- **Auto-scaling**: HPA based on CPU/memory metrics

---

## 🛠️ Technology Stack

| Category             | Technologies                        |
| -------------------- | ----------------------------------- |
| **Application**      | Python 3.11, Flask 3.0, Gunicorn    |
| **Testing**          | pytest, pytest-cov, pylint, flake8  |
| **Containerization** | Docker, Multi-stage builds          |
| **Orchestration**    | Kubernetes 1.28+                    |
| **CI/CD**            | Jenkins (Declarative Pipeline)      |
| **IaC**              | Ansible, kubectl                    |
| **Monitoring**       | Prometheus, Grafana                 |
| **Security**         | Trivy, SonarQube, Safety            |
| **Version Control**  | Git (feature/develop/main branches) |

---

## 📊 Pipeline Flow

```
Developer Commit
       ↓
   Git Push
       ↓
Jenkins Trigger
       ↓
┌──────────────────┐
│ Code Analysis    │ → SonarQube + Linting
└──────────────────┘
       ↓
┌──────────────────┐
│ Unit Tests       │ → pytest (>80% coverage)
└──────────────────┘
       ↓
┌──────────────────┐
│ Build Image      │ → Docker multi-stage build
└──────────────────┘
       ↓
┌──────────────────┐
│ Security Scan    │ → Trivy + Safety
└──────────────────┘
       ↓
┌──────────────────┐
│ Deploy to Dev    │ → Automatic (kubectl)
└──────────────────┘
       ↓
┌──────────────────┐
│ Smoke Tests      │ → Health checks
└──────────────────┘
       ↓
┌──────────────────┐
│ Manual Approval  │ → Test deployment (1h timeout)
└──────────────────┘
       ↓
┌──────────────────┐
│ Deploy to Test   │ → Rolling update
└──────────────────┘
       ↓
┌──────────────────┐
│ Integration Tests│ → Full test suite
└──────────────────┘
       ↓
┌──────────────────┐
│ Manual Approval  │ → Prod deployment (4h, restricted)
└──────────────────┘
       ↓
┌──────────────────┐
│ Canary Deploy    │ → 10% traffic
└──────────────────┘
       ↓
┌──────────────────┐
│ Canary Analysis  │ → Prometheus metrics
└──────────────────┘
       ↓
     Pass?
    /    \
  Yes     No
   ↓       ↓
┌─────┐ ┌─────────┐
│Full │ │Rollback │
│Prod │ └─────────┘
└─────┘
   ↓
┌──────────────────┐
│ Post-Deploy Test │ → Final validation
└──────────────────┘
   ↓
┌──────────────────┐
│ Slack Notify     │ → Success/Failure alerts
└──────────────────┘
```

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **CI/CD Best Practices**
   - Automated testing at multiple stages
   - Progressive deployment (dev → test → prod)
   - Manual approval gates for production
   - Automatic rollback on failure

2. **Kubernetes Expertise**
   - Multi-environment namespace management
   - Deployment strategies (rolling, canary, blue-green)
   - Health checks and readiness probes
   - Auto-scaling with HPA
   - Network policies for security

3. **DevOps Automation**
   - Jenkins declarative pipelines
   - Ansible playbooks for deployment
   - Bash scripts for common operations
   - Git workflow integration

4. **Monitoring & Observability**
   - Prometheus metrics collection
   - Grafana dashboard creation
   - Alert rule configuration
   - Health check implementation

5. **Security Integration**
   - Container vulnerability scanning
   - Static code analysis
   - Dependency checking
   - Network segmentation
   - RBAC implementation

---

## 🚦 Quick Start

### 1. Prerequisites

- Docker, Kubernetes, Jenkins, Ansible installed
- Kubernetes cluster running
- Jenkins with required plugins

### 2. Deploy to Development

```bash
cd ci_cd/scripts
chmod +x deploy.sh
./deploy.sh dev latest
```

### 3. Run Tests

```bash
chmod +x test.sh
./test.sh
```

### 4. Build Docker Image

```bash
chmod +x build.sh
./build.sh v1.0.0
```

### 5. Access Application

```bash
# Port forward to service
kubectl port-forward -n dev svc/cicd-demo 8080:80

# Access application
curl http://localhost:8080/health
```

---

## 📈 Monitoring

### Access Grafana

```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
# Open: http://localhost:3000
# Default: admin / admin123
```

### Access Prometheus

```bash
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
# Open: http://localhost:9090
```

### View Metrics

```bash
# Application metrics
curl http://your-app-url/metrics

# Query Prometheus
# Request rate: rate(http_requests_total[5m])
# Error rate: (rate(http_request_errors_total[5m]) / rate(http_requests_total[5m])) * 100
```

---

## 🔄 Rollback Procedure

### Automatic Rollback

- Triggered automatically if canary analysis fails
- Reverts to previous stable version

### Manual Rollback

```bash
cd ci_cd/scripts
./rollback.sh prod  # Rollback to previous version
./rollback.sh prod 3  # Rollback to specific revision
```

---

## 🎯 Best Practices Implemented

1. ✅ **Infrastructure as Code** - All configurations in version control
2. ✅ **Immutable Infrastructure** - Docker images never modified
3. ✅ **Progressive Delivery** - Gradual rollout to production
4. ✅ **Automated Testing** - Tests at every stage
5. ✅ **Security First** - Multiple security scans
6. ✅ **Monitoring** - Comprehensive metrics and alerts
7. ✅ **Documentation** - Complete setup and troubleshooting guides
8. ✅ **Disaster Recovery** - Easy rollback procedures

---

## 📞 Support & Troubleshooting

### Common Issues

**1. Pipeline Fails at Build**

- Check Docker daemon: `docker ps`
- Verify credentials: `docker login`

**2. Deployment Fails**

- Check cluster: `kubectl cluster-info`
- View events: `kubectl get events -n <namespace>`

**3. Pods Not Starting**

- Check logs: `kubectl logs -n <namespace> <pod-name>`
- Describe pod: `kubectl describe pod -n <namespace> <pod-name>`

**4. Health Checks Fail**

- Port forward: `kubectl port-forward -n <namespace> <pod-name> 8000:8000`
- Test endpoint: `curl http://localhost:8000/health`

### Documentation

- **Setup Guide**: `docs/setup-guide.md` - Complete installation instructions
- **Main README**: `README.md` - Architecture and overview
- **Troubleshooting**: Check logs, events, and metrics

---

## 🎉 Conclusion

This CI/CD project provides a **complete, production-ready pipeline** that you can:

- **Use as-is** for Python Flask applications
- **Adapt** for other languages/frameworks
- **Learn from** for DevOps best practices
- **Extend** with additional features

**Total Files Created**: 30+

- Application code: 4 files
- Kubernetes manifests: 14 files
- Ansible playbooks: 4 files
- Monitoring configs: 3 files
- Scripts: 4 files
- Documentation: 2 files

---

## 📝 Next Steps

1. **Customize** for your application
2. **Add** database and cache layers
3. **Integrate** with your Git repository
4. **Configure** Slack/email notifications
5. **Extend** monitoring dashboards
6. **Implement** disaster recovery
7. **Add** performance testing
8. **Set up** log aggregation (ELK stack)

---

**Built with ❤️ for DevOps Excellence**

For questions or improvements, please reach out to the DevOps team!
