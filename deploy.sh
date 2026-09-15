#!/bin/bash
set -e

cd ~/projects/resume-screener-agent

echo "Loading credentials..."
source .env

echo "Setting DO token..."
export DIGITALOCEAN_API_TOKEN=$DIGITALOCEAN_API_TOKEN

echo "Deploying agent..."
gradient agent deploy

echo ""
echo "✅ Deployment complete!"
echo "Test with:"
echo ""
echo "curl -X POST https://agents.do-ai.run/v1/YOUR_AGENT_ID/main/run \\"
echo "  -H 'Authorization: Bearer $DIGITALOCEAN_API_TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"resume_text\":\"test\",\"job_description\":\"test\",\"model_access_key\":\"YOUR_KEY\"}'"
