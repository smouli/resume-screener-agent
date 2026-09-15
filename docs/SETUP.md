# Setup Guide

Complete step-by-step instructions to set up, test, and deploy the resume screener agent.

## Prerequisites

- DigitalOcean account (free tier works)
- `doctl` CLI installed and authenticated
- Python 3.9+
- `pip` or `pip3`
- Git
- Text editor (VS Code, vim, etc.)

### Install doctl (if not already installed)

```bash
# macOS
brew install doctl

# Ubuntu/Debian
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.2/doctl-1.98.2-linux-x86_64.tar.gz
tar xf ~/doctl-1.98.2-linux-x86_64.tar.gz
sudo mv ~/doctl /usr/local/bin

# Windows (Chocolatey)
choco install doctl
```

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/resume-screener-agent.git
cd resume-screener-agent
```

## Step 2: Set Up DigitalOcean Authentication

### Create DO API Token

1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: "resume-screener-agent"
4. Scopes: `write` (needed to create agents and functions)
5. Copy the token (you'll only see it once)

### Create Model Access Key

1. Go to https://cloud.digitalocean.com/account/api/tokens (same page)
2. Scroll to "Model Access Keys"
3. Click "Generate Key"
4. Copy the key

### Authenticate doctl

```bash
doctl auth init

# When prompted:
# - Paste your API Token (the one you created)
# - Choose region (e.g., nyc)
```

## Step 3: Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your keys
nano .env

# Add:
# DIGITALOCEAN_TOKEN=dop_v1_...your token...
# MODEL_ACCESS_KEY=sk_...your key...
```

Load environment:
```bash
source .env
```

Verify authentication:
```bash
doctl account get

# Should show your account info
```

## Step 4: Create Test Data

### Create sample resume
```bash
cat > tests/sample_resume.txt << 'EOF'
JOHN DOE
john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years building scalable backend systems using Python and AWS.

EXPERIENCE
Senior Backend Engineer | TechCorp (2020-Present)
- Led team of 3 engineers on microservices migration (Python, FastAPI)
- Implemented automated testing pipeline (pytest, GitHub Actions)
- Reduced API latency by 40% through optimization

Backend Engineer | StartupXYZ (2018-2020)
- Built REST APIs using Python and Flask
- Managed AWS infrastructure (EC2, RDS, S3)
- Implemented CI/CD pipelines

SKILLS
Languages: Python, JavaScript, SQL
Frameworks: FastAPI, Flask, Django
Cloud: AWS (EC2, RDS, S3, Lambda)
Tools: Git, Docker, pytest
Databases: PostgreSQL, MySQL, Redis

EDUCATION
B.S. Computer Science | University (2018)
EOF
```

### Create sample job description
```bash
cat > tests/sample_job_desc.txt << 'EOF'
Senior Python Engineer

About the Role:
We're looking for an experienced Python engineer to join our backend team. You'll work on our core platform serving millions of users.

Requirements (Required):
- 5+ years of Python experience
- Strong knowledge of REST APIs and microservices
- AWS or cloud platform experience
- Experience with relational databases
- Excellent problem-solving skills

Requirements (Preferred):
- Kubernetes experience
- Machine learning background
- Open source contributions
- Experience leading teams

Responsibilities:
- Design and implement scalable backend systems
- Mentor junior engineers
- Participate in code reviews
- Optimize application performance
- Work with product team on feature prioritization

Compensation:
$150K-$200K + equity + benefits
EOF
```

## Step 5: Deploy the DO Function

```bash
# Make the deployment script executable
chmod +x scripts/deploy_function.sh

# Run it
./scripts/deploy_function.sh

# Expected output:
# Uploading function...
# Function deployed: resume_scorer
# Namespace: default
# Status: ready
```

Verify function deployment:
```bash
doctl serverless function list

# Should show:
# Name              Status   Runtime
# resume_scorer     ready    python
```

## Step 6: Create the Agent

```bash
# Make the agent script executable
chmod +x scripts/create_agent.sh

# Run it
./scripts/create_agent.sh

# Expected output:
# Creating agent: resume-screener
# Model: gpt-4o
# Region: nyc
# Agent ID: abc123...
# Endpoint: https://api.digitalocean.com/v2/inference/agents/abc123.../invoke
```

