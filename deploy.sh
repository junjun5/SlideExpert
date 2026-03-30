#!/bin/bash
set -e

PROJECT_ID="YOUR_PROJECT_ID"
DISPLAY_NAME="SlideExpert"

echo "========================================================="
echo "🚀 DEPLOYING GOOGLE SLIDE AGENT TO VERTEX AI"
echo "========================================================="

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "🔧 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# Sync dependencies
echo "📦 Syncing dependencies..."
uv sync

# Deploy to Agent Engine (Reasoning Engine)
echo "🤖 Step 1/2: Deploying to Vertex AI Agent Engine..."
make deploy

# Register to Gemini Enterprise
echo ""
echo "🤖 Step 2/2: Registering Agent to Gemini Enterprise..."
echo "Note: This part is interactive. Please follow the prompts."
make register-gemini-enterprise

echo ""
echo "========================================================="
echo "🎉 Deployment & Registration Process Initiated!"
echo "========================================================="
echo "Check your Google Cloud Console for status:"
echo "https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=$PROJECT_ID"
echo "========================================================="
