#!/bin/bash

# ==============================================================================
# Railway Configuration Setup Script
# ==============================================================================
# Quickly configure all required environment variables for Railway deployment
#
# Usage: ./setup-railway-config.sh
# ==============================================================================

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
print_header() {
  echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

print_step() {
  echo -e "${GREEN}→${NC} $1"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

# Check if railway CLI is installed
check_railway() {
  if ! command -v railway &> /dev/null; then
    print_error "Railway CLI not found"
    echo "Install with: npm install -g @railway/cli"
    exit 1
  fi
  print_success "Railway CLI found"
}

# Check if logged in
check_login() {
  if ! railway whoami &> /dev/null 2>&1; then
    print_error "Not logged in to Railway"
    print_step "Running: railway login"
    railway login
  fi
  print_success "Railway authenticated"
}

# Set required variables
set_required_variables() {
  print_header "Setting Required Variables"
  
  # ANTHROPIC_API_KEY
  read -p "Enter your Anthropic API Key (sk-ant-...): " API_KEY
  if [ -n "$API_KEY" ]; then
    railway variable set ANTHROPIC_API_KEY "$API_KEY"
    print_success "ANTHROPIC_API_KEY set"
  else
    print_error "ANTHROPIC_API_KEY is required"
    exit 1
  fi
  
  # NEO4J_PASSWORD
  read -sp "Enter Neo4j Password: " NEO4J_PASS
  echo
  if [ -n "$NEO4J_PASS" ]; then
    railway variable set NEO4J_PASSWORD "$NEO4J_PASS"
    print_success "NEO4J_PASSWORD set"
  else
    print_error "NEO4J_PASSWORD is required"
    exit 1
  fi
  
  echo ""
}

# Set optional variables
set_optional_variables() {
  print_header "Setting Optional Variables"
  
  # OLLAMA_BASE_URL
  read -p "Ollama Base URL (optional, default: http://localhost:11434): " OLLAMA_URL
  OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
  railway variable set OLLAMA_BASE_URL "$OLLAMA_URL"
  print_success "OLLAMA_BASE_URL set to: $OLLAMA_URL"
  
  # DATABASE_URL
  read -p "PostgreSQL Database URL (optional): " DB_URL
  if [ -n "$DB_URL" ]; then
    railway variable set DATABASE_URL "$DB_URL"
    print_success "DATABASE_URL set"
  else
    print_warning "DATABASE_URL not set (optional)"
  fi
  
  echo ""
}

# Verify settings
verify_settings() {
  print_header "Verifying Configuration"
  
  echo "Current Railway Variables:"
  echo ""
  railway variable list
  echo ""
  
  # Count variables
  count=$(railway variable list 2>/dev/null | wc -l)
  if [ "$count" -gt 2 ]; then
    print_success "Variables successfully configured"
  else
    print_error "Variable configuration may have failed"
    exit 1
  fi
}

# Redeploy
redeploy() {
  print_header "Redeploying Service"
  
  read -p "Redeploy service now? (y/n): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Redeploying..."
    railway redeploy
    print_success "Deployment initiated"
    
    echo ""
    print_step "Waiting for service to start (30 seconds)..."
    sleep 30
    
    print_step "Checking status..."
    railway logs --tail 20
  else
    print_warning "Manual redeploy required: railway redeploy"
  fi
}

# Test deployment
test_deployment() {
  print_header "Testing Deployment"
  
  echo "Getting your Railway domain..."
  domain=$(railway domains 2>/dev/null | grep -oP 'https?://\S+' | head -1 || echo "unknown")
  
  if [ "$domain" != "unknown" ]; then
    echo "Testing health endpoint: $domain/system/health"
    echo ""
    
    # Wait a bit for service to be ready
    sleep 5
    
    curl -s "$domain/system/health" | head -20 || echo "Service still starting..."
  else
    print_warning "Could not determine Railway domain"
    print_step "Check: railway open"
  fi
  
  echo ""
}

# Main execution
main() {
  print_header "Railway Configuration Setup"
  
  check_railway
  check_login
  
  # Show current variables
  echo ""
  echo "Current variables:"
  railway variable list 2>/dev/null | head -5 || echo "(none yet)"
  echo ""
  
  read -p "Configure Railway environment variables now? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Setup cancelled"
    exit 0
  fi
  
  echo ""
  set_required_variables
  set_optional_variables
  verify_settings
  redeploy
  test_deployment
  
  echo ""
  print_header "Setup Complete!"
  echo ""
  echo "Your deployment is configured and running."
  echo ""
  echo "Useful commands:"
  echo "  • View logs:     railway logs --follow"
  echo "  • Check status:  railway status"
  echo "  • Open in browser: railway open"
  echo "  • Redeploy:      railway redeploy"
  echo "  • View variables: railway variable list"
  echo ""
}

main