Save the Agent ID for later:
```bash
# Copy the agent ID and save it
export AGENT_ID="abc123..."  # Replace with actual ID
echo $AGENT_ID > .agent_id
```

## Step 7: Test the Agent

### Option A: Using curl (Command Line)

```bash
AGENT_ID=$(cat .agent_id)

curl -X POST "https://api.digitalocean.com/v2/inference/agents/${AGENT_ID}/invoke" \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Score this resume against the job description.\n\nResume:\n'$(cat tests/sample_resume.txt)'\n\nJob Description:\n'$(cat tests/sample_job_desc.txt)'"
  }' | jq .
```

### Option B: Using Python Script

```bash
python -c "
import requests
import json
import os

agent_id = open('.agent_id').read().strip()
model_key = os.getenv('MODEL_ACCESS_KEY')

resume = open('tests/sample_resume.txt').read()
job_desc = open('tests/sample_job_desc.txt').read()

prompt = f'''Score this resume against the job description on a scale of 0-100.

Resume:
{resume}

Job Description:
{job_desc}

Provide:
1. Score (0-100)
2. Strengths (list of matched requirements)
3. Gaps (missing requirements)
4. Recommendation'''

response = requests.post(
    f'https://api.digitalocean.com/v2/inference/agents/{agent_id}/invoke',
    headers={
        'Authorization': f'Bearer {model_key}',
        'Content-Type': 'application/json'
    },
    json={'prompt': prompt}
)

print(json.dumps(response.json(), indent=2))
"
```

### Expected Response

```json
{
  "id": "msg_123...",
  "object": "message",
  "created_at": "2026-01-20T12:34:56Z",
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Score: 85/100\n\nStrengths:\n- 5+ years Python (required)\n- AWS experience (required)\n- REST API design\n- Team leadership\n\nGaps:\n- No Kubernetes experience\n- No ML background\n\nRecommendation: STRONG MATCH - Recommend for phone screen"
      }
    }
  ]
}
```

## Step 8: Score Your Own Resume

Now it's time to get creative:

```bash
# Create your own resume
cat > tests/my_resume.txt << 'EOF'
[Your actual resume here]
EOF

# Create your target job description
cat > tests/my_target_job.txt << 'EOF'
[Target job description]
EOF

# Score it
AGENT_ID=$(cat .agent_id)
curl -X POST "https://api.digitalocean.com/v2/inference/agents/${AGENT_ID}/invoke" \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Score this resume..."
  }' | jq .
```

## Step 9: Clean Up (Optional)

To delete resources and stop incurring charges:

```bash
# Delete the function
doctl serverless function delete resume_scorer

# Delete the agent
AGENT_ID=$(cat .agent_id)
doctl compute agents delete $AGENT_ID

# Or delete everything via API
```

## Troubleshooting

### "Invalid credentials"
```bash
doctl auth status
# Should show your authenticated account
# If not, run: doctl auth init
```

### "Function not found when called"
```bash
# Check function status
doctl serverless function list
# Function must be "ready" before agent can call it
# Wait 30 seconds and retry
```

### "Agent endpoint returns 401"
```bash
# Check Model Access Key
echo $MODEL_ACCESS_KEY
# Should be non-empty and start with "sk_"

# If not set:
source .env
```

### "Function execution times out"
- Default timeout is 30 seconds
- Scoring logic should be faster than that
- Check function logs: `doctl serverless logs`

### "High costs"
- Check number of API calls: `doctl compute inference metrics`
- Score 1 resume = ~1-2 API calls
- Cost should be ~$0.0002 per resume

## Next Steps

- [DEPLOYMENT.md](DEPLOYMENT.md) — Deploy to production
- [ARCHITECTURE.md](ARCHITECTURE.md) — Understand how it works
- Customize the scoring algorithm in `functions/resume_scorer.py`
- Build a web UI to use it interactively
- Write a blog post about it!

## Questions?

Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details or open an issue on GitHub.
