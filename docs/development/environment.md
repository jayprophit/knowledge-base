---
title: Development Environment Setup
description: Comprehensive guide to setting up and configuring the development environment
author: DevOps Team
created_at: '2025-07-04'
updated_at: '2025-07-05'
version: 2.0.0
---

# Development Environment

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Setup](#quick-setup)
3. [Detailed Setup](#detailed-setup)
4. [Configuration](#configuration)
5. [Docker Setup](#docker-setup)
6. [IDE Configuration](#ide-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## System Requirements

### Hardware
- **CPU**: 4 cores (8+ recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 20GB free space (SSD recommended)
- **OS**: Linux/macOS/Windows 10+

### Software Dependencies

| Software | Version | Required | Notes |
|----------|---------|----------|-------|
| Python | 3.9+ | ✅ | Core language |
| Node.js | 16.0+ | ✅ | Frontend development |
| Docker | 20.10+ | ✅ | Containerization |
| Git | 2.30+ | ✅ | Version control |
| PostgreSQL | 13+ | ⚠️ | Required for local DB |
| Redis | 6.0+ | ⚠️ | Required for caching |

## Quick Setup

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/knowledge-base.git
cd knowledge-base

# Run the setup script
./scripts/setup.sh

# Start the development environment
make dev
```

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/knowledge-base.git
   cd knowledge-base
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

## Detailed Setup

### Python Environment

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   # Core requirements
   pip install -r requirements.txt
   
   # Development requirements
   pip install -r requirements-dev.txt
   ```

3. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```ini
# Application
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/knowledge_base

# Cache
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@example.com

# Authentication
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

### Database Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS (using Homebrew)
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create database and user**
   ```sql
   CREATE DATABASE knowledge_base;
   CREATE USER kb_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE knowledge_base TO kb_user;
   ```

## Docker Setup

### Development with Docker

1. **Build and start containers**
   ```bash
   docker-compose up -d
   ```

2. **Run database migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Web | 8000 | Django development server |
| Frontend | 3000 | Next.js development server |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache and message broker |
| PgAdmin | 5050 | Database administration |

## IDE Configuration

### VS Code

1. **Recommended extensions**
   - Python
   - ESLint
   - Prettier
   - Docker
   - GitLens

2. **Workspace settings** (`.vscode/settings.json`)
   ```json
   {
     "python.pythonPath": "venv/bin/python",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.formatting.provider": "black",
     "editor.formatOnSave": true,
     "editor.codeActionsOnSave": {
       "source.organizeImports": true
     },
     "files.exclude": {
       "**/__pycache__": true,
       "**/*.pyc": true,
       "**/.mypy_cache": true
     }
   }
   ```

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Verify PostgreSQL is running
   - Check `.env` for correct database credentials
   - Run `python manage.py check --database default`

2. **Node.js dependency issues**
   ```bash
   rm -rf node_modules/
   rm package-lock.json
   npm cache clean --force
   npm install
   ```

3. **Python dependency conflicts**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --no-cache-dir
   ```

### Debugging

1. **Django Debug Toolbar**
   - Access at `http://localhost:8000/__debug__/`
   - Shows SQL queries, request/response info, and more

2. **Browser DevTools**
   - Network tab for API requests
   - Console for JavaScript errors
   - React DevTools for component inspection

## Best Practices

### Environment Management

- Never commit sensitive data to version control
- Use `.env` for local development
- Keep `.env.example` updated with all required variables
- Use different settings files for different environments

### Dependency Management

- Pin all dependencies with exact versions
- Update dependencies regularly
- Use `pip-tools` for managing Python dependencies
- Document all major dependency updates

### Development Workflow

1. Create a new branch for each feature/bugfix
2. Write tests for new functionality
3. Run linters and formatters before committing
4. Open a pull request for code review
5. Run all tests before merging to main

## Maintenance

### Keeping Dependencies Updated

```bash
# Update Python dependencies
pip list --outdated
pip install -U package_name

# Update Node.js dependencies
npm outdated
npm update
```

### Database Migrations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check for migration issues
python manage.py check
```

## Support

For additional help, contact:
- **DevOps Team**: devops@example.com
- **Backend Team**: backend@example.com
- **Frontend Team**: frontend@example.com

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0.0 | 2025-07-05 | DevOps Team | Complete environment guide |
| 1.0.0 | 2025-07-04 | System | Initial stub |
