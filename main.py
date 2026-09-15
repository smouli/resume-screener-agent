"""
Resume Screener Agent using Gradient ADK + LangGraph

Analyzes resumes against job descriptions using:
- Quantitative scoring via deployed DO Function
- Qualitative analysis via Claude (via Gradient SDK)
- Tool use for intelligent reasoning
"""

import os
import json
import httpx
from typing import Dict, TypedDict, Annotated

from gradient import AsyncGradient
from gradient_adk import entrypoint, RequestContext
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode

SCORING_ENDPOINT = "https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-309f9b5b-dd19-493d-8450-b30f94517e21/default/resume-screener"


class State(TypedDict):
    """Agent state for resume screening."""
    resume_text: str
    job_description: str
    messages: Annotated[list, add_messages]
    score_result: dict
    final_analysis: str


async def score_resume_tool(resume_text: str, job_description: str) -> dict:
    """Call the deployed DO Function to score a resume."""
    payload = {
        "resume_text": resume_text,
        "job_description": job_description
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SCORING_ENDPOINT, json=payload, timeout=10)
            result = response.json().get("body", {})
            if result.get("error"):
                return {"error": result["error"]}
            return result
    except Exception as e:
        return {"error": f"Scoring failed: {str(e)}"}


async def llm_node(state: State) -> State:
    """Use Gradient SDK to analyze the resume match with LLM tool use."""

    inference_client = AsyncGradient(
        model_access_key=os.environ.get("GRADIENT_MODEL_ACCESS_KEY")
    )

    # Define tool for scoring
    tools = [
        {
            "type": "function",
            "function": {
                "name": "score_resume",
                "description": "Score a resume against a job description. Returns score (0-100), strengths, gaps, and detailed analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resume_text": {
                            "type": "string",
                            "description": "Resume text"
                        },
                        "job_description": {
                            "type": "string",
                            "description": "Job description text"
                        }
                    },
                    "required": ["resume_text", "job_description"]
                }
            }
        }
    ]

    # Initial prompt
    system_prompt = """You are an expert resume screener and hiring consultant.

Your process:
1. Use the score_resume tool to get quantitative analysis
2. Interpret the score in hiring context
3. Identify key strengths and gaps
4. Provide a clear hiring recommendation
5. Explain your reasoning

Be professional, fair, and actionable."""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"""Analyze this candidate's resume against the job description.

RESUME:
{state['resume_text']}

JOB DESCRIPTION:
{state['job_description']}

Use the score_resume tool to get quantitative metrics, then provide your professional assessment."""
        }
    ]

    # Agent loop with tool use
    while True:
        response = await inference_client.chat.completions.create(
            model="openai-gpt-oss-120b",
            messages=messages,
            tools=tools,
            temperature=0.7,
            max_tokens=1024
        )

        # Check if tool was called
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]

            if tool_call.function.name == "score_resume":
                args = json.loads(tool_call.function.arguments)
                tool_result = await score_resume_tool(
                    args.get("resume_text", ""),
                    args.get("job_description", "")
                )
                state["score_result"] = tool_result

                # Add assistant message and tool result
                messages.append({
                    "role": "assistant",
                    "content": response.choices[0].message.content or "",
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "score_resume",
                    "content": json.dumps(tool_result)
                })
            else:
                break
        else:
            # Agent done - extract analysis
            state["final_analysis"] = response.choices[0].message.content or ""
            break

    return state


@entrypoint
async def main(input: Dict, context: RequestContext):
    """Main agent entrypoint for resume screening."""

    resume_text = input.get("resume_text", "")
    job_description = input.get("job_description", "")

    if not resume_text or not job_description:
        return {
            "error": "Missing resume_text or job_description",
            "status": "failed"
        }

    # Initialize state
    initial_state = State(
        resume_text=resume_text,
        job_description=job_description,
        messages=[],
        score_result={},
        final_analysis=""
    )

    # Run the agent
    state = await llm_node(initial_state)

    # Return combined result
    return {
        "status": "success",
        "score": state["score_result"].get("score", 0),
        "match_percentage": state["score_result"].get("match_percentage", "0%"),
        "strengths": state["score_result"].get("strengths", []),
        "gaps": state["score_result"].get("gaps", []),
        "recommendation": state["score_result"].get("recommendation", ""),
        "reasoning": state["score_result"].get("reasoning", ""),
        "agent_analysis": state["final_analysis"],
        "keywords_matched": state["score_result"].get("keywords_matched", 0),
        "keywords_total": state["score_result"].get("keywords_total", 0)
    }
