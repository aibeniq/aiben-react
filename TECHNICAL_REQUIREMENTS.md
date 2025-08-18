# Technical Requirements - AIBeniq Application

## System Requirements

### Minimum Hardware Requirements

- **CPU**: 4+ cores recommended for production
- **RAM**: 8GB minimum, 16GB+ recommended for production
- **Storage**: 10GB+ free space for application and dependencies
- **Network**: Stable internet connection for LLM API access and package downloads

### Supported Operating Systems

- **Development**: Windows 10/11, macOS 10.15+, Linux Ubuntu 18.04+
- **Production**: Linux distributions (Ubuntu 20.04+, RHEL 8+, CentOS 8+)
- **Container Platform**: Docker-compatible systems, OpenShift 4.x

## Core Technology Stack

### Backend Requirements

- **Python**: 3.10.x (minimum 3.10, maximum < 4.0)
- **Package Manager**: uv 0.5.11+ (preferred) or pip
- **Web Framework**: FastAPI 0.114.2+
- **Database ORM**: SQLModel 0.0.21+
- **Database Driver**: psycopg[binary] 3.1.13+

### Frontend Requirements

- **Node.js**: 20.x LTS
- **Package Manager**: npm (included with Node.js)
- **Build Tool**: Vite 6.3.5+
- **Framework**: React 18.2.0+
- **TypeScript**: 5.2.2+

### Database Requirements

- **Primary Database**: PostgreSQL 17+ (production)
- **Vector Database**: ChromaDB 1.0.9 (embedded mode)

## Infrastructure Dependencies

### Container Platform

- **Docker**: 24.0+ with BuildKit support
- **Docker Compose**: 2.20+ for local development
- **OpenShift**: 4.12+ for enterprise deployment
- **Kubernetes**: 1.25+ (if using vanilla Kubernetes)

### Cloud Services (Production)

- **ROSA**: Red Hat OpenShift Service on AWS
- **AWS Services**: Route 53, ELB, VPC, IAM
- **Container Registry**: Red Hat Quay.io, AWS ECR, or Docker Hub

## Production Deployment

### Container Specifications

- **Base Images**:
  - Backend: python:3.10 (official)
  - Frontend: nginx:1 with Node.js 20 build stage
- **Security**: Non-root user configuration for OpenShift compatibility
- **Resource Limits**: Configurable via Kubernetes manifests

### Resource Usage

- **Backend**: ~512MB RAM per instance
- **Frontend**: ~100MB RAM per nginx instance
- **Database**: 2GB+ RAM recommended
- **Vector Operations**: Additional memory for embeddings
