#!/bin/bash
#
# Local SSL Certificate Setup Script
# Generates self-signed SSL certificates for local HTTPS development
#
# Usage:
#   ./setup-ssl-local.sh
#
# What it does:
#   1. Creates certs/ directory
#   2. Generates 4096-bit RSA self-signed certificate (valid 1 year)
#   3. Verifies certificate files
#   4. Shows certificate details
#   5. Provides next steps

set -e  # Exit on error

echo "========================================="
echo "Local SSL Certificate Setup"
echo "========================================="
echo ""

# Step 1: Create directory
echo "📁 Creating certs directory..."
mkdir -p certs
echo "   ✅ Directory created: certs/"
echo ""

# Step 2: Generate certificate
echo "🔐 Generating self-signed SSL certificate..."
echo "   Key size: 4096-bit RSA"
echo "   Validity: 365 days (1 year)"
echo "   Common Name: localhost"
echo ""

openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost" \
  2>&1 | grep -v "^\.\..*+$" || true

echo ""
echo "   ✅ Certificate generated successfully"
echo ""

# Step 3: Set proper permissions
echo "🔒 Setting file permissions..."
chmod 600 certs/key.pem
chmod 644 certs/cert.pem
echo "   ✅ Permissions set (key: 600, cert: 644)"
echo ""

# Step 4: Verify files
echo "📋 Certificate files:"
ls -lh certs/ | grep -E "cert.pem|key.pem"
echo ""

# Step 5: Show certificate details
echo "📜 Certificate details:"
echo "   Subject: $(openssl x509 -in certs/cert.pem -noout -subject | sed 's/subject=//')"
echo "   Valid from: $(openssl x509 -in certs/cert.pem -noout -startdate | sed 's/notBefore=//')"
echo "   Valid until: $(openssl x509 -in certs/cert.pem -noout -enddate | sed 's/notAfter=//')"
echo ""

# Step 6: Check if vars.py exists
echo "⚙️  Checking vars.py configuration..."
if [ -f "vars.py" ]; then
    if grep -q "SSL_ENABLED.*True" vars.py 2>/dev/null; then
        echo "   ✅ SSL already enabled in vars.py"
    else
        echo "   ⚠️  vars.py exists but SSL not enabled"
        echo ""
        echo "   Add these lines to vars.py:"
        echo ""
        echo "   # SSL/HTTPS Configuration"
        echo "   SSL_ENABLED = True"
        echo "   SSL_CERT_PATH = \"certs/cert.pem\""
        echo "   SSL_KEY_PATH = \"certs/key.pem\""
    fi
else
    echo "   ⚠️  vars.py not found"
    echo "   Copy vars.py.example to vars.py and add SSL settings"
fi
echo ""

echo "========================================="
echo "✅ SSL Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Enable SSL in vars.py (if not already done):"
echo "   SSL_ENABLED = True"
echo "   SSL_CERT_PATH = \"certs/cert.pem\""
echo "   SSL_KEY_PATH = \"certs/key.pem\""
echo ""
echo "2. Start the dashboard:"
echo "   python3 launch-project-ape.py"
echo "   (or double-click launch-project-ape.command on macOS)"
echo ""
echo "3. Access dashboard:"
echo "   https://localhost:8765/configure"
echo ""
echo "4. Accept browser security warning:"
echo "   Click 'Advanced' → 'Proceed to localhost'"
echo "   (Normal for self-signed certificates)"
echo ""
echo "📚 For detailed documentation, see:"
echo "   Docs/SSL_SETUP_LOCAL.md"
echo ""
