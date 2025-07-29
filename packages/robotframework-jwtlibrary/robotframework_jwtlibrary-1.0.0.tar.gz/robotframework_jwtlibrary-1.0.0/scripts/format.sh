#!/bin/bash
# scripts/format.sh
# Code formatting script for JWT Robot Framework Library

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_status "Formatting code..."

# Format code with Black
print_status "Running Black formatter..."
black src tests
print_success "Black formatting completed"

# Sort imports with isort
print_status "Sorting imports with isort..."
isort src tests
print_success "Import sorting completed"

print_success "Code formatting completed! ✨"
