# Resume Screener Agent

An AI-powered resume screening agent built with DigitalOcean's serverless infrastructure. Automatically scores resumes against job descriptions using intelligent analysis and detailed reasoning.

## 🚀 Quick Overview

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

## 🏗️ Architecture

```
Your App → DO Inference Agent → DO Function → Score & Analysis
```

**How credentials work:**
- Client sends `model_access_key` in request body
- Agent uses it to call Gradient LLM API
- Simple for demos, secure backends recommended for production

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams, credential handling strategies, and production recommendations.

## 📋 Features

- ✅ **Intelligent Scoring** — ML-powered resume analysis
- ✅ **Detailed Reasoning** — Explains why a resume scored as it did
- ✅ **Keyword Matching** — Identifies required vs missing skills
- ✅ **Experience Analysis** — Evaluates relevant experience
- ✅ **Serverless** — No infrastructure to manage
- ✅ **Production-Ready** — Can handle real use cases

## 🎯 Use Cases

- **Recruiting teams** — Screen hundreds of resumes automatically
- **Job portals** — Show applicants their match score
- **Career coaching** — Help candidates improve their resumes
- **Learning projects** — Understand agentic AI architecture

## ⚡ Quick Start (Local)

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

## 📖 Documentation

- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) — How it works, diagrams, component breakdown
- [**SETUP.md**](docs/SETUP.md) — Step-by-step setup and testing
- [**DEPLOYMENT.md**](docs/DEPLOYMENT.md) — Deploy to DigitalOcean
- [**API.md**](docs/API.md) — Agent endpoint documentation

## 🧪 Testing

```bash
# Test the scoring function
python -m pytest tests/

# Test the agent endpoint (after deployment)
curl -X POST https://api.digitalocean.com/v2/inference/agents/{agent_id}/invoke \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -d '{"prompt": "Score this resume: ..."}'
```

## 📊 Example Response

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

## ⚠️ Known Limitations

### Gradient ADK Deployment
The agent works **perfectly locally** ✅ but has limitations when deployed via Gradient ADK's serverless platform.

**What works locally:**
- ✅ Full agent functionality
- ✅ LLM analysis generation
- ✅ All external API calls
- ✅ Pass credentials via request payload

**What doesn't work on Gradient ADK:**
- ❌ Deployed agent can't reach external APIs (network restriction)
- ❌ Environment variables not passed to containers
- ❌ ADK agents can't be configured with secrets via UI
- ❌ No documented secrets management for deployed agents

**Why:** Gradient ADK appears designed for self-contained agents (with built-in tools) rather than agents calling external APIs. Its deployed environment has network restrictions that block outbound API calls.

**Solution:** The agent is fully functional when run **locally** using `gradient agent run`. For a production deployment that calls external LLM APIs, use platforms with unrestricted network access (AWS Lambda, Railway, Render, etc.).

**What IS deployed and working:**
- ✅ Scoring function on DO Functions (live endpoint)
- ✅ Agent code on GitHub (ready to deploy elsewhere)

## 💡 Key Insights

This project teaches:

1. **Agentic Patterns** — How agents use function routing to execute logic
2. **Serverless Architecture** — Building scalable systems without VMs
3. **DO Infrastructure** — Function routing, Inference, API orchestration
4. **AI/ML Integration** — Scoring algorithms, prompt engineering
5. **Production Workflows** — From local testing to deployed agents
6. **Deployment Challenges** — Understanding platform limitations and workarounds

## 🛠️ Built With

- **Framework:** OpenAI SDK (via DO Inference)
- **Infrastructure:** DigitalOcean Serverless
- **Language:** Python
- **Deployment:** doctl CLI

## 📝 Blog Post

See the accompanying article: "Building an AI Resume Screener with DigitalOcean Serverless Inference" (coming soon)

## 🤝 Contributing

Contributions welcome! Check [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🚀 Next Steps

1. [Set up locally](docs/SETUP.md)
2. [Deploy to DigitalOcean](docs/DEPLOYMENT.md)
3. [Score your own resume](docs/SETUP.md#testing)
4. Share your results!

---

**Questions?** Open an issue or see the docs for more details.

**Want to contribute?** Fork, improve, and submit a PR!
