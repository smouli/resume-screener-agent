# Deployment Guide

Instructions for deploying the resume screener agent to production.

## Prerequisites

- Completed [SETUP.md](SETUP.md)
- Agent and function deployed locally and tested
- DigitalOcean account with sufficient credits/billing

## Production Considerations

### Scaling

**Current Setup:** On-demand serverless
- Agents spin up when called
- Auto-scales with traffic
- Best for: Variable traffic, cost-conscious

**High-Volume Alternative:** Dedicated Inference
- Agent runs 24/7
- Lower latency per request
- Best for: Consistent high traffic (1000+ req/day)

### Monitoring

Monitor these metrics in DO Console:

1. **Inference API Calls** — How many requests
2. **Model Tokens** — Input/output token usage
3. **Function Invocations** — How many times function runs
4. **Error Rate** — Percentage of failed requests

### Costs

| Volume | Approx Monthly Cost |
|--------|---------------------|
| 100 resumes/month | $0.02 |
| 1,000 resumes/month | $0.20 |
| 10,000 resumes/month | $2.00 |
| 100,000 resumes/month | $20.00 |

## Deployment Checklist

- [ ] Tested locally with multiple resumes
- [ ] No API keys hardcoded in code
- [ ] Environment variables configured
- [ ] Function executes in < 30 seconds
- [ ] Agent endpoint returns valid JSON
- [ ] Error handling in place
- [ ] Costs understood
- [ ] Monitoring set up

## Production Deployment

### 1. Set Up Production Environment Variables

```bash
# Create separate .env.production
cp .env.example .env.production

# Edit with production settings
nano .env.production

# Key differences:
# - Same API token and model key
# - Can add different function namespace if needed
# - Consider enabling logging
```

### 2. Deploy Production Function

```bash
FUNCTION_NAMESPACE=resume-screener-prod
doctl serverless deploy functions/resume_scorer.py \
  --namespace $FUNCTION_NAMESPACE
```

### 3. Create Production Agent

```bash
doctl gradient agent create \
  --name "resume-screener-prod" \
  --model gpt-4o \
  --region nyc \
  --instructions "You are a professional resume screener..."
```

### 4. Set Up Monitoring

```bash
# Monitor function execution
doctl serverless logs --tail

# Monitor inference usage
doctl compute inference metrics

# Set up alerts in DO Console if needed
```

### 5. Document the Endpoint

Save your production endpoint:

```bash
# Create deployment info file
cat > DEPLOYMENT_INFO.md << 'EOF'
# Production Deployment

Agent ID: abc123...
Endpoint: https://api.digitalocean.com/v2/inference/agents/abc123.../invoke
Deployed: 2026-01-20
Last Updated: 2026-01-20

Model Access Key: (stored in DO Console - do not commit)
API Token: (stored in DO Console - do not commit)

Status: LIVE

## Monitoring

- Function invocations: ~X per day
- Average cost: ~$X per month
- Average response time: ~2-3 seconds

## Rollback Plan

If production breaks:
1. Revert to previous function version
2. Check logs: `doctl serverless logs`
3. Update function and redeploy
4. Test with sample resume before re-enabling
EOF

git add DEPLOYMENT_INFO.md
git commit -m "docs: add deployment info"
```

## Integration Options

### Option 1: Direct API Calls (Simple)

```python
import requests

def score_resume(resume_text, job_description):
    response = requests.post(
        f"https://api.digitalocean.com/v2/inference/agents/{AGENT_ID}/invoke",
        headers={
            "Authorization": f"Bearer {MODEL_ACCESS_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": f"Score this resume: {resume_text}\n\nJob: {job_description}"
        }
    )
    return response.json()
```

### Option 2: Web API (REST)

Wrap the agent in a simple API:

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/score", methods=["POST"])
def score_resume():
    resume = request.json.get("resume")
    job_desc = request.json.get("job_description")
    
    response = requests.post(
        f"https://api.digitalocean.com/v2/inference/agents/{AGENT_ID}/invoke",
        headers={
            "Authorization": f"Bearer {MODEL_ACCESS_KEY}",
            "Content-Type": "application/json"
        },
        json={"prompt": f"Score: {resume}\n\nJob: {job_desc}"}
    )
    
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(port=5000)
```

### Option 3: Batch Processing

For large resume volumes:

```python
# Score multiple resumes in parallel
import concurrent.futures

def score_resumes_batch(resumes, job_description):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(score_resume, resume, job_description)
            for resume in resumes
        ]
        results = [f.result() for f in futures]
    return results
```

## Troubleshooting Production Issues

### High Latency (> 5 seconds per request)

1. Check if model is starting cold
   - First request might be slower (cold start)
   - Subsequent requests should be faster
2. Consider dedicated inference if you have consistent traffic
3. Check network latency to DO region

### High Costs

1. Check token usage: `doctl compute inference metrics`
2. Resumes scoring more tokens than expected?
   - Trim prompt instruction
   - Use shorter model prompts
3. Consider cheaper model (gpt-4-turbo instead of gpt-4o)

### Function Failures

1. Check logs: `doctl serverless logs`
2. Common issues:
   - Timeout: Function takes > 30 seconds
   - Memory: Insufficient resources for model
   - Import error: Missing Python dependency
3. Fix and redeploy: `doctl serverless deploy functions/resume_scorer.py`

### Agent Not Calling Function

1. Verify function route is configured correctly
2. Check agent instructions include function reference
3. Test function directly with: `doctl serverless invoke resume_scorer`

## Rollback Procedure

If production breaks:

```bash
# 1. Check what's deployed
doctl serverless function list

# 2. Check recent logs
doctl serverless logs --tail

# 3. Identify the issue and fix
# (Edit resume_scorer.py)

# 4. Redeploy
./scripts/deploy_function.sh

# 5. Test
curl -X POST "https://api.digitalocean.com/v2/inference/agents/${AGENT_ID}/invoke" \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -d '{"prompt": "..."}'

# 6. If still broken, revert to last working version
git checkout HEAD~1 functions/resume_scorer.py
./scripts/deploy_function.sh
```

## Maintenance Schedule

### Weekly
- Check error logs
- Verify response times
- Monitor costs

### Monthly
- Review metrics and usage patterns
- Update dependencies if needed
- Test disaster recovery procedures

### Quarterly
- Audit function performance
- Consider infrastructure optimizations
- Update documentation

## Security Checklist

- [ ] API keys stored in DO Console (not in code)
- [ ] Environment variables set in .env (not committed)
- [ ] .gitignore prevents secret leaks
- [ ] Endpoint requires authentication (Model Access Key)
- [ ] Logs don't contain sensitive resume data
- [ ] Rate limiting considered for public endpoint
- [ ] API tokens rotated quarterly

## Support & Escalation

### For Issues:
1. Check logs: `doctl serverless logs`
2. Check DO status page: https://status.digitalocean.com
3. Contact DO support: https://cloud.digitalocean.com/support

### For Code Issues:
1. Check SETUP.md for troubleshooting
2. Open GitHub issue with:
   - Steps to reproduce
   - Logs/error messages
   - Environment details

## Next Steps

- [Set up Web UI](../README.md#-next-steps) (optional)
- [Write blog post](../README.md#-blog-post) about your agent
- Monitor and optimize based on real usage
- Share your results!

---

See [SETUP.md](SETUP.md) for local testing and [ARCHITECTURE.md](ARCHITECTURE.md) for technical details.
