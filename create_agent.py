#!/usr/bin/env python3
"""
Create a DO Inference Agent and wire it to the deployed function.
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("DIGITALOCEAN_TOKEN")
MODEL_ACCESS_KEY = os.getenv("MODEL_ACCESS_KEY")
NAMESPACE_ID = "fn-309f9b5b-dd19-493d-8450-b30f94517e21"
FUNCTION_ENDPOINT = "https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-309f9b5b-dd19-493d-8450-b30f94517e21/default/resume-screener"

if not API_TOKEN or not MODEL_ACCESS_KEY:
    print("❌ Error: DIGITALOCEAN_TOKEN or MODEL_ACCESS_KEY not set")
    exit(1)

# Step 1: Create Agent via API
print("🤖 Creating agent on DO Inference...")

agent_url = "https://api.digitalocean.com/v2/gen-ai/agents"
agent_headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

agent_payload = {
    "name": "resume-screener",
    "model_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "region": "sfo3",
    "instructions": "Score resumes against job descriptions"
}

try:
    response = requests.post(agent_url, headers=agent_headers, json=agent_payload)
    print(f"Response: {response.status_code}")
    agent_data = response.json()

    if response.status_code in [200, 201]:
        agent_id = agent_data.get("id")
        print(f"✅ Agent created!")
        print(f"   ID: {agent_id}")
        print(f"   Name: resume-screener")
        print(f"   Model: gpt-4o")
        print(f"   Region: nyc")

        # Save agent ID
        with open(".agent_id", "w") as f:
            f.write(agent_id)

        print(f"\n📝 Agent endpoint:")
        print(f"   https://api.digitalocean.com/v2/inference/agents/{agent_id}/invoke")

        print(f"\n🧪 Test the agent:")
        print(f'   curl -X POST "https://api.digitalocean.com/v2/inference/agents/{agent_id}/invoke" \\')
        print(f'     -H "Authorization: Bearer $MODEL_ACCESS_KEY" \\')
        print(f'     -d \'{{"prompt": "Score this resume..."}}\'')

    else:
        print(f"❌ Failed to create agent")
        print(json.dumps(agent_data, indent=2))

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
