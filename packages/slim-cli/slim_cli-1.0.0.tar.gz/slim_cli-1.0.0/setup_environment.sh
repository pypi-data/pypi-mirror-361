#!/bin/bash

# SLIM CLI Environment Setup Script
# This script sets up all dependencies needed to run SLIM CLI and its tests

set -e  # Exit on error

echo "🚀 SLIM CLI Environment Setup"
echo "============================="

# Check if running with proper permissions
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please don't run this script as root/sudo (except for apt commands)"
   echo "   The script will use sudo where needed."
   exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Install system dependencies
echo ""
echo "📦 Step 1: Installing system dependencies..."
echo "This step requires sudo access for apt commands."

if command_exists apt; then
    sudo apt update
    sudo apt install -y python3.12-venv python3-pip python3-dev
    echo "✅ System dependencies installed"
else
    echo "⚠️  This script is designed for Debian/Ubuntu systems with apt."
    echo "   Please install python3-venv and python3-pip manually."
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo "🐍 Step 2: Setting up Python virtual environment..."

if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Step 3: Activate venv and upgrade pip
echo ""
echo "📦 Step 3: Activating environment and upgrading pip..."
source venv/bin/activate
pip install --upgrade pip
echo "✅ Pip upgraded to latest version"

# Step 4: Install project dependencies
echo ""
echo "📚 Step 4: Installing project dependencies..."
pip install -e .
echo "✅ Project dependencies installed"

# Step 5: Install test dependencies
echo ""
echo "🧪 Step 5: Installing test dependencies..."
pip install pytest pytest-cov pytest-mock pytest-asyncio
echo "✅ Test dependencies installed"

# Step 6: Create .env template if it doesn't exist
echo ""
echo "🔐 Step 6: Setting up environment variables..."

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# SLIM CLI Environment Variables
# Uncomment and fill in the API keys for the providers you want to use

# For OpenAI
#OPENAI_API_KEY=your-api-key-here

# For Anthropic  
#ANTHROPIC_API_KEY=your-api-key-here

# For Azure OpenAI
#AZURE_TENANT_ID=your-tenant-id
#AZURE_CLIENT_ID=your-client-id
#AZURE_CLIENT_SECRET=your-client-secret
#API_ENDPOINT=your-endpoint
#API_VERSION=your-version
#APIM_SUBSCRIPTION_KEY=your-key

# For local testing without AI (environment variable has been removed)
EOF
    echo "✅ Created .env template file"
else
    echo "✅ .env file already exists"
fi

# Step 7: Check for Ollama (optional)
echo ""
echo "🤖 Step 7: Checking Ollama installation (optional for local AI)..."

if command_exists ollama; then
    echo "✅ Ollama is installed"
    echo "   To use Ollama, run 'ollama serve' in another terminal"
    echo "   Then pull a model: 'ollama pull llama3.1'"
else
    echo "ℹ️  Ollama not installed. To install:"
    echo "   Visit https://ollama.com for installation instructions"
fi

# Step 8: Verify installation
echo ""
echo "✅ Step 8: Verifying installation..."
echo ""

# Show Python version
python --version

# Show pytest version
python -m pytest --version

# Show installed packages
echo ""
echo "📋 Key installed packages:"
pip list | grep -E "(slim-cli|pytest|litellm|ollama|openai|rich)" || true

# Final instructions
echo ""
echo "✅ Environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure your .env file with API keys (if needed)"
echo "   vim .env"
echo ""
echo "3. Run the tests:"
echo "   # All tests"
echo "   python -m pytest"
echo ""
echo "   # Only AI tests"
echo "   python -m pytest tests/jpl/slim/utils/test_ai_utils.py -v"
echo ""
echo "   # With debug output"
echo "   python -m pytest tests/jpl/slim/utils/test_ai_utils.py -v -s"
echo ""
echo "4. For Ollama support (optional):"
echo "   # Terminal 1:"
echo "   ollama serve"
echo "   # Terminal 2:"
echo "   ollama pull llama3.1"
echo ""
echo "🎉 Happy testing!"