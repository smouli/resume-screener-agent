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

### What We Tried

| Approach | Status | Notes |
|----------|--------|-------|
| `export VAR=value` before deploy | ❌ | CLI doesn't capture shell vars |
| Setting in `agent.yml` with `${VAR}` | ❌ | Interpolation syntax not supported/doesn't work |
| Hardcoding in code | ⚠️ | Works but fails GitHub secret scanning |
| Fallback authentication methods | ❌ | Gradient ADK expects specific key format |

### Current Status

- **Local agent** — Fully functional ✅
- **DO Function endpoint** — Fully functional ✅
- **Gradient ADK deployment** — Non-functional ❌

### Recommended Approach

For production use, **run the agent locally** or **call the DO Function endpoint directly**:

```bash
# Local (recommended for testing/demos)
export GRADIENT_MODEL_ACCESS_KEY=$YOUR_KEY
python -c "from main import main; import asyncio; asyncio.run(main(...))"

# OR call the deployed scoring function directly
curl -X POST https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-309f9b5b-dd19-493d-8450-b30f94517e21/default/resume-screener \
  -d '{"resume_text": "...", "job_description": "..."}'
```

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
