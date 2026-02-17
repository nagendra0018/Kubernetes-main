# Kubernetes Complete Application Deployment Guide

This folder contains comprehensive YAML configurations for deploying a production-ready application on Kubernetes.

## 📁 File Structure

```
allydatafiles/
├── 01-namespace.yml              # Namespaces (production, staging, development)
├── 02-configmap.yml              # Application configuration
├── 03-secret.yml                 # Sensitive data (passwords, API keys)
├── 04-storage.yml                # PVCs and StorageClass
├── 05-deployment.yml             # Main application deployment
├── 06-service.yml                # Services (ClusterIP, NodePort, LoadBalancer)
├── 07-ingress.yml                # Ingress rules for external access
├── 08-hpa.yml                    # Horizontal & Vertical Pod Autoscalers
├── 09-security-rbac.yml          # RBAC, NetworkPolicy, PodSecurityPolicy
├── 10-statefulset-database.yml   # StatefulSets for PostgreSQL & Redis
├── 11-cronjob-job.yml            # CronJobs and Jobs
├── 12-monitoring.yml             # Prometheus ServiceMonitor and alerts
├── 13-daemonset.yml              # DaemonSets for logging and monitoring
└── README.md                     # This file
```

## 🚀 Deployment Order

Deploy in the following order for proper dependency resolution:

```bash
# 1. Create namespaces
kubectl apply -f 01-namespace.yml

# 2. Create ConfigMaps and Secrets
kubectl apply -f 02-configmap.yml
kubectl apply -f 03-secret.yml

# 3. Create storage resources
kubectl apply -f 04-storage.yml

# 4. Deploy RBAC and security policies
kubectl apply -f 09-security-rbac.yml

# 5. Deploy databases (StatefulSets)
kubectl apply -f 10-statefulset-database.yml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n production --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n production --timeout=300s

# 6. Deploy main application
kubectl apply -f 05-deployment.yml

# 7. Create services
kubectl apply -f 06-service.yml

# 8. Create ingress
kubectl apply -f 07-ingress.yml

# 9. Setup autoscaling
kubectl apply -f 08-hpa.yml

# 10. Deploy monitoring and logging
kubectl apply -f 12-monitoring.yml
kubectl apply -f 13-daemonset.yml

# 11. Setup scheduled jobs
kubectl apply -f 11-cronjob-job.yml
```

## 🔧 Quick Deploy All

```bash
# Deploy everything in order
kubectl apply -f 01-namespace.yml && \
kubectl apply -f 02-configmap.yml && \
kubectl apply -f 03-secret.yml && \
kubectl apply -f 04-storage.yml && \
kubectl apply -f 09-security-rbac.yml && \
kubectl apply -f 10-statefulset-database.yml && \
sleep 30 && \
kubectl apply -f 05-deployment.yml && \
kubectl apply -f 06-service.yml && \
kubectl apply -f 07-ingress.yml && \
kubectl apply -f 08-hpa.yml && \
kubectl apply -f 12-monitoring.yml && \
kubectl apply -f 13-daemonset.yml && \
kubectl apply -f 11-cronjob-job.yml
```

## 📊 What's Included

### **Security Features:**

- ✅ RBAC (Role-Based Access Control)
- ✅ ServiceAccounts with minimal permissions
- ✅ NetworkPolicies for pod isolation
- ✅ PodSecurityPolicies
- ✅ PodDisruptionBudgets
- ✅ ResourceQuotas and LimitRanges
- ✅ Secret management
- ✅ TLS/SSL certificates
- ✅ Security contexts (non-root, read-only filesystem)

### **High Availability:**

- ✅ Multiple replicas (3)
- ✅ Pod anti-affinity rules
- ✅ Liveness, Readiness, and Startup probes
- ✅ Rolling update strategy
- ✅ PodDisruptionBudget (min 2 available)
- ✅ StatefulSets for databases

### **Autoscaling:**

- ✅ Horizontal Pod Autoscaler (HPA) - CPU, Memory, Custom metrics
- ✅ Vertical Pod Autoscaler (VPA)
- ✅ Scale up/down policies
- ✅ Min/Max replica configuration

### **Monitoring & Logging:**

- ✅ Prometheus ServiceMonitor
- ✅ PrometheusRules for alerts
- ✅ Grafana dashboard configuration
- ✅ Fluentd DaemonSet for log collection
- ✅ Node-exporter for host metrics
- ✅ Application metrics endpoint

### **Storage:**

