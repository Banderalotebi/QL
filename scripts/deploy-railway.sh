#!/bin/bash

# ==============================================================================
# Railway Deployment Script for Muqattaat Cryptanalytic Lab
# ==============================================================================
# Deploy the entire system to Railway with proper configuration
# 
# Prerequisites:
#   - Railway account: https://railway.app
#   - Railway CLI installed: npm install -g @railway/cli
#   - Git repository pushed to GitHub
#   - Required environment variables configured in Railway dashboard
#
# Usage:
#   ./scripts/deploy-railway.sh [options]
#
# Options:
#   --project <name>    Railway project name (default: muqattaat-lab)
#   --env <name>        Environment name (default: production)
#   --dry-run           Show what would be deployed without actually deploying
#   --setup-env         Only setup environment variables, don't deploy
#   --logs              Show deployment logs
#   --help              Show this help message
# ==============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="${PROJECT_NAME:-muqattaat-lab}"
ENVIRONMENT="${ENVIRONMENT:-production}"
DRY_RUN=false
SETUP_ENV_ONLY=false
SHOW_LOGS=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --project)
      PROJECT_NAME="$2"
      shift 2
      ;;
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --setup-env)
      SETUP_ENV_ONLY=true
      shift
      ;;
    --logs)
      SHOW_LOGS=true
      shift
      ;;
    --help)
      head -20 "$0" | tail -19
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Helper functions
print_header() {
  echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC} $1"
  echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
}

print_step() {
  echo -e "${GREEN}→${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

# Check prerequisites
check_prerequisites() {
  print_header "Checking Prerequisites"
  
  # Check Railway CLI
  if ! command -v railway &> /dev/null; then
    print_error "Railway CLI not found"
    echo "Install with: npm install -g @railway/cli"
    exit 1
  fi
  print_success "Railway CLI found"
  
  # Check if logged in to Railway
  if ! railway whoami &> /dev/null 2>&1; then
    print_warning "Not logged in to Railway"
    print_step "Running: railway login"
    railway login
  fi
  print_success "Railway authenticated"
  
  # Check if git is clean
  if [[ -n $(git -C "$ROOT_DIR" status -s) ]]; then
    print_warning "Git working directory not clean"
    print_step "Uncommitted changes will not be deployed"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi
  fi
  
  # Check Docker is accessible (for local testing)
  if ! command -v docker &> /dev/null; then
    print_warning "Docker not found (optional for local testing)"
  else
    print_success "Docker found"
  fi
  
  echo ""
}

# Setup environment variables
setup_environment() {
  print_header "Configuring Environment Variables"
  
  # Read required secrets from .env or user input
  read -p "Anthropic API Key (ANTHROPIC_API_KEY): " ANTHROPIC_API_KEY
  read -p "Neo4j Password (NEO4J_PASSWORD): " NEO4J_PASSWORD
  read -p "Database URL (DATABASE_URL) [optional]: " DATABASE_URL
  read -p "Ollama Base URL (OLLAMA_BASE_URL) [http://localhost:11434]: " OLLAMA_BASE_URL
  OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
  
  print_step "Setting Railway environment variables..."
  
  if [ "$DRY_RUN" = false ]; then
    railway variable set ANTHROPIC_API_KEY "$ANTHROPIC_API_KEY" -e "$ENVIRONMENT"
    railway variable set NEO4J_PASSWORD "$NEO4J_PASSWORD" -e "$ENVIRONMENT"
    
    if [ -n "$DATABASE_URL" ]; then
      railway variable set DATABASE_URL "$DATABASE_URL" -e "$ENVIRONMENT"
    fi
    
    railway variable set OLLAMA_BASE_URL "$OLLAMA_BASE_URL" -e "$ENVIRONMENT"
    
    print_success "Environment variables configured"
  else
    echo "Would set: ANTHROPIC_API_KEY, NEO4J_PASSWORD, OLLAMA_BASE_URL"
  fi
  
  echo ""
}

# Test deployment locally
test_local_deployment() {
  print_header "Testing Local Deployment"
  
  if ! command -v docker &> /dev/null; then
    print_warning "Docker not available, skipping local test"
    return
  fi
  
  print_step "Building Docker image..."
  if [ "$DRY_RUN" = false ]; then
    docker build -t muqattaat-lab:test -f "$ROOT_DIR/Dockerfile" "$ROOT_DIR"
    print_success "Docker image built"
    
    print_step "Testing image..."
    docker run --rm muqattaat-lab:test python -c "import src.agents.hive_council; print('✓ Imports OK')"
    print_success "Local test passed"
  else
    echo "Would build and test Docker image"
  fi
  
  echo ""
}

# Deploy to Railway
deploy_to_railway() {
  print_header "Deploying to Railway"
  
  if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN: Would execute the following commands:"
    echo "  railway source connect"
    echo "  railway deploy --projectID <id> --environmentName $ENVIRONMENT"
    echo ""
    return
  fi
  
  print_step "Linking to Railway project: $PROJECT_NAME"
  railway link -p "$PROJECT_NAME" -e "$ENVIRONMENT" || true
  
  print_step "Deploying to Railway..."
  railway deploy
  
  print_success "Deployment initiated"
  
  if [ "$SHOW_LOGS" = true ]; then
    echo ""
    print_step "Fetching deployment logs..."
    sleep 5
    railway logs --tail 100
  fi
  
  echo ""
}

# Get deployment info
get_deployment_info() {
  print_header "Deployment Information"
  
  print_step "Getting Railway domains..."
  railway domain list || echo "Use Railway dashboard to view domains"
  
  print_step "Getting deployment status..."
  railway status || echo "Use Railway dashboard to view status"
  
  echo ""
  echo -e "${GREEN}Deployment Complete!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Check Railway dashboard: https://railway.app"
  echo "  2. Monitor logs: railway logs --tail 100"
  echo "  3. Test health: curl https://your-domain/system/health"
  echo "  4. View dashboard: https://your-domain:8501"
  echo ""
}

# Main execution
main() {
  print_header "Railway Deployment Script - Muqattaat Lab"
  echo "Project: $PROJECT_NAME"
  echo "Environment: $ENVIRONMENT"
  echo ""
  
  check_prerequisites
  
  if [ "$SETUP_ENV_ONLY" = true ]; then
    setup_environment
    print_success "Environment configured"
    exit 0
  fi
  
  # Confirm deployment
  if [ "$DRY_RUN" = false ]; then
    echo "Ready to deploy to Railway"
    echo ""
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      print_warning "Deployment cancelled"
      exit 0
    fi
  fi
  
  setup_environment
  test_local_deployment
  deploy_to_railway
  get_deployment_info
}

# Run main
main
