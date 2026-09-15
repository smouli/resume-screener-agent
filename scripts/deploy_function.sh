#!/bin/bash

# Deploy resume_scorer function to DigitalOcean Functions
# Usage: ./scripts/deploy_function.sh

set -e

echo "🚀 Deploying resume_scorer function..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Copy .env.example and fill in your credentials."
    exit 1
fi

# Load environment
source .env

# Check if FUNCTION_NAMESPACE is set
NAMESPACE=${FUNCTION_NAMESPACE:-fn-309f9b5b-dd19-493d-8450-b30f94517e21}
REGION=${FUNCTION_REGION:-nyc}

echo "📦 Configuration:"
echo "   Namespace: $NAMESPACE"
echo "   Region: $REGION"
echo "   Function: resume_scorer"

# Deploy the function from root
echo "⏳ Deploying..."
cd ..
doctl serverless deploy .

echo ""
echo "✅ Deployment successful!"
echo ""
echo "📝 Verify deployment:"
echo "   doctl serverless function list"
echo ""
echo "🧪 Test the function:"
echo "   doctl serverless invoke resume_scorer -- '{\"resume_text\": \"...\", \"job_description\": \"...\"}'"
echo ""
