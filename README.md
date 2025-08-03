# 🌟 Joulaa Platform

<div align="center">

![Joulaa Logo](https://via.placeholder.com/200x80/4F46E5/FFFFFF?text=Joulaa)

**Enterprise-Grade Arabic-First AI Platform for Business Intelligence & Automation**

**Created by [MedNextApp.com](https://mednextapp.com)**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/your-org/joulaa-platform)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/your-org/joulaa-platform/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Arabic Support](https://img.shields.io/badge/Arabic-RTL%20Support-orange)](https://github.com/your-org/joulaa-platform)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple)](https://github.com/your-org/joulaa-platform)

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🛠️ Development](#-development) • [🔒 Security](#-security) • [🤝 Contributing](#-contributing)

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Development](#-development)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Security](#-security)
- [Monitoring](#-monitoring)
- [Contributing](#-contributing)
- [Support](#-support)
- [License](#-license)

## 🎯 Overview

Joulaa Platform is a comprehensive, enterprise-grade business intelligence and AI automation platform specifically designed for Arabic-speaking enterprises. Built with modern technologies and designed for scalability, security, and performance, it provides native Arabic language support with full RTL (Right-to-Left) interface capabilities.

### 🌍 Target Market

**Primary Focus**: Arabic-speaking enterprises in the MENA region seeking AI-powered business automation and intelligence solutions.

- **Enterprise Size**: Mid to large enterprises (500+ employees)
- **Industries**: Finance, Manufacturing, Retail, Healthcare, Government, Oil & Gas
- **Geographic Focus**: Saudi Arabia, UAE, Egypt, Jordan, Qatar, Kuwait, Bahrain
- **Languages**: Native Arabic with English support

### 🎯 Key Capabilities

- **🤖 AI-Powered Analytics**: Advanced machine learning algorithms for predictive analytics
- **📊 Real-time Dashboards**: Interactive visualizations with real-time data updates
- **🔗 Enterprise Integration**: Seamless integration with SAP, Oracle, Microsoft, and other enterprise systems
- **🌐 Multi-language Support**: Arabic and English language processing with advanced NLP capabilities
- **☁️ Scalable Architecture**: Kubernetes-native design for horizontal scaling
- **🛡️ Security First**: Enterprise-grade security with compliance support (GDPR, SOC 2)
- **📱 RTL Support**: Complete Right-to-Left interface for Arabic users
- **🎨 Agent Studio**: Visual drag-and-drop interface for building AI agents

## ✨ Key Features

### 🤖 AI & Machine Learning
- **Predictive Analytics**: Forecast trends and identify patterns using advanced ML models
- **Natural Language Processing**: Advanced Arabic and English text analysis
- **AI Agent Builder**: Visual drag-and-drop interface for creating custom AI agents
- **OpenAI Integration**: GPT models for text generation and analysis
- **Anthropic Claude**: Advanced reasoning and analysis capabilities
- **Custom Models**: Train and deploy custom ML models for specific use cases
- **Arabic NLP**: Specialized Arabic language processing with reshaping and bidirectional text support

### 📊 Business Intelligence
- **Interactive Dashboards**: Drag-and-drop dashboard builder with real-time updates
- **Real-time Reporting**: Live data visualization and automated reporting
- **Data Visualization**: Charts, graphs, maps, and custom visualizations
- **KPI Monitoring**: Key performance indicator tracking and alerting
- **Scheduled Reports**: Automated report generation and distribution
- **Multi-language Reports**: Generate reports in both Arabic and English

### 🔗 Enterprise Integration
- **REST APIs**: Comprehensive API for custom integrations
- **WebSocket Support**: Real-time bidirectional communication
- **Database Connectivity**: PostgreSQL with Redis caching
- **File Storage**: MinIO object storage for scalable file management
- **Webhook Support**: Real-time event notifications
- **Enterprise SSO**: Single sign-on integration capabilities

### 🛡️ Security & Compliance
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Role-Based Access Control**: Granular permission management
- **Data Encryption**: End-to-end encryption at rest and in transit
- **Audit Logging**: Comprehensive activity tracking and compliance reporting
- **Rate Limiting**: API rate limiting and DDoS protection
- **Arabic Password Validation**: Specialized validation for Arabic users

### 🌐 Internationalization
- **Arabic Language**: Full RTL support with Arabic NLP capabilities
- **English Language**: Comprehensive English language processing
- **RTL Interface**: Complete right-to-left user interface
- **Bidirectional Text**: Proper handling of mixed Arabic-English content
- **Locale Support**: Multi-timezone and cultural formatting

## 🛠️ Technology Stack

### Frontend Technologies
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite with SWC for fast development
- **Styling**: Tailwind CSS with RTL support
- **State Management**: Zustand for lightweight state management
- **Data Fetching**: TanStack Query (React Query) for server state
- **Forms**: React Hook Form with Zod validation
- **Routing**: React Router DOM v6
- **Internationalization**: React i18next with Arabic support
- **UI Components**: Custom components with Lucide React icons
- **Animations**: Framer Motion for smooth animations
- **Drag & Drop**: React DnD for agent studio
- **Charts**: Recharts for data visualization
- **Real-time**: Socket.IO client for WebSocket connections

### Backend Technologies
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 ORM
- **Cache**: Redis 7+ for caching and session management
- **Authentication**: JWT with refresh tokens and bcrypt hashing
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **Validation**: Pydantic v2 for data validation and serialization
- **Async Support**: Full async/await support with ASGI
- **WebSockets**: Native WebSocket support for real-time features
- **File Upload**: Multipart form data handling
- **Security**: CORS, rate limiting, and input sanitization

### AI & Machine Learning
- **OpenAI**: GPT models for text generation and analysis
- **Anthropic**: Claude models for advanced reasoning
- **Arabic NLP**: Custom Arabic language processing pipeline
- **Text Processing**: Arabic reshaper and bidirectional text support
- **Vector Operations**: Embeddings and similarity search capabilities
- **ML Pipeline**: Automated model training and deployment

### Infrastructure & DevOps
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes with Helm charts
- **Object Storage**: MinIO for scalable file storage
- **Monitoring**: Prometheus and Grafana integration ready
- **CI/CD**: GitHub Actions workflows
- **Database Migrations**: Alembic for database schema management
- **Environment Management**: Multiple environment configurations

### Development Tools
- **Code Quality**: ESLint, Prettier, Black, Flake8
- **Testing**: Vitest (frontend), Pytest (backend)
- **Type Checking**: TypeScript and mypy
- **Pre-commit Hooks**: Husky and lint-staged
- **Package Management**: npm workspaces for monorepo structure

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Load Balancer │    │   Backend       │
│                 │    │                 │    │                 │
│ • React/TS      │───▶│ • Nginx/Traefik │───▶│ • FastAPI       │
│ • Tailwind CSS  │    │ • SSL/TLS       │    │ • SQLAlchemy    │
│ • RTL Support   │    │ • Rate Limiting │    │ • WebSockets    │
│ • Agent Studio  │    │ • CORS          │    │ • AI Integration│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Object Storage│    │   Monitoring    │    │   Database      │
│                 │    │                 │    │                 │
│ • MinIO         │    │ • Prometheus    │    │ • PostgreSQL    │
│ • File Storage  │    │ • Grafana       │    │ • Redis Cache   │
│ • Asset Delivery│    │ • Health Checks │    │ • Vector Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Services   │    │   External APIs │    │   Security      │
│                 │    │                 │    │                 │
│ • OpenAI GPT    │    │ • Enterprise    │    │ • JWT Auth      │
│ • Anthropic     │    │ • SAP/Oracle    │    │ • RBAC          │
│ • Arabic NLP    │    │ • Third-party   │    │ • Audit Logs    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Project Structure

```
joulaa-platform/
├── 📁 frontend/                 # React TypeScript frontend
│   ├── 📁 src/
│   │   ├── 📁 components/       # Reusable UI components
│   │   ├── 📁 pages/           # Page components
│   │   ├── 📁 hooks/           # Custom React hooks
│   │   ├── 📁 services/        # API services
│   │   ├── 📁 stores/          # Zustand stores
│   │   ├── 📁 utils/           # Utility functions
│   │   └── 📁 i18n/            # Internationalization
│   ├── 📄 package.json         # Frontend dependencies
│   ├── 📄 vite.config.ts       # Vite configuration
│   └── 📄 tailwind.config.js   # Tailwind CSS config
├── 📁 backend/                  # FastAPI Python backend
│   ├── 📁 app/                 # Application code
│   ├── 📁 core/                # Core functionality
│   ├── 📁 models/              # Database models
│   ├── 📁 schemas/             # Pydantic schemas
│   ├── 📁 services/            # Business logic
│   ├── 📁 utils/               # Utility functions
│   ├── 📁 tests/               # Test suites
│   ├── 📄 requirements.txt     # Python dependencies
│   └── 📄 Dockerfile           # Backend container
├── 📁 k8s/                     # Kubernetes manifests
├── 📁 scripts/                 # Deployment scripts
├── 📁 shared/                  # Shared types and utilities
├── 📄 docker-compose.yml       # Development environment
├── 📄 package.json             # Root package configuration
└── 📄 README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- **Docker**: 20.10+ with Docker Compose
- **Node.js**: 18+ with npm
- **Git**: Latest version
- **Optional**: Python 3.11+ for local backend development

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/joulaa-platform.git
cd joulaa-platform
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env.development

# Edit configuration (add your API keys)
vim .env.development
```

### 3. Start Development Environment

```bash
# Start all services with Docker Compose
docker-compose up -d

# Wait for services to be ready (check logs)
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create test users (optional)
docker-compose exec backend python create_test_users.py
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (admin/joulaa_admin_password)
- **PostgreSQL**: localhost:5432 (joulaa_user/joulaa_password)
- **Redis**: localhost:6379

## 📦 Installation

### Development Installation

#### Option 1: Docker Development (Recommended)

```bash
# Clone and setup
git clone https://github.com/your-org/joulaa-platform.git
cd joulaa-platform

# Start development environment
docker-compose up -d

# Install frontend dependencies for IDE support
cd frontend && npm install
```

#### Option 2: Local Development

**Backend Setup:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Production Installation

#### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/your-org/joulaa-platform.git
cd joulaa-platform

# Configure production environment
cp .env.example .env.production
vim .env.production

# Build and start production stack
docker-compose -f docker-compose.prod.yml up -d
```

#### Using Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Wait for deployment
kubectl rollout status deployment/backend
kubectl rollout status deployment/frontend

# Get service URLs
kubectl get ingress
```

## ⚙️ Configuration

### Environment Variables

The platform uses environment variables for configuration. Key variables include:

```bash
# Application
APP_NAME="Joulaa Platform"
APP_VERSION="1.0.0"
ENVIRONMENT="development"  # development, staging, production
DEBUG=true
SECRET_KEY="your-secret-key-here"

# Database
DATABASE_URL="postgresql://joulaa_user:joulaa_password@localhost:5432/joulaa"
REDIS_URL="redis://:redis_password@localhost:6379/0"

# AI Services
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"

# Storage
MINIO_ENDPOINT="localhost:9000"
MINIO_ACCESS_KEY="joulaa_admin"
MINIO_SECRET_KEY="joulaa_admin_password"

# Security
JWT_SECRET_KEY="your-jwt-secret"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
```

### Feature Flags

```bash
# AI Features
FEATURE_AI_CHAT=true
FEATURE_PREDICTIVE_ANALYTICS=true
FEATURE_ARABIC_NLP=true

# UI Features
FEATURE_DARK_MODE=true
FEATURE_RTL_SUPPORT=true
FEATURE_AGENT_STUDIO=true
```

## 🛠️ Development

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards and conventions
   - Write tests for new functionality
   - Update documentation as needed
   - Ensure RTL support for Arabic text

3. **Run Tests**
   ```bash
   # Frontend tests
   cd frontend && npm test
   
   # Backend tests
   cd backend && pytest
   ```

4. **Code Quality Checks**
   ```bash
   # Frontend
   npm run lint
   npm run type-check
   
   # Backend
   black .
   flake8
   ```

### Testing

#### Frontend Testing

```bash
# Run unit tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

#### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

The project uses several tools to maintain code quality:

- **Frontend**: ESLint, Prettier, TypeScript
- **Backend**: Black, Flake8, mypy
- **Pre-commit Hooks**: Husky and lint-staged
- **Conventional Commits**: Standardized commit messages

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Authentication

The API uses JWT tokens for authentication:

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/users/me"
```

### WebSocket Endpoints

- **Chat**: `/ws/chat/{chat_id}` - Real-time chat functionality
- **Notifications**: `/ws/notifications` - Real-time notifications
- **Agent Studio**: `/ws/agent-studio` - Real-time agent building

## 🚀 Deployment

### Docker Deployment

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace joulaa

# Apply secrets
kubectl apply -f k8s/secrets/

# Deploy services
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n joulaa
```

### Health Checks

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

## 🔒 Security

### Security Features

- **Authentication**: JWT with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS 1.3 for data in transit, AES-256 at rest
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting and DDoS protection
- **Security Headers**: CORS, CSP, HSTS, and more
- **Audit Logging**: Comprehensive activity tracking
- **Arabic Security**: Specialized validation for Arabic text input

### Security Best Practices

- Regular security updates and dependency scanning
- Secure secret management
- Network segmentation
- Regular security audits
- Compliance with GDPR and regional regulations

## 📊 Monitoring

### Application Metrics

- **Request Rate**: HTTP requests per second
- **Response Time**: API response latencies
- **Error Rate**: HTTP error percentages
- **Database**: Connection pool and query metrics
- **Cache**: Redis hit/miss ratios
- **AI Usage**: OpenAI and Anthropic API usage

### Monitoring Stack

- **Metrics**: Prometheus for metrics collection
- **Visualization**: Grafana for dashboards
- **Alerting**: Prometheus Alertmanager
- **Logging**: Structured logging with JSON format
- **Tracing**: Distributed tracing ready

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Guide

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow coding standards and add tests
4. **Run tests**: Ensure all tests pass
5. **Commit changes**: Use conventional commit messages
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Create Pull Request**: Submit PR with detailed description

### Development Guidelines

- Follow existing code style and conventions
- Write tests for new features
- Update documentation as needed
- Ensure RTL support for Arabic text
- Test with both Arabic and English interfaces
- Consider accessibility and performance

## 📞 Support

### Getting Help

- **Documentation**: [docs.joulaa.com](https://docs.joulaa.com)
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-org/joulaa-platform/issues)
- **Email**: support@joulaa.com
- **Community**: [Join our Discord](https://discord.gg/joulaa)

### Enterprise Support

For enterprise customers:

- **Priority Support**: 24/7 support with SLA
- **Professional Services**: Implementation and consulting
- **Training**: Custom training programs
- **Custom Development**: Feature development and customization

Contact: enterprise@joulaa.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by the Joulaa Team**

**Created by [MedNextApp.com](https://mednextapp.com)**

[Website](https://joulaa.com) • [Documentation](https://docs.joulaa.com) • [Support](mailto:support@joulaa.com) • [Enterprise](mailto:enterprise@joulaa.com)

</div>