- ✅ PersistentVolumeClaims
- ✅ Dynamic volume provisioning
- ✅ StorageClass configuration
- ✅ StatefulSet volume templates
- ✅ Multiple storage types (app, database, backup)

### **Networking:**

- ✅ ClusterIP service (internal)
- ✅ NodePort service (external)
- ✅ LoadBalancer service (cloud)
- ✅ Headless service (StatefulSet)
- ✅ Ingress with TLS
- ✅ NetworkPolicies

### **Jobs & CronJobs:**

- ✅ Database backup CronJob (daily)
- ✅ Cache cleanup CronJob (every 30 min)
- ✅ Database migration Job

## 🔍 Verification Commands

```bash
# Check all resources in production namespace
kubectl get all -n production

# Check pod status
kubectl get pods -n production -o wide

# Check services
kubectl get svc -n production

# Check ingress
kubectl get ingress -n production

# Check HPA status
kubectl get hpa -n production

# Check PVC status
kubectl get pvc -n production

# View pod logs
kubectl logs -f deployment/myapp-deployment -n production

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# Describe deployment
kubectl describe deployment myapp-deployment -n production

# Check resource usage
kubectl top pods -n production
kubectl top nodes
```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Update all passwords in `03-secret.yml`
- [ ] Add real TLS certificates in `03-secret.yml`
- [ ] Update Docker registry credentials
- [ ] Configure proper Ingress hostnames
- [ ] Review and adjust resource limits
- [ ] Configure backup storage (S3/GCS)
- [ ] Set up monitoring alerts (Slack/PagerDuty)
- [ ] Enable encryption at rest for etcd
- [ ] Configure network policies for your environment
- [ ] Review and adjust autoscaling thresholds
- [ ] Set up log aggregation
- [ ] Configure backup retention policies

## 🛠️ Customization

### Update Image Version:

```bash
kubectl set image deployment/myapp-deployment myapp=myapp:v2.0.0 -n production
```

### Scale Manually:

```bash
kubectl scale deployment myapp-deployment --replicas=5 -n production
```

### Update ConfigMap:

```bash
kubectl edit configmap app-config -n production
kubectl rollout restart deployment/myapp-deployment -n production
```

### Update Secret:

```bash
kubectl edit secret app-secrets -n production
kubectl rollout restart deployment/myapp-deployment -n production
```

## 📈 Monitoring Access

After deploying monitoring stack:

```bash
# Port-forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Port-forward to Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Access metrics endpoint
kubectl port-forward -n production svc/myapp-service 9090:9090
curl http://localhost:9090/metrics
```

## 🔄 Rollback

```bash
# View rollout history
kubectl rollout history deployment/myapp-deployment -n production

# Rollback to previous version
kubectl rollout undo deployment/myapp-deployment -n production

# Rollback to specific revision
kubectl rollout undo deployment/myapp-deployment --to-revision=2 -n production
```

## 🧹 Cleanup

```bash
# Delete all resources in production namespace
kubectl delete namespace production

# Or delete specific resources
kubectl delete -f 11-cronjob-job.yml
kubectl delete -f 13-daemonset.yml
kubectl delete -f 12-monitoring.yml
kubectl delete -f 08-hpa.yml
kubectl delete -f 07-ingress.yml
kubectl delete -f 06-service.yml
kubectl delete -f 05-deployment.yml
kubectl delete -f 10-statefulset-database.yml
kubectl delete -f 09-security-rbac.yml
kubectl delete -f 04-storage.yml
kubectl delete -f 03-secret.yml
kubectl delete -f 02-configmap.yml
kubectl delete -f 01-namespace.yml
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Production Best Practices](https://kubernetes.io/docs/setup/best-practices/)
- [Security Best Practices](https://kubernetes.io/docs/concepts/security/)

## 🆘 Troubleshooting

### Pod not starting:

```bash
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production
kubectl get events -n production
```

### Service not accessible:

```bash
kubectl get endpoints <service-name> -n production
kubectl describe svc <service-name> -n production
```

### Database connection issues:

```bash
kubectl exec -it postgres-0 -n production -- psql -U appuser -d myappdb
kubectl exec -it redis-0 -n production -- redis-cli -a <password>
```

### Check network policies:

```bash
kubectl get networkpolicy -n production
kubectl describe networkpolicy myapp-network-policy -n production
```

---

**Note:** This is a template configuration. Customize according to your application requirements, cloud provider, and security policies.

🚀 **Happy Deploying!**
