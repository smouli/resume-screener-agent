# Architecture Overview

## High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│                      Your Application                   │
│  (Web UI, CLI, or API integration)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ POST /v2/inference/agents/{id}/invoke
                       │ {"prompt": "Score this resume: ..."}
                       ↓
┌──────────────────────────────────────────────────────────┐
│         DigitalOcean Inference (Serverless)              │
│                                                          │
│  Agent: resume-screener                                  │
│  Model: GPT-4o                                           │
│  Status: Spins up on-demand                              │
│                                                          │
│  1. Receives prompt                                      │
│  2. Reads agent instructions                             │
│  3. Checks available tools (function routes)             │
│  4. Decides: "I need to score this resume"               │
│  5. Routes to DO Function                                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Function Route: score_resume
                       │ {"resume_text": "...", "job_desc": "..."}
                       ↓
┌──────────────────────────────────────────────────────────┐
│         DigitalOcean Functions (Serverless)              │
│                                                          │
│  Function: resume_scorer                                 │
│  Status: Spins up on-demand                              │
│                                                          │
│  1. Receives resume + job description                    │
│  2. Parses and tokenizes                                 │
│  3. Runs ML scoring algorithm                            │
│  4. Extracts keywords and analysis                        │
│  5. Returns: {"score": 85, "reasons": [...]}             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Returns result
                       ↓
┌──────────────────────────────────────────────────────────┐
│         DigitalOcean Inference (Agent)                   │
│                                                          │
│  6. Receives function result                             │
│  7. Synthesizes and enriches response                    │
│  8. Formats final answer                                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Returns to application
                       ↓
┌──────────────────────────────────────────────────────────┐
│                      Your Application                    │
│  {"score": 85, "reasoning": "...", "recommendation": "..."}
└──────────────────────────────────────────────────────────┘
```

## Components

### 1. DO Inference (Agent Host)

**What it is:** Serverless AI hosting that runs your agent

**What it does:**
- Hosts the "resume-screener" agent
- Spins up when a request arrives
- Shuts down after response is sent
- Manages the agent's decision-making loop

**Configuration:**
```yaml
Agent: resume-screener
Model: gpt-4o (or gpt-4-turbo)
Region: nyc (or your preferred region)
Endpoint: https://api.digitalocean.com/v2/inference/agents/{agent_id}/invoke
Execution: On-demand serverless (pay per token)
```

**Responsibilities:**
1. Receive prompt from your application
2. Read agent configuration from DO API
3. Invoke model with instructions
4. Check for tool calls (function routes)
5. Orchestrate function routing
6. Synthesize final response

---

### 2. DO Functions (Scoring Logic)

**What it is:** Serverless compute for your custom code

**What it does:**
- Runs the `resume_scorer.py` function
- Executes the actual ML scoring logic
- Returns structured results to the agent

**Configuration:**
```yaml
Function: resume_scorer
Language: Python 3.9+
Region: nyc
Namespace: default
Execution: On-demand serverless (pay per invocation)
Timeout: 30 seconds
```

**Responsibilities:**
1. Parse resume and job description
2. Extract key information
3. Run scoring algorithm
4. Return structured results

---

### 3. Function Routing (The Bridge)

**What it is:** DO's mechanism for connecting agents to functions

**How it works:**
```
Agent → Sees function route definition
      → Decides function needs to be called
      → Sends request to DO Functions
      → Waits for result
      → Receives result
      → Continues processing
```

**In your agent configuration:**
```python
tools = [
    {
        "type": "function_route",
        "name": "score_resume",
        "faas_namespace": "default",
        "input_schema": {
            "type": "object",
            "properties": {
                "resume_text": {"type": "string"},
                "job_description": {"type": "string"}
            },
            "required": ["resume_text", "job_description"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "score": {"type": "number"},
                "reasons": {"type": "array"}
            }
        }
    }
]
```

---

## Request Flow (Detailed)

### Step 1: Your App Sends Request
```bash
POST https://api.digitalocean.com/v2/inference/agents/{agent_id}/invoke
Authorization: Bearer $MODEL_ACCESS_KEY
Content-Type: application/json

