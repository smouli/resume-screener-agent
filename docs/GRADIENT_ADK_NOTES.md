# Gradient ADK Deployment Notes

## Environment Variable Limitation

### The Problem

When deploying the agent to DigitalOcean's Gradient ADK platform, environment variables required for authentication **are not passed to the deployed container**, even though they work perfectly when running locally.

### Why It Happens

```
Local Execution:
shell env vars → gradient agent run → Code can access via os.environ.get()
✅ Works

Deployment Execution:
shell env vars → gradient agent deploy → [No capture mechanism] → Deployed container
❌ Fails
```

The `gradient agent deploy` CLI does not have a mechanism to:
1. Capture env vars from the current shell
2. Inject them into the deployed container at runtime
3. Define them in the `agent.yml` configuration file in a way that works reliably

### What We Tried (Comprehensive Testing Log)

| Approach | Status | Notes | Discovery |
|----------|--------|-------|-----------|
| `export VAR=value` before deploy | ❌ | CLI doesn't capture shell vars | Env vars from shell don't reach container |
| Setting in `agent.yml` with `${VAR}` | ❌ | Interpolation syntax not supported | agent.yml doesn't support variable interpolation |
| Hardcoding in code | ⚠️ | Works but fails GitHub secret scanning | Security issue; not a real solution |
| Fallback authentication methods | ❌ | Gradient ADK expects specific key format | Tried DIGITALOCEAN_API_TOKEN as fallback; doesn't work |
| UI "endpoint access keys" setting | ❌ | Only generates tokens for calling agent, not for agent's internal use | UI mechanism isn't designed for agent → API authentication |
| Pass key in request payload | ✅ | **WORKS LOCALLY** | Agent can accept credentials via request JSON |
| Deployed with request payload | ❌ | 403 Auth error, then network restriction | Network isolation prevents deployed agent from reaching external APIs |

### Root Cause Analysis

After systematic testing, we discovered **two separate issues**:

1. **Environment variable passing** — Gradient ADK deploy doesn't support passing env vars to containers
2. **Network isolation** — Deployed Gradient ADK containers have network restrictions that block external API calls

This suggests **Gradient ADK is designed for self-contained agents** (with built-in tools like file access, bash) rather than agents that call external APIs.

### Current Status

- **Local agent** — Fully functional ✅ (with key in request)
- **DO Function endpoint** — Fully functional ✅
- **Gradient ADK deployment** — Non-functional ❌ (network isolation)

### Solution: Pass Credentials in Request Payload

**What works:** The agent accepts `model_access_key` in the request JSON:

```bash
gradient agent run
```

Then call it with:
```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python engineer, 5 years AWS",
    "job_description": "Senior Python - Required: Python, AWS",
    "model_access_key": "doo_v1_your_key_here"
  }'
```

**Why this matters:**
- Eliminates dependency on environment variables
- Allows dynamic credential passing at runtime
- Works locally ✅
- More secure than hardcoding
- Not restricted by Gradient ADK's deployment limitations

**Why it doesn't solve Gradient ADK deployment:**
- The deployed agent still can't reach external APIs (network isolation)
- But the approach is architecturally sound for any platform with unrestricted network access

### Recommended Approach for Production

For production deployment of an agent that calls external APIs:

1. **Use platforms with unrestricted network access:**
   - AWS Lambda / API Gateway
   - Railway.app
   - Render
   - Fly.io
   - Traditional VPS (EC2, Linode, etc.)

2. **Use DigitalOcean App Platform (not Gradient ADK):**
   - Standard container deployment
   - Full env var support
   - Unrestricted outbound network

3. **For local development/demos:**
   - Run `gradient agent run` 
   - Pass credentials in request payload
   - Works perfectly ✅

### For Future Reference

If you want to deploy the agent to Gradient ADK in the future:

1. **Check Gradient's docs** for any new env var mechanisms
2. **Contact Gradient support** — They may have undocumented features
3. **Consider alternative platforms** — AWS Lambda, Render, Railway (all handle env vars properly)
4. **Use DO Apps** — DigitalOcean's standard app platform may have better env var support

### Architecture Notes

The agent's architecture is sound. The limitation is purely **platform-specific** and **not a code issue**:

- Agent logic ✅ (tested locally)
- Scoring function ✅ (deployed and working)
- Tool use and reasoning ✅ (verified with test cases)
- Environment configuration ❌ (Gradient ADK limitation)

The scoring function alone is production-grade and can handle real use cases. The agent adds intelligent reasoning on top via local execution.
