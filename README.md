# Resume Screener Agent

An AI-powered resume screening agent built with DigitalOcean's serverless infrastructure. Automatically scores resumes against job descriptions using intelligent analysis and detailed reasoning.

## Quick Overview

**What it does:**
- Takes a resume and job description as input
- Scores the resume (0-100) against the job requirements
- Provides detailed analysis of strengths and gaps
- Uses function routing to execute scoring logic on DO Functions
- All serverless, no servers to manage

**Tech Stack:**
- **Agent:** DigitalOcean Serverless Inference (GPT-4o)
- **Compute:** DigitalOcean Functions (scoring logic)
- **Orchestration:** DO Function Routing
- **Infrastructure:** Fully serverless

**Cost:** ~$1-3 per 100 resumes scored

## Architecture

```
Your App → DO Inference Agent → DO Function → Score & Analysis
```

**How credentials work:**
- Client sends `model_access_key` in request body
- Agent uses it to call Gradient LLM API
- Simple for demos, secure backends recommended for production

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams, credential handling strategies, and production recommendations.

## Features

- **Intelligent Scoring** — ML-powered resume analysis
- **Detailed Reasoning** — Explains why a resume scored as it did
- **Keyword Matching** — Identifies required vs missing skills
- **Experience Analysis** — Evaluates relevant experience
- **Serverless** — No infrastructure to manage
- **Production-Ready** — Can handle real use cases

## Use Cases

- **Recruiting teams** — Screen hundreds of resumes automatically
- **Job portals** — Show applicants their match score
- **Career coaching** — Help candidates improve their resumes
- **Learning projects** — Understand agentic AI architecture

## Quick Start (Local)

### Prerequisites
- Python 3.10+
- Git
- DigitalOcean API credentials (optional, for deployed scoring function)

### Setup (2 minutes)

1. **Clone and install**
   ```bash
   git clone https://github.com/smouli/resume-screener-agent.git
   cd resume-screener-agent
   pip install -r requirements.txt
   ```

2. **Set your credentials**
   ```bash
   export MODEL_ACCESS_KEY="your_gradient_model_access_key"
   ```

3. **Run the agent**
   ```bash
   gradient agent run
   ```

4. **Test it (in another terminal)**
   ```bash
   curl -X POST http://localhost:8080/run \
     -H "Content-Type: application/json" \
     -d '{
       "resume_text": "Python engineer, 5 years AWS, FastAPI",
       "job_description": "Senior Python - Required: Python, AWS",
       "model_access_key": "your_gradient_model_access_key"
     }'
   ```

### Full Setup
See [SETUP.md](docs/SETUP.md) for deployment and advanced configuration.

## Documentation

- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) — How it works, credential handling, production strategies
- [**GRADIENT_ADK_NOTES.md**](docs/GRADIENT_ADK_NOTES.md) — Platform investigation and findings
- [**SETUP.md**](docs/SETUP.md) — Local setup and testing
- [**DEPLOYMENT.md**](docs/DEPLOYMENT.md) — Deploy to DigitalOcean Gradient ADK

## Testing

```bash
# Test the scoring function
python -m pytest tests/

# Test the agent endpoint (after deployment)
curl -X POST https://api.digitalocean.com/v2/inference/agents/{agent_id}/invoke \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -d '{"prompt": "Score this resume: ..."}'
```

## Example Response

```json
{
  "score": 85,
  "match_percentage": "85%",
  "strengths": [
    "5+ years of Python experience (required)",
    "AWS/Cloud expertise matches job requirements",
    "Leadership experience in cross-functional teams"
  ],
  "gaps": [
    "No Kubernetes experience (preferred, not required)",
    "Limited ML/AI background"
  ],
  "reasoning": "Strong candidate with deep backend experience and proven track record. Missing some preferred qualifications but core requirements are met.",
  "recommendation": "STRONG MATCH - Recommend for phone screen"
}
```

## Issues I Faced

### Gradient ADK Secrets Management
The agent works perfectly locally but I hit a wall trying to deploy it on Gradient ADK's serverless platform.

**The Problem:**
I wanted the deployed agent to call Gradient's LLM API, but Gradient ADK doesn't support passing secrets/environment variables to deployed agents. I tried everything:
- Environment variables (doesn't capture them from shell)
- Config files (no support in agent.yml)
- UI secrets panel (designed for something else entirely)
- Hardcoding (GitHub blocks it immediately)

**Why It Happens:**
Gradient ADK is designed for self-contained agents with built-in tools (file access, bash, etc.), not agents that call external APIs. The deployed environment has network restrictions that block outbound API calls anyway.

**My Solution:**
Clients pass the `model_access_key` in the request payload. It's simple and works great for demos and internal use. For a public product, you'd want a backend proxy to keep credentials secure server-side.

**What's Actually Deployed:**
- Scoring function on DO Functions (live and working)
- Agent code on GitHub (ready to deploy elsewhere when needed)

## Key Insights

This project teaches:

1. **Agentic Patterns** — How agents use function routing to execute logic
2. **Serverless Architecture** — Building scalable systems without VMs
3. **DO Infrastructure** — Function routing, Inference, API orchestration
4. **AI/ML Integration** — Scoring algorithms, prompt engineering
5. **Production Workflows** — From local testing to deployed agents
6. **Deployment Challenges** — Understanding platform limitations and workarounds

## Built With

- **Framework:** Gradient SDK (via DO Inference)
- **Infrastructure:** DigitalOcean Serverless
- **Language:** Python
- **Deployment:** doctl CLI + Gradient Agent SDK

## License

MIT License - see [LICENSE](LICENSE)
