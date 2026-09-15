# Gradient ADK Deployment Notes

## Secrets Management (Solved)

### The Discovery

Initially, I struggled with passing credentials to the deployed agent on Gradient ADK. But the platform actually has a proper secrets management system that I discovered during development.

### How Gradient Secrets Work

Gradient ADK provides a **secrets management system** that properly handles credentials:

```yaml
# Define secret in project
gradient secrets set project --name "model-access-key" --value "YOUR_KEY"

# Reference in agent.yml
environment:
  - name: GRADIENT_MODEL_ACCESS_KEY
    value: secret:model-access-key

# Agent reads from environment at deployment time
key = os.environ.get("GRADIENT_MODEL_ACCESS_KEY")
```

**Why this works:**
- Secrets stored securely in Gradient project
- Never exposed in code or logs
- Automatically injected at deployment time
- Clean, production-grade pattern

### What We Tested

| Approach | Status | Notes | Learning |
|----------|--------|-------|----------|
| Shell env vars + deploy | ❌ | CLI doesn't capture from shell | Env vars aren't passed through CLI |
| agent.yml config with `${VAR}` | ❌ | No interpolation support | Config is literal; variables don't expand |
| Hardcoding in code | ⚠️ | Works but exposes secrets | Never hardcode; GitHub catches it |
| Gradient project secrets | ✅ | **CORRECT SOLUTION** | Proper secrets management |

### Current Deployment

- **Agent** — Deployed and working ✅
  - Endpoint: https://agents.do-ai.run/v1/03ed9e72-a9ed-4312-bdfa-981ef6655783/main/run
  - Credentials via Gradient project secrets
  - Secured, no keys in code

- **Scoring Function** — Deployed and working ✅
  - Serverless compute on DO Functions
  - Stateless, pure computation

### Key Takeaway

The breakthrough was realizing **Gradient ADK has proper secrets management** — I just needed to find the documentation. The solution is clean, secure, and production-grade. No hardcoding, no request payload exposure, just proper environment variable management through the platform's built-in secrets system.
