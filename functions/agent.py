"""
Resume Screener Agent Function

Runs on DO Functions. Uses Claude API with tool use to intelligently
analyze resumes against job descriptions, then calls the scorer function
for quantitative metrics.
"""

import json
import os
import httpx
from anthropic import Anthropic

SCORING_ENDPOINT = "https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-309f9b5b-dd19-493d-8450-b30f94517e21/default/resume-screener"


def main(event, context):
    """Agent function handler."""
    try:
        resume_text = event.get("resume_text", "")
        job_description = event.get("job_description", "")

        if not resume_text or not job_description:
            return {
                "statusCode": 400,
                "body": {
                    "error": "Missing resume_text or job_description"
                }
            }

        # Run the agent
        result = run_screening_agent(resume_text, job_description)

        return {
            "statusCode": 200,
            "body": result
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {
                "error": f"Agent failed: {str(e)}"
            }
        }


def run_screening_agent(resume_text: str, job_description: str) -> dict:
    """Run Claude agent with tool use to analyze resume match."""

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    tools = [
        {
            "name": "score_resume",
            "description": "Get quantitative score for resume match. Returns score 0-100, strengths, gaps, and detailed analysis.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "resume_text": {
                        "type": "string",
                        "description": "Resume text to score"
                    },
                    "job_description": {
                        "type": "string",
                        "description": "Job description to match against"
                    }
                },
                "required": ["resume_text", "job_description"]
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": f"""Analyze this candidate's resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

First, use the score_resume tool to get quantitative metrics. Then provide your professional assessment."""
        }
    ]

    system_prompt = """You are an expert resume screener and hiring consultant.

Your job:
1. Use the score_resume tool to get detailed quantitative analysis
2. Analyze the candidate's fit across multiple dimensions
3. Identify key strengths and gaps
4. Provide a clear recommendation
5. Explain your reasoning concisely

Be professional and fair in your assessment."""

    # Agent loop
    while True:
        response = client.messages.create(
            model="claude-opus-5",
            max_tokens=1024,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            # Find tool use block
            tool_use = None
            for block in response.content:
                if block.type == "tool_use":
                    tool_use = block
                    break

            if not tool_use:
                break

            # Call scoring function
            if tool_use.name == "score_resume":
                score_result = call_scoring_function(
                    tool_use.input.get("resume_text", ""),
                    tool_use.input.get("job_description", "")
                )
            else:
                score_result = {"error": f"Unknown tool: {tool_use.name}"}

            # Continue conversation with tool result
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(score_result)
                    }
                ]
            })
        else:
            # Agent done - extract response
            analysis = ""
            for block in response.content:
                if hasattr(block, "text"):
                    analysis = block.text
                    break

            # Get score from the function call we made
            score_result = call_scoring_function(resume_text, job_description)

            return {
                "score": score_result.get("score", 0),
                "match_percentage": score_result.get("match_percentage", "0%"),
                "strengths": score_result.get("strengths", []),
                "gaps": score_result.get("gaps", []),
                "recommendation": score_result.get("recommendation", ""),
                "reasoning": score_result.get("reasoning", ""),
                "agent_analysis": analysis,
                "keywords_matched": score_result.get("keywords_matched", 0),
                "keywords_total": score_result.get("keywords_total", 0)
            }

    return {"error": "Agent failed to complete"}


def call_scoring_function(resume_text: str, job_description: str) -> dict:
    """Call the deployed scoring function."""
    payload = {
        "resume_text": resume_text,
        "job_description": job_description
    }

    try:
        response = httpx.post(SCORING_ENDPOINT, json=payload, timeout=10)
        return response.json().get("body", {})
    except Exception as e:
        return {"error": f"Scoring failed: {str(e)}"}