{
  "prompt": "Score this resume against the job description:\n\nResume: [full resume text]\n\nJob Description: [job requirements]"
}
```

**Latency Impact:** ~100-500ms first time (cold start), <100ms subsequent

---

### Step 2: Agent Spins Up
DO Inference receives the request and:
1. Looks up agent config from DO API
2. Allocates resources (serverless, auto-scaled)
3. Initializes the model with agent instructions
4. Prepares available tools (function routes)

---

### Step 3: Agent Processes Prompt
The agent (GPT-4o) reads:
```
System Instructions:
"You are a professional resume screener. Score resumes on a scale of 0-100.
You have access to a scoring function that analyzes resumes systematically.
Always use the score_resume function to get accurate results.
Then synthesize the score with additional context and reasoning."

User Prompt:
"Score this resume..."
```

The agent decides:
- ✅ "I need to call the score_resume function to analyze this properly"

---

### Step 4: Agent Routes to Function
Agent makes a function call:
```json
{
  "tool": "score_resume",
  "arguments": {
    "resume_text": "John Doe\nExperience: 5 years Python...",
    "job_description": "We need a Senior Python Engineer with 5+ years..."
  }
}
```

DO Inference orchestrates:
1. Validates arguments against input_schema
2. Calls DO Functions with the arguments
3. Waits for result (async, managed by DO)
4. Returns result to agent

---

### Step 5: Function Executes
DO Functions runs `resume_scorer.py`:

```python
def main(event, context):
    resume_text = event["resume_text"]
    job_description = event["job_description"]
    
    # ML scoring logic
    score = analyze_resume(resume_text, job_description)
    
    return {
        "body": {
            "score": score,
            "strengths": [...],
            "gaps": [...],
            "keywords_found": [...]
        }
    }
```

Function returns:
```json
{
  "score": 85,
  "strengths": ["5+ years Python", "AWS experience"],
  "gaps": ["No Kubernetes"],
  "keywords_found": 12,
  "total_keywords_checked": 15
}
```

---

### Step 6: Agent Receives Result
Agent gets back:
```
Tool Result:
{
  "score": 85,
  "strengths": [...],
  "gaps": [...]
}
```

Agent synthesizes:
"Based on the scoring analysis (85/100), this candidate is a strong match. They have the required experience but are missing some preferred qualifications."

---

### Step 7: Final Response
Agent returns to your app:
```json
{
  "score": 85,
  "match_percentage": "85%",
  "strengths": [...],
  "gaps": [...],
  "reasoning": "Strong match with proven experience...",
  "recommendation": "STRONG MATCH - Recommend for phone screen"
}
```

**Total Latency:** 2-5 seconds (first call), 1-3 seconds (subsequent)

---

## Cost Model

### DO Inference (Agent Hosting)
```
Price: $0.00015 per 1K input tokens + $0.0006 per 1K output tokens
Example: Score 1 resume
  Input tokens: ~500 (prompt + instructions)
  Output tokens: ~200 (response)
  Cost: (500/1000 * $0.00015) + (200/1000 * $0.0006) = ~$0.00015
  
Cost per 100 resumes: ~$0.015
```

### DO Functions (Scoring Logic)
```
Price: $0.0000002 per invocation + $0.50 per GB-hour
Example: Score 1 resume
  Invocation: $0.0000002
  Execution: ~0.5 seconds, minimal compute
  Cost: negligible
  
Cost per 100 resumes: ~$0.00002
```

### Total
```
Cost per resume: ~$0.0002 (essentially free)
Cost per 100 resumes: ~$0.02 (very cheap)
Cost per 10,000 resumes: ~$2 (scales linearly)
```

---

## Why This Architecture?

**Why Serverless?**
- No servers to manage
- Auto-scales with traffic
- Pay only for what you use
- Fast to deploy

**Why Function Routing?**
- Agent handles orchestration
- Separation of concerns (agent logic ≠ scoring logic)
- Easy to test independently
- Can update function without changing agent

**Why DO Inference for Agent?**
- Purpose-built for agentic workloads
- Direct integration with DO Functions
- Simple function routing
- No custom orchestration needed

**Why Not Just a Single Function?**
- Single function = you orchestrate (more code)
- Agent handling = DO orchestrates (less code)
- Agent can refine, retry, synthesize (smarter)

---

## Scaling Considerations

### Current Architecture Limits
- Single agent instance (spins up as needed)
- Sequential function calls
- Single model (GPT-4o)

### If You Scale to 100K+ Resumes
- Multiple agent instances (automatic)
- Batch processing (send resume batches)
- Consider dedicated inference (always-on)
- Add caching for similar resumes

### If You Add Multiple Job Types
- Multiple agents (one per job type)
- Agent routing (parent agent picks specialist)
- Shared function library

---

## Security Model & Credential Handling

### Current Architecture: Client-Provided Credentials

**How it works:**
```bash
curl -X POST https://agents.do-ai.run/.../run \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "...",
    "job_description": "...",
    "model_access_key": "doo_v1_your_gradient_key"  ← Client provides this
  }'
