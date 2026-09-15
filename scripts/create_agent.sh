#!/bin/bash

# Create resume-screener agent on DigitalOcean Inference
# Usage: ./scripts/create_agent.sh

set -e

echo "🤖 Creating resume-screener agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found. Copy .env.example and fill in your credentials."
    exit 1
fi

# Load environment
source .env

# Check required variables
if [ -z "$DIGITALOCEAN_TOKEN" ]; then
    echo "❌ Error: DIGITALOCEAN_TOKEN not set"
    exit 1
fi

AGENT_NAME=${AGENT_NAME:-resume-screener}
REGION=${AGENT_REGION:-nyc}
MODEL=${AGENT_MODEL:-gpt-4o}
NAMESPACE=${FUNCTION_NAMESPACE:-default}

echo "📋 Configuration:"
echo "   Agent Name: $AGENT_NAME"
echo "   Model: $MODEL"
echo "   Region: $REGION"
echo "   Function Namespace: $NAMESPACE"

# Agent system instructions
read -r -d '' INSTRUCTIONS << 'EOF' || true
You are a professional resume screener. Your job is to score resumes against job descriptions.

You have access to a scoring function that provides detailed analysis. Use it to:
1. Score resumes on a scale of 0-100
2. Identify key strengths that match the job
3. Identify gaps where the candidate lacks experience
4. Provide recommendations for hiring teams

Always be fair but honest in your assessment. Provide reasoning for your score.

When scoring, consider:
- Required vs preferred qualifications
- Years of relevant experience
- Technical skills match
- Soft skills indicators
- Industry experience

After getting the score from the function, synthesize it into a human-readable recommendation.
EOF

echo "⏳ Creating agent..."

# Create the agent using DO API
AGENT_RESPONSE=$(curl -s -X POST "https://api.digitalocean.com/v2/gen-ai/agents" \
    -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"$AGENT_NAME\",
        \"model\": \"$MODEL\",
        \"system_prompt\": \"$INSTRUCTIONS\",
        \"region\": \"$REGION\"
    }")

# Extract agent ID
AGENT_ID=$(echo $AGENT_RESPONSE | jq -r '.id')

if [ -z "$AGENT_ID" ] || [ "$AGENT_ID" == "null" ]; then
    echo "❌ Failed to create agent"
    echo $AGENT_RESPONSE | jq .
    exit 1
fi

echo "✅ Agent created!"
echo ""
echo "📝 Agent Details:"
echo "   ID: $AGENT_ID"
echo "   Name: $AGENT_NAME"
echo "   Model: $MODEL"
echo "   Endpoint: https://api.digitalocean.com/v2/inference/agents/$AGENT_ID/invoke"
echo ""
echo "💾 Saving agent ID to .agent_id..."
echo "$AGENT_ID" > .agent_id

echo ""
echo "📚 Next steps:"
echo "   1. Add function route: see docs/SETUP.md"
echo "   2. Test the agent: see docs/SETUP.md"
echo ""
echo "🔗 Agent endpoint:"
echo "   https://api.digitalocean.com/v2/inference/agents/$AGENT_ID/invoke"
echo ""
echo "🧪 Test with curl:"
echo "   curl -X POST \"https://api.digitalocean.com/v2/inference/agents/$AGENT_ID/invoke\" \\"
echo "     -H \"Authorization: Bearer \$MODEL_ACCESS_KEY\" \\"
echo "     -d '{\"prompt\": \"Score this resume...\"}'"
echo ""
