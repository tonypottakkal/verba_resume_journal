#!/bin/bash

# Docker Configuration Validation Script
# This script validates the Docker setup for the Local Resume System

set -e

echo "==================================="
echo "Docker Configuration Validation"
echo "==================================="
echo ""

# Check if Docker is installed
echo "1. Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker is installed: $(docker --version)"
echo ""

# Check if Docker Compose is installed
echo "2. Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✅ Docker Compose is installed: $(docker-compose --version)"
echo ""

# Validate docker-compose.yml syntax
echo "3. Validating docker-compose.yml syntax..."
if docker-compose config --quiet 2>&1 | grep -q "ERROR"; then
    echo "❌ docker-compose.yml has syntax errors"
    docker-compose config
    exit 1
fi
echo "✅ docker-compose.yml syntax is valid"
echo ""

# Check if .env.example exists
echo "4. Checking .env.example file..."
if [ ! -f ".env.example" ]; then
    echo "❌ .env.example file not found"
    exit 1
fi
echo "✅ .env.example file exists"
echo ""

# Check if Dockerfile exists
echo "5. Checking Dockerfile..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found"
    exit 1
fi
echo "✅ Dockerfile exists"
echo ""

# Validate required environment variables in .env.example
echo "6. Validating environment variables in .env.example..."
required_vars=(
    "WEAVIATE_URL_VERBA"
    "SKILL_EXTRACTION_MODEL"
    "SKILL_EXTRACTION_PROVIDER"
    "RESUME_GENERATION_MODEL"
    "RESUME_GENERATION_PROVIDER"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if ! grep -q "^$var=" .env.example && ! grep -q "^# $var=" .env.example; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing environment variables in .env.example:"
    printf '   - %s\n' "${missing_vars[@]}"
    exit 1
fi
echo "✅ All required environment variables are present"
echo ""

# Check if volumes are defined in docker-compose.yml
echo "7. Checking volume definitions..."
if ! grep -q "weaviate_data:" docker-compose.yml; then
    echo "❌ weaviate_data volume not defined"
    exit 1
fi
if ! grep -q "resume_exports:" docker-compose.yml; then
    echo "❌ resume_exports volume not defined"
    exit 1
fi
echo "✅ All required volumes are defined"
echo ""

# Check if resume export volume is mounted
echo "8. Checking volume mounts..."
if ! grep -q "resume_exports:/Verba/exports" docker-compose.yml; then
    echo "❌ resume_exports volume not mounted"
    exit 1
fi
echo "✅ Resume export volume is properly mounted"
echo ""

# Check if new environment variables are in docker-compose.yml
echo "9. Checking resume-specific environment variables in docker-compose.yml..."
resume_env_vars=(
    "SKILL_EXTRACTION_MODEL"
    "SKILL_EXTRACTION_PROVIDER"
    "RESUME_GENERATION_MODEL"
    "RESUME_GENERATION_PROVIDER"
)

missing_compose_vars=()
for var in "${resume_env_vars[@]}"; do
    if ! grep -q "$var" docker-compose.yml; then
        missing_compose_vars+=("$var")
    fi
done

if [ ${#missing_compose_vars[@]} -ne 0 ]; then
    echo "❌ Missing environment variables in docker-compose.yml:"
    printf '   - %s\n' "${missing_compose_vars[@]}"
    exit 1
fi
echo "✅ All resume-specific environment variables are in docker-compose.yml"
echo ""

# Check if additional Python dependencies are in Dockerfile
echo "10. Checking additional Python dependencies in Dockerfile..."
if ! grep -q "reportlab" Dockerfile; then
    echo "❌ reportlab dependency not found in Dockerfile"
    exit 1
fi
if ! grep -q "python-docx" Dockerfile; then
    echo "❌ python-docx dependency not found in Dockerfile"
    exit 1
fi
if ! grep -q "markdown" Dockerfile; then
    echo "❌ markdown dependency not found in Dockerfile"
    exit 1
fi
echo "✅ All required Python dependencies are in Dockerfile"
echo ""

# Check if exports directory creation is in Dockerfile
echo "11. Checking exports directory creation..."
if ! grep -q "mkdir -p /Verba/exports" Dockerfile; then
    echo "❌ Exports directory creation not found in Dockerfile"
    exit 1
fi
echo "✅ Exports directory creation is in Dockerfile"
echo ""

echo "==================================="
echo "✅ All validation checks passed!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env: cp .env.example .env"
echo "2. Configure your API keys in .env"
echo "3. Start the services: docker-compose up -d"
echo "4. Access the application at http://localhost:8000"
echo ""
