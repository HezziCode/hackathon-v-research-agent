---
name: kubernetes-deploy
description: |
  Use when deploying Digital FTEs to Kubernetes with Agent Sandbox (gVisor), Dapr sidecar injection,
  persistent storage, network policies, and resource limits. Use when creating sandbox configs,
  deployment manifests, or service monitors.
  NOT when building application code (use the SDK skills instead).
---

# Kubernetes Deploy — Secure Execution Foundation

## Overview

Kubernetes deployment (L0) provides the secure execution foundation for Digital FTEs. Each FTE runs inside an Agent Sandbox (gVisor) with Dapr sidecar, persistent storage, network policies, and resource limits.

## Agent Sandbox CRDs

### Sandbox — Single Isolated Environment

```yaml
apiVersion: agentsandbox.io/v1alpha1
kind: Sandbox
metadata:
  name: research-analyst-fte
  namespace: digital-ftes
spec:
  runtime: gvisor  # or kata-containers
  resources:
    limits:
      cpu: "2"
      memory: "4Gi"
      ephemeral-storage: "10Gi"
    requests:
      cpu: "500m"
      memory: "1Gi"
  storage:
    persistentVolumeClaim:
      claimName: fte-working-dir
      mountPath: /workspace
  networkPolicy:
    egress:
      - to: ["kafka:9092", "redis:6379"]
      - to: ["*.googleapis.com:443"]  # For Gemini API
      - to: ["api.anthropic.com:443"]
      - to: ["api.openai.com:443"]
    ingress:
      - from: ["fastapi-service"]
  ttl: 24h
  autoResumeOnReconnect: true
```

### SandboxPool — Pre-warmed Pool

```yaml
apiVersion: agentsandbox.io/v1alpha1
kind: SandboxPool
metadata:
  name: research-fte-pool
spec:
  size: 3  # Pre-warmed sandboxes ready
  template:
    spec:
      runtime: gvisor
      resources:
        limits: { cpu: "2", memory: "4Gi" }
```

## Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: research-analyst-fte
  namespace: digital-ftes
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "research-fte"
    dapr.io/app-port: "8000"
spec:
  replicas: 1
  template:
    spec:
      runtimeClassName: gvisor
      containers:
        - name: fte-worker
          image: research-analyst-fte:v1
          ports:
            - containerPort: 8000
          env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: llm-api-keys
                  key: anthropic
          volumeMounts:
            - name: workspace
              mountPath: /workspace
      volumes:
        - name: workspace
          persistentVolumeClaim:
            claimName: fte-workspace
```

## Service Monitor (Prometheus)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: research-fte-monitor
spec:
  selector:
    matchLabels:
      app: research-analyst-fte
  endpoints:
    - port: metrics
      interval: 30s
```

## Key Rules

1. ALL FTE pods MUST use `runtimeClassName: gvisor` or Kata
2. Dapr sidecar injection MUST be enabled (`dapr.io/enabled: "true"`)
3. API keys via Kubernetes Secrets, never in env or code
4. Network policies MUST restrict egress to known endpoints only
5. Persistent volumes for workspace (survives restarts)
6. Resource limits are mandatory — prevent runaway LLM loops
7. SandboxPool for eliminating cold-start latency
