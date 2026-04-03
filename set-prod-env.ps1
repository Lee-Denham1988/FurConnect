# FurConnect Production Environment Variables Setup Script (PowerShell)
# This script sets environment variables for production deployment

# Generate a strong secret key (or replace with your own)
# You can generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$secretKey = "your-strong-secret-key-here-replace-with-generated-key"

# Set environment variables
[Environment]::SetEnvironmentVariable("DJANGO_SECRET_KEY", $secretKey, "User")
[Environment]::SetEnvironmentVariable("DJANGO_DEBUG", "False", "User")
[Environment]::SetEnvironmentVariable("DJANGO_ALLOWED_HOSTS", "yourdomain.com,www.yourdomain.com", "User")
[Environment]::SetEnvironmentVariable("DJANGO_CSRF_TRUSTED_ORIGINS", "https://yourdomain.com,https://www.yourdomain.com", "User")
[Environment]::SetEnvironmentVariable("DJANGO_CSRF_COOKIE_SECURE", "True", "User")
[Environment]::SetEnvironmentVariable("DJANGO_SESSION_COOKIE_SECURE", "True", "User")
[Environment]::SetEnvironmentVariable("DJANGO_CSRF_COOKIE_HTTPONLY", "True", "User")
[Environment]::SetEnvironmentVariable("DJANGO_SESSION_COOKIE_HTTPONLY", "True", "User")
[Environment]::SetEnvironmentVariable("DJANGO_CSRF_COOKIE_SAMESITE", "Strict", "User")
[Environment]::SetEnvironmentVariable("DJANGO_SESSION_COOKIE_SAMESITE", "Strict", "User")

Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANT: Edit the following in the script before running in production:" -ForegroundColor Yellow
Write-Host "   - DJANGO_SECRET_KEY: Generate a new key with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
Write-Host "   - DJANGO_ALLOWED_HOSTS: Set to your actual domain(s)"
Write-Host "   - DJANGO_CSRF_TRUSTED_ORIGINS: Set to your actual domain(s)"
Write-Host ""
Write-Host "Run this as Administrator for User scope, or System scope for machine-wide." -ForegroundColor Cyan
