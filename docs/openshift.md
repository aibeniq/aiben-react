# OpenShift / ROSA

Two tiers: Local CRC (dev) and ROSA (managed prod).

## Quickstart (Dev - CRC)

```powershell
crc setup
crc config set memory 16384
crc start
oc login -u developer -p developer https://api.crc.testing:6443
./scripts/deploy-openshift.ps1 -Environment development
```

## Quickstart (ROSA Prod)

```powershell
aws configure
rosa login
rosa create cluster --cluster-name aibeniq --region us-east-1 --compute-nodes 3
rosa create admin --cluster aibeniq
oc login https://api.<cluster>.openshiftapps.com:6443 -u cluster-admin -p <pwd>
./scripts/deploy-openshift.ps1 -Environment production
```

## Operations

- Scale pause/resume: `./scripts/pause-cluster.ps1 -Action pause|resume`
- Model pre-download handled by backend threads post model add.

## Troubleshooting

- PVC immutable fields: avoid patching storageClassName; embed spec in base.
- Initial Ollama model pull may take 60s+; increase request timeouts.
