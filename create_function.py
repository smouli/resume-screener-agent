#!/usr/bin/env python3
"""
Create a function resource in DO Functions namespace.
Run this once before deploying.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

NAMESPACE_ID = "fn-309f9b5b-dd19-493d-8450-b30f94517e21"
API_TOKEN = os.getenv("DIGITALOCEAN_TOKEN")

if not API_TOKEN:
    print("❌ Error: DIGITALOCEAN_TOKEN not set in .env")
    exit(1)

url = f"https://api.digitalocean.com/v2/functions/namespaces/{NAMESPACE_ID}/functions"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "name": "resume_scorer"
}

print("🚀 Creating function resource...")
print(f"   Namespace: {NAMESPACE_ID}")
print(f"   Function: resume_scorer")

response = requests.post(url, headers=headers, json=payload)

print(f"\n📝 Response: {response.status_code}")
print(response.json())

if response.status_code in [200, 201]:
    print("\n✅ Function created!")
    print("Next step: ./scripts/deploy_function.sh")
else:
    print("\n❌ Failed to create function")
    print(response.text)
