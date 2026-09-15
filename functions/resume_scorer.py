"""
Resume Scorer Function

Intelligent resume scoring using keyword extraction and semantic analysis.
Called by the resume-screener agent via function routing.

Scoring algorithm:
1. Extract skills from job description (required vs preferred)
2. Match against resume text
3. Calculate match percentage
4. Identify strengths and gaps
5. Provide recommendation
"""

import re


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
        resume_text = event.get("resume_text", "")
        job_description = event.get("job_description", "")

        if not resume_text or not job_description:
            return {
                "body": {
                    "error": "Missing resume_text or job_description"
                }
            }

        result = score_resume(resume_text, job_description)

        return {
            "body": {
                "score": result["score"],
                "match_percentage": f"{result['score']}%",
                "strengths": result["strengths"],
                "gaps": result["gaps"],
                "keywords_matched": result["keywords_matched"],
                "keywords_total": result["keywords_total"],
                "reasoning": result["reasoning"],
                "recommendation": result["recommendation"]
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

    Scoring logic:
    - Extract required skills (words before "required")
    - Extract preferred skills (words before "preferred")
    - Match against resume
    - Weight required (70%) vs preferred (30%)
    - Return score 0-100

    Args:
        resume_text (str): Resume content
        job_description (str): Job description content

    Returns:
        dict: Scoring results with score, strengths, gaps, recommendation
    """

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    # Extract all skill keywords from job description
    all_keywords = extract_all_skills(job_lower)
    required_keywords = extract_required_skills(job_lower)
    preferred_keywords = extract_preferred_skills(job_lower)

    # If extraction didn't find keywords, use all keywords
    if not required_keywords:
        required_keywords = all_keywords[:10]
    if not preferred_keywords:
        preferred_keywords = all_keywords[10:20]

    # Find matches in resume
    matched_required = [kw for kw in required_keywords if kw in resume_lower]
    matched_preferred = [kw for kw in preferred_keywords if kw in resume_lower]
    matched_all = matched_required + matched_preferred

    # Calculate match percentages
    required_pct = len(matched_required) / max(len(required_keywords), 1)
    preferred_pct = len(matched_preferred) / max(len(preferred_keywords), 1)

    # Weighted score: required skills are more important
    score = int((required_pct * 0.7 + preferred_pct * 0.3) * 100)
    score = min(100, max(0, score))

    # Find gaps (required skills not in resume)
    gaps = [kw for kw in required_keywords if kw not in resume_lower]

    # Determine recommendation
    if score >= 85:
        recommendation = "⭐ EXCELLENT MATCH - Strong hire recommendation"
    elif score >= 70:
        recommendation = "✅ STRONG MATCH - Recommend for phone screen"
    elif score >= 50:
        recommendation = "👍 MODERATE MATCH - Consider for phone screen"
    elif score >= 30:
        recommendation = "⚠️ WEAK MATCH - May not be ideal fit"
    else:
        recommendation = "❌ POOR MATCH - Not recommended"

    # Generate reasoning
    reasoning = f"""Matched {len(matched_required)}/{len(required_keywords)} required skills. Matched {len(matched_preferred)}/{len(preferred_keywords)} preferred skills. Key matches: {', '.join(matched_all[:5]) if matched_all else 'None'}."""

    return {
        "score": score,
        "strengths": matched_required[:5] if matched_required else matched_preferred[:5],
        "gaps": gaps[:5],
        "keywords_matched": len(matched_all),
        "keywords_total": len(required_keywords) + len(preferred_keywords),
        "reasoning": reasoning,
        "recommendation": recommendation
    }


def extract_required_skills(job_description):
    """Extract skills from the 'required' section."""
    skills = []
    required_section = re.search(r'required[:\s]*(.*?)(?=preferred|$)', job_description, re.IGNORECASE | re.DOTALL)
    if required_section:
        text = required_section.group(1)
        skills = extract_technical_keywords(text)
    return skills[:10]


def extract_preferred_skills(job_description):
    """Extract skills from the 'preferred' section."""
    skills = []
    preferred_section = re.search(r'preferred[:\s]*(.*?)(?=responsibilities|$)', job_description, re.IGNORECASE | re.DOTALL)
    if preferred_section:
        text = preferred_section.group(1)
        skills = extract_technical_keywords(text)
    return skills[:10]


def extract_all_skills(job_description):
    """Extract all technical and soft skills from job description."""
    return extract_technical_keywords(job_description) + extract_soft_skills(job_description)


def extract_technical_keywords(text):
    """Extract technical skills and keywords."""

    keywords = [
        "python", "javascript", "java", "c++", "c#", "rust", "go", "kotlin",
        "php", "ruby", "swift", "typescript", "scala", "r", "matlab",
        "react", "vue", "angular", "django", "flask", "fastapi", "spring",
        "express", "node", "rails", "asp.net", "laravel", "gin", "echo",
        "aws", "azure", "gcp", "kubernetes", "docker", "terraform",
        "lambda", "ec2", "s3", "rds", "dynamodb", "cloudfront",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "firestore", "oracle", "sqlite",
        "git", "github", "gitlab", "jenkins", "circleci", "github actions",
        "docker compose", "helm", "ansible", "puppet", "chef",
        "agile", "scrum", "kanban", "ci/cd", "devops", "microservices",
        "rest api", "grpc", "graphql", "tdd", "bdd", "oop", "functional",
    ]

    found = []
    text_lower = text.lower()

    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)

    return list(set(found))


def extract_soft_skills(text):
    """Extract soft skills."""

    soft_skills = [
        "communication", "leadership", "teamwork", "problem solving",
        "problem-solving", "project management", "collaboration",
        "adaptability", "learning", "mentoring", "teaching",
        "critical thinking", "analytical", "attention to detail",
        "organization", "time management", "customer focused",
    ]

    found = []
    text_lower = text.lower()

    for skill in soft_skills:
        if skill in text_lower:
            found.append(skill)

    return list(set(found))


if __name__ == "__main__":
    test_resume = """
    JOHN DOE
    5+ years software engineering with Python and AWS expertise.

    Backend Engineer - Built microservices using Python and FastAPI
    AWS infrastructure management (EC2, RDS, S3)
    Led team of 3 engineers
    CI/CD with GitHub Actions
    REST API development with Django and Flask
    PostgreSQL and Redis databases
    Docker containerization
    """

    test_job = """
    Senior Python Engineer

    REQUIRED:
    - 5+ years Python experience
    - REST API design
    - AWS or cloud experience
    - PostgreSQL or SQL databases

    PREFERRED:
    - Kubernetes and Docker
    - Microservices architecture
    - Leadership experience
    """

    result = main({"resume_text": test_resume, "job_description": test_job}, None)
    import json
    print(json.dumps(result, indent=2))
