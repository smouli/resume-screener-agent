#!/usr/bin/env python3
"""
Resume Screener Agent

An intelligent agent that uses Claude Opus 5 with tool use to analyze resumes.
The agent calls the deployed DO Function endpoint for quantitative scoring,
then provides qualitative analysis and recommendations.

Usage:
    python agent.py

Or use as a module:
    from agent import run_agent
    result = run_agent(resume_text, job_description)
"""

import os
import json
import httpx
from pathlib import Path
from anthropic import Anthropic

FUNCTION_ENDPOINT = "https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-309f9b5b-dd19-493d-8450-b30f94517e21/default/resume-screener"

tools = [
    {
        "name": "score_resume",
        "description": "Score a resume against a job description. Returns a detailed score (0-100) with strengths, gaps, and recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "resume_text": {
                    "type": "string",
                    "description": "The full text of the resume to score"
                },
                "job_description": {
                    "type": "string",
                    "description": "The full job description to match against"
                }
            },
            "required": ["resume_text", "job_description"]
        }
    }
]


def score_resume_tool(resume_text: str, job_description: str) -> dict:
    """Call the deployed DO Function to score a resume."""
    payload = {
        "resume_text": resume_text,
        "job_description": job_description
    }

    try:
        response = httpx.post(FUNCTION_ENDPOINT, json=payload, timeout=10)
        result = response.json().get("body", {})
        if result.get("error"):
            return {"error": result["error"]}
        return result
    except Exception as e:
        return {"error": f"Function call failed: {str(e)}"}


def run_agent(resume_text: str, job_description: str) -> dict:
    """Run the agent loop to analyze a resume."""
    client = Anthropic()

    messages = [
        {
            "role": "user",
            "content": f"""Analyze this candidate's resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Use the score_resume tool to get quantitative metrics, then provide qualitative analysis."""
        }
    ]

    system_prompt = """You are an expert resume screener and hiring consultant.

Your process:
1. Use the score_resume tool to get quantitative analysis
2. Interpret the score in context
3. Identify key strengths and gaps
4. Provide a clear hiring recommendation
5. Explain your reasoning

Be professional, fair, and actionable."""

    analysis_text = ""
    score_data = {}

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

            # Execute the tool
            if tool_use.name == "score_resume":
                tool_result = score_resume_tool(
                    tool_use.input.get("resume_text", ""),
                    tool_use.input.get("job_description", "")
                )
                score_data = tool_result
            else:
                tool_result = {"error": f"Unknown tool: {tool_use.name}"}

            # Continue conversation with tool result
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": json.dumps(tool_result)
                    }
                ]
            })
        else:
            # Agent done - extract analysis
            for block in response.content:
                if hasattr(block, "text"):
                    analysis_text = block.text
                    break
            break

    return {
        "score": score_data.get("score", 0),
        "match_percentage": score_data.get("match_percentage", "0%"),
        "strengths": score_data.get("strengths", []),
        "gaps": score_data.get("gaps", []),
        "recommendation": score_data.get("recommendation", ""),
        "reasoning": score_data.get("reasoning", ""),
        "agent_analysis": analysis_text,
        "keywords_matched": score_data.get("keywords_matched", 0),
        "keywords_total": score_data.get("keywords_total", 0)
    }


if __name__ == "__main__":
    print("🤖 Resume Screener Agent\n")
    print("=" * 70)

    # Load test data if available
    resume_path = Path("tests/sample_resume.txt")
    job_path = Path("tests/sample_job_desc.txt")

    if resume_path.exists() and job_path.exists():
        print("📄 Loading test data...\n")
        resume_text = resume_path.read_text()
        job_description = job_path.read_text()
    else:
        resume_text = """
        Senior Python Engineer, 6+ years experience
        Skills: Python, FastAPI, Django, AWS, PostgreSQL, Docker, Kubernetes
        Experience: Built microservices, managed AWS infrastructure, led teams
        """

        job_description = """
        Senior Python Engineer - Required: 5+ years Python, AWS, REST APIs, PostgreSQL.
        Preferred: Docker, Kubernetes, FastAPI, Leadership.
        """

    print(f"📋 Analyzing resume against job description...\n")
    result = run_agent(resume_text, job_description)

    print(f"📊 SCORE: {result['score']}/100 ({result['match_percentage']})")
    print(f"📈 Keywords: {result['keywords_matched']}/{result['keywords_total']}")
    print(f"\n✅ Strengths: {', '.join(result['strengths'])}")
    print(f"⚠️  Gaps: {', '.join(result['gaps']) if result['gaps'] else 'None identified'}")
    print(f"\n💡 {result['recommendation']}")
    print(f"\n🤖 AGENT ANALYSIS:\n{result['agent_analysis']}")
    print("\n" + "=" * 70)
