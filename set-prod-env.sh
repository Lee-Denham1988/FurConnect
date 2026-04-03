#!/bin/bash
# FurConnect Production Environment Variables Setup Script (Bash)
# This script sets environment variables for production deployment on Linux/Mac

# Generate a strong secret key (or replace with your own)
# You can generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

DJANGO_SECRET_KEY="your-strong-secret-key-here-replace-with-generated-key"
DJANGO_DEBUG="False"
DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
DJANGO_CSRF_TRUSTED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
DJANGO_CSRF_COOKIE_SECURE="True"
DJANGO_SESSION_COOKIE_SECURE="True"
DJANGO_CSRF_COOKIE_HTTPONLY="True"
DJANGO_SESSION_COOKIE_HTTPONLY="True"
DJANGO_CSRF_COOKIE_SAMESITE="Strict"
DJANGO_SESSION_COOKIE_SAMESITE="Strict"

# Option 1: Export to current session only
export DJANGO_SECRET_KEY
export DJANGO_DEBUG
export DJANGO_ALLOWED_HOSTS
export DJANGO_CSRF_TRUSTED_ORIGINS
export DJANGO_CSRF_COOKIE_SECURE
export DJANGO_SESSION_COOKIE_SECURE
export DJANGO_CSRF_COOKIE_HTTPONLY
export DJANGO_SESSION_COOKIE_HTTPONLY
export DJANGO_CSRF_COOKIE_SAMESITE
export DJANGO_SESSION_COOKIE_SAMESITE

echo "✅ Environment variables exported for this session"
echo ""
echo "⚠️  IMPORTANT: Do one of the following for persistence:"
echo ""
echo "Option 1: Add to ~/.bashrc (Linux/Mac):"
echo "  cat >> ~/.bashrc << 'EOF'"
echo "  export DJANGO_SECRET_KEY='$DJANGO_SECRET_KEY'"
echo "  export DJANGO_DEBUG='False'"
echo "  export DJANGO_ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'"
echo "  export DJANGO_CSRF_TRUSTED_ORIGINS='https://yourdomain.com,https://www.yourdomain.com'"
echo "  export DJANGO_CSRF_COOKIE_SECURE='True'"
echo "  export DJANGO_SESSION_COOKIE_SECURE='True'"
echo "  EOF"
echo "  source ~/.bashrc"
echo ""
echo "Option 2: Add to /etc/environment (system-wide, requires sudo):"
echo "  sudo tee -a /etc/environment > /dev/null << 'EOF'"
echo "  DJANGO_SECRET_KEY='$DJANGO_SECRET_KEY'"
echo "  DJANGO_DEBUG='False'"
echo "  etc..."
echo "  EOF"
echo ""
echo "Option 3: Use a .env file with python-dotenv package:"
echo "  pip install python-dotenv"
echo "  Create .env file with variables"
echo ""
echo "MUST EDIT:"
echo "  - DJANGO_SECRET_KEY: Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
echo "  - DJANGO_ALLOWED_HOSTS: Set to your actual domain(s)"
echo "  - DJANGO_CSRF_TRUSTED_ORIGINS: Set to your actual domain(s)"
