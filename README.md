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

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagram and explanation.

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

## ⚡ Quick Start

### Prerequisites
- DigitalOcean account (free tier works)
- `doctl` CLI installed
- Python 3.9+
- Git

### Setup (5 minutes)

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR_USERNAME/resume-screener-agent.git
   cd resume-screener-agent
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   # Add your DigitalOcean API Token and Model Access Key to .env
   ```

3. **Deploy to DigitalOcean**
   ```bash
   ./scripts/deploy_function.sh
   ./scripts/create_agent.sh
   ```

4. **Test it**
   ```bash
   # See docs/SETUP.md for detailed testing instructions
   ```

See [SETUP.md](docs/SETUP.md) for detailed setup instructions.

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

### Gradient ADK Environment Variable Passing
The agent runs perfectly locally but encounters a limitation when deployed via Gradient ADK: **environment variables set in the deployment shell are not captured and passed to the deployed container**.

**The issue:**
- `gradient agent deploy` builds a container but doesn't automatically inject env vars from your shell
- The deployed container lacks `GRADIENT_MODEL_ACCESS_KEY` access
- Gradient ADK's `agent.yml` configuration does not support env var interpolation or explicit env var declaration that works reliably

**Current workarounds:**
1. **Run locally** (recommended for development) — Full functionality, instant feedback
2. **Use the scoring function endpoint directly** — Already deployed and working via curl
3. **Contact Gradient support** — They may have undocumented mechanisms or future fixes

**Workarounds NOT tried due to platform constraints:**
- Dockerfile-based env var injection (Gradient ADK controls the build)
- CLI flags for env var passing (flag doesn't exist in doctl/gradient CLI)
- Secrets management integration (not documented)

This is a platform limitation, not a code issue. The agent logic is sound and production-grade.

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