```

**Advantages:**
- ✅ Simple, no backend needed
- ✅ Works for personal/internal use
- ✅ No key storage requirement
- ✅ Fast to develop/test

**Limitations:**
- ❌ Key exposed to client
- ❌ Client must be trusted
- ❌ No usage control/billing per user
- ❌ Not suitable for public APIs

### Production Architecture: Backend-Managed Credentials

For a public/production system, use a secure backend proxy:

```
┌──────────────────┐
│  Untrusted Client │
│  (Web, Mobile)    │
└────────┬─────────┘
         │
         │ POST /api/score-resume
         │ {"resume_text": "...", "job_description": "..."}
         │ (NO key required)
         ↓
┌──────────────────────────────────────┐
│  YOUR Backend API (Node/Python/etc)  │
│                                      │
│  1. Authenticate client (JWT/OAuth)  │
│  2. Check rate limits                │
│  3. Load MODEL_ACCESS_KEY from vault │
│  4. Call deployed agent              │
│  5. Log usage for billing            │
│  6. Return result to client          │
└────────┬─────────────────────────────┘
         │
         │ POST https://agents.do-ai.run/.../run
         │ {"resume_text": "...", "model_access_key": "..."}
         │ (Key is internal only)
         ↓
┌──────────────────────────────────────┐
│   DigitalOcean Gradient ADK Agent    │
│   (Deployed Resume Screener)         │
└──────────────────────────────────────┘
```

**Why this matters:**
- ✅ Key never leaves your infrastructure
- ✅ Per-user rate limiting & billing
- ✅ Audit trail of who scored what
- ✅ Can add business logic (price per resume, etc.)

### Why We Chose Client-Provided (Current)

For a portfolio/demo project:
1. **Simpler:** No backend needed, shows agent works
2. **Honest:** Documents the limitation (not hidden)
3. **Functional:** Fully working end-to-end
4. **Educational:** Shows trade-offs clearly

### Gradient ADK Limitation Discovered

During development, we discovered **Gradient ADK doesn't support secrets management**:
- ❌ Can't pass env vars to deployed agents
- ❌ No UI support for agent secrets
- ❌ No documented secrets API
- ❌ Deployed containers have network isolation that blocks external API calls

**This means:** Gradient ADK isn't suitable for agents that call external APIs with credentials. It's designed for self-contained agents (with built-in tools like file access, bash, etc.)

### Data Flow & Privacy
- Resume text → Agent → Scoring function → Response (no persistence)
- No data stored by default
- No logs contain sensitive resume data
- Key only used during request execution

### Best Practices
- **Local/Demo:** Pass key in request (current approach)
- **Production:** Use backend proxy with secure vault
- **Vault options:** 
  - AWS Secrets Manager
  - DO Managed Vault (if available)
  - HashiCorp Vault
  - Environment variables in Docker secrets
- **Always:** Rotate keys regularly, monitor access logs

---

## Comparison: Agent vs Manual Loop

### With Agent (This Project)
```python
# Your app just calls the agent
response = agent.invoke(resume_text, job_desc)
print(response.score)  # Done!
```

### Manual Loop (Without Agent)
```python
# You orchestrate everything
response = model.create(prompt, tools=[score_resume_tool])
if response.tool_calls:
    for tool_call in response.tool_calls:
        result = call_function(tool_call)
        response = model.create(
            # Resend entire conversation history
            messages=[...previous..., tool_result]
        )
# Multiple API calls, you manage state
```

**Agent advantage:** Simpler code, DO handles orchestration

---

## Architecture Diagram (Visual)

See the interactive diagram: [Architecture Visualization](../README.md#-architecture)

---

## Next Steps

- [SETUP.md](SETUP.md) — How to deploy this locally and test
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deploy to DigitalOcean
- Source code: `functions/resume_scorer.py`, `agent/agent_config.sh`
