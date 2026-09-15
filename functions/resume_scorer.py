"""
Resume Scorer Function

This function runs on DigitalOcean Functions and provides intelligent resume scoring.
It's called by the resume-screener agent via function routing.

Usage (via agent):
  The agent will call this function with:
  {
    "resume_text": "full resume text",
    "job_description": "full job description"
  }

  Returns:
  {
    "score": 85,
    "strengths": ["Skill 1", "Skill 2"],
    "gaps": ["Missing Skill 1"],
    "keywords_found": 12,
    "total_keywords": 15,
    "reasoning": "explanation of score"
  }
"""


def main(event, context):
    """
    Main function handler for DigitalOcean Functions.

    Args:
        event: Function invocation event containing:
            - resume_text (str): Full resume text
            - job_description (str): Full job description
        context: DO Functions runtime context

    Returns:
        dict: HTTP response with body containing score and analysis
    """

    try:
        # Extract input
        resume_text = event.get("resume_text", "")
        job_description = event.get("job_description", "")

        # Validate input
        if not resume_text or not job_description:
            return {
                "body": {
                    "error": "Missing resume_text or job_description"
                }
            }

        # TODO: Implement scoring algorithm
        # For now, return a placeholder response
        score = score_resume(resume_text, job_description)

        return {
            "body": {
                "score": score["score"],
                "match_percentage": f"{score['score']}%",
                "strengths": score["strengths"],
                "gaps": score["gaps"],
                "keywords_found": score["keywords_found"],
                "total_keywords": score["total_keywords"],
                "reasoning": score["reasoning"],
                "recommendation": score["recommendation"]
            }
        }

    except Exception as e:
        return {
            "body": {
                "error": f"Scoring failed: {str(e)}"
            },
            "statusCode": 500
        }


def score_resume(resume_text, job_description):
    """
    Score a resume against a job description.

    This is a placeholder implementation. Replace with your actual scoring logic:
    - ML model for semantic similarity
    - Keyword matching
    - Experience evaluation
    - Skill gap analysis

    Args:
        resume_text (str): Resume content
        job_description (str): Job description content

    Returns:
        dict: Scoring results
    """

    # TODO: Implement real scoring algorithm
    # For now, return placeholder based on keyword matching

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    # Simple keyword extraction (replace with ML model)
    required_keywords = extract_keywords(job_lower, is_required=True)
    preferred_keywords = extract_keywords(job_lower, is_required=False)

    # Find matches
    matched_required = [kw for kw in required_keywords if kw in resume_lower]
    matched_preferred = [kw for kw in preferred_keywords if kw in resume_lower]

    # Calculate score (0-100)
    required_match = len(matched_required) / max(len(required_keywords), 1)
    preferred_match = len(matched_preferred) / max(len(preferred_keywords), 1)

    score = int((required_match * 70 + preferred_match * 30) * 100)
    score = min(100, max(0, score))

    # Determine recommendation
    if score >= 80:
        recommendation = "STRONG MATCH - Recommend for phone screen"
    elif score >= 60:
        recommendation = "MODERATE MATCH - Consider for phone screen"
    elif score >= 40:
        recommendation = "WEAK MATCH - May not be ideal fit"
    else:
        recommendation = "POOR MATCH - Not recommended"

    return {
        "score": score,
        "strengths": matched_required[:5],
        "gaps": [kw for kw in required_keywords if kw not in resume_lower][:3],
        "keywords_found": len(matched_required) + len(matched_preferred),
        "total_keywords": len(required_keywords) + len(preferred_keywords),
        "reasoning": f"Found {len(matched_required)}/{len(required_keywords)} required skills and {len(matched_preferred)}/{len(preferred_keywords)} preferred skills.",
        "recommendation": recommendation
    }


def extract_keywords(text, is_required=True):
    """
    Extract keywords from job description.

    TODO: Replace with actual keyword extraction:
    - NLP model (spaCy, transformers)
    - Professional skill databases
    - Education/certification requirements

    Args:
        text (str): Text to extract from
        is_required (bool): Whether to extract required or preferred keywords

    Returns:
        list: Extracted keywords
    """

    # Simple keyword list (replace with real NLP model)
    tech_keywords = [
        "python", "javascript", "java", "c++", "rust", "go", "kotlin",
        "react", "vue", "angular", "fastapi", "django", "flask",
        "aws", "gcp", "azure", "kubernetes", "docker", "postgresql",
        "sql", "nosql", "redis", "elasticsearch", "git", "cicd"
    ]

    soft_keywords = [
        "communication", "leadership", "teamwork", "problem-solving",
        "project management", "collaboration", "adaptability"
    ]

    found = []
    for keyword in (tech_keywords + soft_keywords):
        if keyword in text:
            found.append(keyword)

    return found[:10]  # Return top 10


if __name__ == "__main__":
    # Test locally
    test_resume = """
    John Doe
    5+ years Python experience
    AWS expertise
    Team lead
    """

    test_job = """
    Senior Python Engineer
    Required: 5+ years Python, AWS experience
    Preferred: Kubernetes, leadership
    """

    result = main({
        "resume_text": test_resume,
        "job_description": test_job
    }, None)

    import json
    print(json.dumps(result, indent=2))
